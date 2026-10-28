from uuid import UUID, uuid4

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
from aibackend.services.memory_card import (
    export_memory_card_images,
    generate_memory_card_images,
    prompt_memory_card,
    send_all_image,
)

router = APIRouter()


@router.post("/memory-card")
async def generate_memory_card(
    book_id: UUID,
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
) -> MemoryCardResponse:
    try:
        return await prompt_memory_card(book_id, style, domain, db)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post("/memory-card-batch")
async def generate_memory_card_batch(
    book_id: list[UUID],
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
) -> list[MemoryCardResponse]:
    responses = []
    for current_book_id in book_id:
        try:
            response = await prompt_memory_card(current_book_id, style, domain, db)
            responses.append(response)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(f"Failed to generate memory cards for book {current_book_id}"),
            ) from exc

    return responses


@router.post("/memory-card/import", status_code=201)
async def import_memory_card(
    file: UploadFile = File(...),
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
) -> MemoryCardImportResponse:
    if file.filename is None or not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="A JSON file is required")
    try:
        raw = await file.read(10 * 1024 * 1024 + 1)
        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413, detail="JSON file exceeds the 10 MB limit"
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

    repo = MemoryCardRepository(db)
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


@router.post("/memory-card/queue/images")
async def queue_images(db: AsyncSession = Depends(get_db)) -> dict:
    return await send_all_image(db)


@router.post("/memory-card/deck/{deck_id}/images")
async def generate_images(deck_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    return await generate_memory_card_images(deck_id, db)


@router.post("/memory-card/deck/{deck_id}/export")
async def export_deck(deck_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    return await export_memory_card_images(deck_id, db)


@router.delete("/memory-card/deck/{deck_id}/images")
async def clear_memory_card_images(
    deck_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict[str, int | str]:
    repo = MemoryCardRepository(db)
    try:
        deleted_count = await repo.clear_images(deck_id)
        return {"deck_id": str(deck_id), "deleted_images": deleted_count}
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
    repo = MemoryCardRepository(db)
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
