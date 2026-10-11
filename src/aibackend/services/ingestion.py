import logging
from pathlib import Path

import json_repair
import ollama
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.models.graph import ExtractionResult
from aibackend.models.knowledge import MemoryCards as MemoryCardSchema
from aibackend.prompts.graph_ingestion import PROMPT as GRAPH_PROMPT
from aibackend.prompts.memory_card import PROMPT as MEMORY_CARD_PROMPT
from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import BookChunks as BookChunks_db
from aibackend.repositories.knowledge import MemoryCard as MemoryCardDB
from aibackend.utils.chunk import chunk_text
from aibackend.utils.pdf import get_chapters

logger = logging.getLogger(__name__)


async def ingest_book(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(selectinload(Book_db.chapters).selectinload(BookChapter_db.chunks))
        .where(Book_db.id == book_id)
    )
    result = await db.execute(stmt)
    book: Book_db = result.scalar_one()
    book.chapters.clear()
    await db.flush()
    pdf_path = Path("/mnt") / book.source.lstrip("/")
    chapters: dict[str, str] = get_chapters(pdf_path)

    for chapter_number, (chapter_title, content) in enumerate(
        chapters.items(), start=1
    ):
        bookchapter_db = BookChapter_db(
            chapter_number=chapter_number, title=chapter_title
        )
        chunks = chunk_text(content, chunk_size=1000, overlap=200)
        for i, chunk in enumerate(chunks):
            bookchunk_db = BookChunks_db(raw_text=chunk, position=i)
            bookchapter_db.chunks.append(bookchunk_db)
        book.chapters.append(bookchapter_db)

    await db.commit()
    await db.refresh(book)

    return {
        "book_id": book.id,
    }


async def memory_card(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(
            selectinload(Book_db.chapters)
            .selectinload(BookChapter_db.chunks)
            .selectinload(BookChunks_db.memory_cards)
        )
        .where(Book_db.id == book_id)
    )
    book = await db.scalar(stmt)
    if book is None:
        raise ValueError(f"Book {book_id} not found")
    for chapter in book.chapters:
        for chunk in chapter.chunks:
            chunk.memory_cards.clear()
            await db.flush()
            system_prompt = MEMORY_CARD_PROMPT.format(
                book_title=book.title, chapter_title=chapter.title
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk.raw_text},
            ]
            json_format = MemoryCardSchema.model_json_schema()
            try:
                response = ollama.chat(
                    model="qwen3.5:9b",
                    messages=messages,
                    think=False,
                    format=json_format,
                    options={"temperature": 0.5},
                )
                content = response["message"]["content"]
                cards = MemoryCardSchema.model_validate_json(
                    json_repair.repair_json(content)
                )
                for card in cards.cards:
                    db_memory_card = MemoryCardDB(
                        question=card.question,
                        answer=card.answer,
                        keypoint=card.keypoint,
                    )
                    chunk.memory_cards.append(db_memory_card)
                await db.commit()
            except ValidationError as e:
                print(f"Pydantic validation failed: {e}, chunk {chunk.id}")
                await db.rollback()
                continue
    return "OK"


async def graph(book_id: str, db: AsyncSession):
    response = ollama.chat(
        model="qwen3.5:9b",
        messages=[
            {"role": "system", "content": GRAPH_PROMPT},
            {"role": "user", "content": chunk},
        ],
        format=ExtractionResult.model_json_schema(),
        options={"temperature": 0},
    )

    return ExtractionResult.model_validate_json(response.message.content)
