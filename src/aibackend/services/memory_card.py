import json_repair
import ollama
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.models.knowledge import MemoryCards as MemoryCardSchema
from aibackend.prompts.memory_card import PROMPT as MEMORY_CARD_PROMPT
from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import BookChunks as BookChunks_db
from aibackend.repositories.knowledge import MemoryCard as MemoryCard_db


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
            chunk_id = chunk.id
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
                    db_memory_card = MemoryCard_db(
                        question=card.question,
                        answer=card.answer,
                        keypoint=card.keypoint,
                    )
                    chunk.memory_cards.append(db_memory_card)
                await db.commit()
            except ValidationError as e:
                print(f"Pydantic validation failed: {e}, chunk {chunk_id}")
                await db.rollback()
                continue
    return "OK"
