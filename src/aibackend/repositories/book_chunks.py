from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.chunking import Book, Chunk


class BookChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def get_book(self, book_id: UUID) -> Book:
        result = await self.db.execute(
            text("""
                SELECT *
                FROM books
                WHERE id = :book_id
            """),
            {"book_id": book_id},
        )
        row = result.mappings().one_or_none()
        return Book(**row) if row else None

    async def delete_chunks(self, book_id: UUID) -> None:
        await self.db.execute(
            text("""
                DELETE FROM chunks
                WHERE book_id = :book_id
            """),
            {"book_id": str(book_id)},
        )

    async def create_chunk(self, chunk: Chunk) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO chunks (
                    book_id,
                    position,
                    raw_text,
                    meta_data
                )
                VALUES (
                    :book_id,
                    :position,
                    :raw_text,
                    :meta_data
                )
                RETURNING id
            """),
            {
                "book_id": str(chunk.book_id),
                "position": chunk.position,
                "raw_text": chunk.raw_text,
                "meta_data": chunk.meta_data,
            },
        )
        return result.scalar_one()
