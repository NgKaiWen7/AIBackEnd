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

    async def create_book(self, book: Book) -> Book:
        result = await self.db.execute(
            text("""
                INSERT INTO books (
                    id,
                    title,
                    category,
                    status,
                    last_read,
                    description,
                    source,
                    created_at
                )
                VALUES (
                    :id,
                    :title,
                    :category,
                    :status,
                    :last_read,
                    :description,
                    :source,
                    COALESCE(:created_at, NOW())
                )
                RETURNING *
            """),
            {
                "id": book.id,
                "title": book.title,
                "category": book.category,
                "status": book.status,
                "last_read": book.last_read,
                "description": book.description,
                "source": book.source,
                "created_at": book.created_at,
            },
        )

        row = result.mappings().one()
        return Book(**row)

    async def get_book(self, book_id: UUID) -> Book | None:
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

    async def get_chunks(self, id: UUID, combine_chunk: int) -> list[Chunk]:
        result = await self.db.execute(
            text(
                """
                SELECT * FROM large_chunks
                WHERE book_id = :book_id
                """
            ),
            {"book_id": id},
        )
        chunks = []
        for i in result.mappings():
            data = dict(i)
            data.pop("embeddings")
            chunks.append(Chunk(**data))
        return chunks

    async def update_embedding(self, id: UUID, embeddings: list[float]):
        await self.db.execute(
            text("""
                UPDATE chunks SET
                embeddings = :embeddings
                WHERE id = :id
                """),
            {"embeddings": str(embeddings), "id": id},
        )

    async def query(self, embeddings: list[float], book_id):
        query = text(
            """
            SELECT *
            FROM chunks ORDER BY embeddings <=> CAST(:embeddings AS vector) ASC
            LIMIT 5
            """
        )
        chunks = []
        result = await self.db.execute(query, {"embeddings": str(embeddings)})
        for row in result.mappings():
            data = dict(row)
            data.pop("embeddings")
            chunks.append(Chunk(**data))
        return chunks
