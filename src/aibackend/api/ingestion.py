from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.models.chunking import Book
from aibackend.services.chunking import create_book_from_upload, ingest_book
from aibackend.services.embedding import embed
from aibackend.services.raptor_chunking import (
    raptor_clustering,
    raptor_summarize,
    raptor_embedding,
    raptor_memory_cards,
    export_raptor_images,
)
from aibackend.models.memory_cards import CardStyle, PromptDomain

router = APIRouter()


@router.post("/books")
async def upload_book(
    file: UploadFile = File(...),
    title: str | None = None,
    description: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Book:
    return await create_book_from_upload(
        file=file, db=db, title=title, description=description
    )


@router.post("/ingest-book")
async def upload_pdf(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ingest_book(book_id, db)


@router.post("/embed")
async def embed_book(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await embed(book_id, db)


@router.post("/raptor")
async def raptor_pipeline(
    book_id: UUID,
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
):
    await ingest_book(book_id, db)
    await embed(book_id, db)
    await raptor_clustering(book_id, db)
    await raptor_summarize(book_id, db)
    await raptor_embedding(book_id, db)
    return await raptor_memory_cards(book_id, style, domain, db)


@router.post("/raptor_clustering")
async def cluster_raptor(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await raptor_clustering(book_id, db)


@router.post("/raptor_summarize")
async def raptor_summarize_(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await raptor_summarize(book_id, db)


@router.post("/raptor_embedding")
async def raptor_embedding_(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await raptor_embedding(book_id, db)


@router.post("/raptor_memory_cards")
async def raptor_memory_cards_(
    book_id: UUID,
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
    db: AsyncSession = Depends(get_db),
):
    return await raptor_memory_cards(book_id, style, domain, db)


@router.post("/raptor/export")
async def export_raptor(book_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    return await export_raptor_images(book_id, db)
