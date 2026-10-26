from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.services.book_chat import chat
from aibackend.services.chunking import ingest_book
from aibackend.services.embedding import embed, query_func
from aibackend.services.memory_card import memory_card

router = APIRouter()


@router.post("/ingest-book")
async def upload_pdf(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ingest_book(book_id, db)


@router.post("/memory-card")
async def generate_memory_card(book_id: UUID, db: AsyncSession = Depends(get_db)):
    return await memory_card(book_id, db)


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
async def query_book(query: str, book_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
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
