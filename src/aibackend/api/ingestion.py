from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.services.book_chat import chat
from aibackend.services.chunking import ingest_book
from aibackend.services.embedding import embed, query
from aibackend.services.graph import graph
from aibackend.services.memory_card import memory_card

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
)


@router.post("/ingest-book")
async def upload_pdf(book_id: str, db: AsyncSession = Depends(get_db)):
    book = await ingest_book(book_id, db)
    return book


@router.post("/memory-card")
async def generate_memory_card(book_id: str, db: AsyncSession = Depends(get_db)):
    result = await memory_card(book_id, db)
    return result


@router.post("/graph")
async def generate_graph(book_id: str, db: AsyncSession = Depends(get_db)):
    result = await graph(book_id, db)
    return result


@router.post("/embed")
async def embed_book(book_id: str, db: AsyncSession = Depends(get_db)):
    result = await embed(book_id, db)
    return result


@router.post("/query")
async def query_book(question: str, db: AsyncSession = Depends(get_db)):
    result = await query(question, db)
    return result


@router.post("/book_chat")
async def book_chat(
    question: str,
    book_id: str | None = None,
    chapter_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await chat(question, db, book_id, chapter_id)
    return result
