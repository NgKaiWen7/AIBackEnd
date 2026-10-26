from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.models.memory_cards import CardStyle, MemoryCardResponse, PromptDomain
from aibackend.repositories.memord_card import MemoryCardRepository
from aibackend.services.memory_card import memory_card

router = APIRouter()


@router.post("/memory-card")
async def generate_memory_card(
    book_id: UUID,
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
) -> MemoryCardResponse:
    try:
        return await memory_card(book_id, style, domain, db)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.delete("/memory-card/source/{source_id}/images")
async def clear_memory_card_images(
    source_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict[str, int | str]:
    repo = MemoryCardRepository(db)
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
