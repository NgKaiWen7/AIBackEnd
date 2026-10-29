from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.models.chunking import Book
from aibackend.services.book_chat import chat
from aibackend.services.chunking import create_book_from_upload, ingest_book
from aibackend.services.embedding import embed, query_func

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
async def upload_pdf(book_id: UUID, large: bool, db: AsyncSession = Depends(get_db)):
    return await ingest_book(book_id, large, db)


@router.post("/embed")
async def embed_book(book_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await embed(book_id, db)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post("/query")
async def query_book(
    query: str, book_id: UUID | None = None, db: AsyncSession = Depends(get_db)
):
    try:
        return await query_func(query, book_id, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post("/book_chat")
async def book_chat(
    question: str,
    book_id: str | None = None,
    chapter_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await chat(question, db, book_id, chapter_id)
    return result
