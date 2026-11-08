from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.models.chunking import Book
from aibackend.services.chunking import create_book_from_upload, ingest_book
from aibackend.services.embedding import embed
from aibackend.services.raptor_chunking import raptor_embed, raptor_summarize

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


@router.post("/raptor_embed")
async def embed_raptor(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await raptor_embed(book_id, db)

@router.post("/raptor_summarize")
async def raptor_summarize_(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await raptor_summarize(book_id, db)
