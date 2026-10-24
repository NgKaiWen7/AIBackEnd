from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MemoryCardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_book(self, book_id: UUID) -> dict | None:
        result = await self.db.execute(
            text("""
                SELECT id, title
                FROM books
                WHERE id = :book_id
            """),
            {"book_id": book_id},
        )
        row = result.mappings().one_or_none()
        return dict(row) if row else None

    async def get_chunks(self, book_id: UUID) -> list[dict]:
        result = await self.db.execute(
            text("""
                SELECT
                    bc.id AS chunk_id,
                    bc.raw_text,
                    ch.title AS chapter_title
                FROM book_chapters AS ch
                JOIN book_chunks AS bc
                    ON bc.chapter_id = ch.id
                WHERE ch.book_id = :book_id
                ORDER BY ch.chapter_number, bc.position
            """),
            {"book_id": book_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def delete_chunk_memory_cards(self, chunk_id: UUID) -> None:
        await self.db.execute(
            text("""
                DELETE FROM memory_cards
                WHERE chunk_id = :chunk_id
            """),
            {"chunk_id": chunk_id},
        )

    async def create_memory_card(
        self, chunk_id: UUID, question: str, answer: str, keypoint: str
    ) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO memory_cards (
                    chunk_id,
                    question,
                    answer,
                    keypoint
                )
                VALUES (
                    :chunk_id,
                    :question,
                    :answer,
                    :keypoint
                )
                RETURNING id
            """),
            {
                "chunk_id": chunk_id,
                "question": question,
                "answer": answer,
                "keypoint": keypoint,
            },
        )
        return result.scalar_one()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()
