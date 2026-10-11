import logging
from pathlib import Path

import json_repair
import ollama
from fastapi import UploadFile
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.models.knowledge import MemoryCards as MemoryCardSchema
from aibackend.prompts.memory_card import PROMPT
from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import MemoryCard as MemoryCardDB
from aibackend.utils.chunk import chunk_text
from aibackend.utils.pdf import get_chapters, get_title

logger = logging.getLogger(__name__)

async def ingest_book(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(selectinload(Book_db.chapters))
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
        book.chapters.append(
            BookChapter_db(
                chapter_number=chapter_number,
                title=chapter_title,
                content=(content or "").replace("\x00", ""),
            )
        )

    await db.commit()
    await db.refresh(book)

    return {
        "book_id": book.id,
        "title": book.title,
        "chapters_saved": len(chapters),
    }


async def memory_card(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(
            selectinload(Book_db.chapters).selectinload(BookChapter_db.memory_cards)
        )
        .where(Book_db.id == book_id)
    )
    book = await db.scalar(stmt)
    if book is None:
        raise ValueError(f"Book {book_id} not found")
    chapters = []
    for chapter in book.chapters:
        chapters.append(
            {
                "id": chapter.id,
                "title": chapter.title,
                "content": chapter.content or "",
            }
        )
        chapter.memory_cards.clear()
    await db.flush()
    await db.commit()
    for chapter in chapters:
        chapter_id = chapter["id"]
        chapter_title = chapter["title"]
        chapter_content = chapter["content"]
        chunks = chunk_text(chapter_content, chunk_size=10_000, overlap=2_000)
        for i, chunk in enumerate(chunks):
            logger.info(
                "Starting book ingestion: chunk=%s for chapter=%s", i, chapter_title
            )
            system_prompt = PROMPT.format(
                book_title=chapter_title, chapter_title=chapter_title
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk},
            ]
            json_format = MemoryCardSchema.model_json_schema()
            response = ollama.chat(
                model="qwen3.5:9b",
                messages=messages,
                think=False,
                format=json_format,
                options={"temperature": 0.5},
            )
            content = response["message"]["content"]
            try:
                cards = MemoryCardSchema.model_validate_json(
                    json_repair.repair_json(content)
                )
                for card in cards.cards:
                    db_memory_card = MemoryCardDB(
                        chapter_id=chapter_id,
                        question=card.question,
                        answer=card.answer,
                        keypoint=card.keypoint,
                    )

                    db.add(db_memory_card)
                    await db.commit()
            except ValidationError as e:
                print(f"Pydantic validation failed: {e}, chunk {i + 1}")
                await db.rollback()
                continue
    return "OK"
