from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.services.ingestion import ingest_book, memory_card, graph

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
