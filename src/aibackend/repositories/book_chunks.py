from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BookChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_book(self, book_id: UUID) -> dict | None:
        result = await self.db.execute(
            text("""
                SELECT id, title, source
                FROM books
                WHERE id = :book_id
            """),
            {"book_id": book_id},
        )
        row = result.mappings().one_or_none()
        return dict(row) if row else None

    async def delete_chapters(self, book_id: UUID) -> None:
        await self.db.execute(
            text("""
                DELETE FROM book_chapters
                WHERE book_id = :book_id
            """),
            {"book_id": book_id},
        )

    async def create_chapter(
        self, book_id: UUID, chapter_number: int, title: str
    ) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO book_chapters (
                    book_id,
                    chapter_number,
                    title
                )
                VALUES (
                    :book_id,
                    :chapter_number,
                    :title
                )
                RETURNING id
            """),
            {
                "book_id": book_id,
                "chapter_number": chapter_number,
                "title": title,
            },
        )
        return result.scalar_one()

    async def create_chunk(
        self, chapter_id: UUID, position: int, raw_text: str | None
    ) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO book_chunks (
                    chapter_id,
                    position,
                    raw_text
                )
                VALUES (
                    :chapter_id,
                    :position,
                    :raw_text
                )
                RETURNING id
            """),
            {
                "chapter_id": chapter_id,
                "position": position,
                "raw_text": raw_text,
            },
        )
        return result.scalar_one()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def get_book_context(
        self, book_id: str, chapter_id: str | None = None
    ) -> dict[str, Any] | None:
        result = await self.db.execute(
            text("""
                SELECT
                    b.id AS book_id,
                    b.title AS book_title,
                    c.id AS chapter_id,
                    c.chapter_number,
                    c.title AS chapter_title
                FROM books AS b
                LEFT JOIN book_chapters AS c
                    ON c.book_id = b.id
                    AND (
                        CAST(:chapter_id AS uuid) IS NULL
                        OR c.id = CAST(:chapter_id AS uuid)
                    )
                WHERE b.id = CAST(:book_id AS uuid)
                ORDER BY c.chapter_number
            """),
            {
                "book_id": book_id,
                "chapter_id": chapter_id,
            },
        )

        rows = result.mappings().all()

        if not rows:
            return None

        chapters = [
            {
                "id": row["chapter_id"],
                "chapter_number": row["chapter_number"],
                "title": row["chapter_title"],
            }
            for row in rows
            if row["chapter_id"] is not None
        ]

        if chapter_id and not chapters:
            raise ValueError(f"Chapter {chapter_id} not found in book {book_id}")

        return {
            "id": rows[0]["book_id"],
            "title": rows[0]["book_title"],
            "chapters": chapters,
        }
