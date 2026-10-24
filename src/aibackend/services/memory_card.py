from uuid import UUID

import json_repair
import ollama
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.memory_cards import MemoryCards
from aibackend.prompts.memory_card import PROMPT as MEMORY_CARD_PROMPT
from aibackend.repositories.memory_cards import MemoryCardRepository


async def memory_card(book_id: UUID, db: AsyncSession) -> str:
    repo = MemoryCardRepository(db)

    book = await repo.get_book(book_id)
    if book is None:
        raise ValueError(f"Book {book_id} not found")

    chunks = await repo.get_chunks(book_id)

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]

        system_prompt = MEMORY_CARD_PROMPT.format(
            book_title=book["title"],
            chapter_title=chunk["chapter_title"],
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chunk["raw_text"] or ""},
        ]

        try:
            response = await ollama.AsyncClient().chat(
                model="qwen3.5:9b",
                messages=messages,
                think=False,
                format=MemoryCards.model_json_schema(),
                options={"temperature": 0.5},
            )

            content = response["message"]["content"]
            cards = MemoryCards.model_validate_json(
                json_repair.repair_json(content)
            )

            # Replace cards only after successful generation and validation.
            await repo.delete_chunk_memory_cards(chunk_id)

            for card in cards.cards:
                await repo.create_memory_card(
                    chunk_id=chunk_id,
                    question=card.question,
                    answer=card.answer,
                    keypoint=card.keypoint,
                )

            await repo.commit()

        except ValidationError as exc:
            await repo.rollback()
            print(f"Pydantic validation failed: {exc}, chunk {chunk_id}")
            continue

        except Exception:
            await repo.rollback()
            raise

    return "OK"
