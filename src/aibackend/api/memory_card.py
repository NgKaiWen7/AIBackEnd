from pathlib import Path
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.models.memory_cards import (
    CardDeck,
    CardStyle,
    MemoryCardImport,
    MemoryCardImportResponse,
    MemoryCardResponse,
    PromptDomain,
    build_system_prompt,
)
from aibackend.repositories.memord_card import MemoryCardRepository
from aibackend.services.memory_card import memory_card

router = APIRouter()

COMPUTE_SERVER_URL = "http://192.168.0.115:8000"
CARD_DECKS_DIR = Path("/mnt/data/card_decks").resolve()


@router.post("/memory-card")
async def generate_memory_card(
    book_id: UUID,
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
) -> MemoryCardResponse:
    try:
        return await memory_card(CARD_DECKS_DIR, book_id, style, domain, db)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/memory-card/import",
    status_code=201,
    response_model=MemoryCardImportResponse,
)
async def import_memory_card(
    file: UploadFile = File(...),
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
) -> MemoryCardImportResponse:
    if file.filename is None or not file.filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="A JSON file is required",
        )

    try:
        raw = await file.read(10 * 1024 * 1024 + 1)

        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="JSON file exceeds the 10 MB limit",
            )

        payload = MemoryCardImport.model_validate_json(raw)

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_input=False),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file",
        ) from exc
    finally:
        await file.close()

    repo = MemoryCardRepository(db, CARD_DECKS_DIR)
    system_prompt = build_system_prompt(style, domain)

    deck = CardDeck(
        source_id=uuid4(),
        system_prompt=system_prompt,
        title=payload.topic,
        concepts=payload.concepts,
    )
    await repo.create_deck(deck)
    await repo.commit()
    return MemoryCardImportResponse(
        deck_id=deck.id,
        source_id=deck.source_id,
        topic=payload.topic,
        cards_imported=len(payload.concepts),
    )


@router.post("/memory-card/source/{source_id}/images")
async def generate_memory_card_images(
    source_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict:
    repo = MemoryCardRepository(db, CARD_DECKS_DIR)
    card_deck = await repo.get_cards(source_id)

    if not card_deck:
        raise HTTPException(
            status_code=404,
            detail="No memory cards found for this source",
        )

    concepts = []

    for card in card_deck.concepts:
        prompt = f"""
        {card_deck.system_prompt}
        CARD TITLE
        {card.title}

        LEARNING CONTENT
        {card.content}

        VISUAL INSTRUCTIONS
        {card.image_prompt}

        OUTPUT REQUIREMENTS
        Generate exactly one finished learning-card image.
        Preserve technical accuracy, terminology, formulas, and code.
        Do not add unrelated concepts or explanatory text outside the image.
        """.strip()
        concepts.append({"id": str(card.id), "prompt": prompt})
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{COMPUTE_SERVER_URL}/generate",
                json={"concepts": concepts},
            )
            response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Timed out waiting for the computing server",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The computing server rejected the generation request",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the computing server",
        ) from exc

    return response.json()


@router.delete("/memory-card/source/{source_id}/images")
async def clear_memory_card_images(
    source_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict[str, int | str]:
    repo = MemoryCardRepository(db, CARD_DECKS_DIR)
    try:
        deleted_count = await repo.clear_images(source_id)
        return {
            "source_id": str(source_id),
            "deleted_images": deleted_count,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to clear memory-card images",
        ) from exc


@router.put("/memory-card/cards/{card_id}/image")
async def update_memory_card_image(
    card_id: UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    repo = MemoryCardRepository(db, CARD_DECKS_DIR)
    try:
        image_path = await repo.update_card_image(card_id, file)

        return {
            "card_id": str(card_id),
            "image_path": image_path,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to update memory-card image",
        ) from exc


@router.delete("/memory-card/cleanup-orphaned-decks")
async def cleanup_orphaned_decks(
    db: AsyncSession = Depends(get_db),
) -> dict[str, int | list[str]]:
    repo = MemoryCardRepository(db, CARD_DECKS_DIR)

    try:
        existing_ids = await repo.get_existing_deck_ids()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve deck IDs",
        ) from exc

    if not CARD_DECKS_DIR.is_dir():
        return {"deleted_count": 0, "deleted": []}

    deleted: list[str] = []

    for path in CARD_DECKS_DIR.iterdir():
        if not path.is_dir() or path.is_symlink():
            continue

        try:
            folder_id = UUID(path.name)
        except ValueError:
            continue

        if folder_id in existing_ids:
            continue

        # Resolve and verify the target before deleting.
        target = path.resolve()

        if target.parent != CARD_DECKS_DIR:
            continue

        try:
            shutil.rmtree(target)
            deleted.append(str(folder_id))
        except OSError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete orphaned deck directory: {folder_id}",
            ) from exc

    return {
        "deleted_count": len(deleted),
        "deleted": deleted,
    }
