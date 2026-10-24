from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BookEmbeddingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_chunks_for_embedding(self, book_id: UUID) -> list[dict]:
        result = await self.db.execute(
            text("""
                SELECT bc.id, bc.raw_text
                FROM book_chunks AS bc
                JOIN book_chapters AS ch
                    ON ch.id = bc.chapter_id
                WHERE ch.book_id = :book_id
                  AND bc.raw_text IS NOT NULL
                  AND bc.raw_text <> ''
                  AND bc.embeddings IS NULL
                ORDER BY ch.chapter_number, bc.position
            """),
            {"book_id": book_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def update_embedding(self, chunk_id: UUID, embedding: list[float]) -> None:
        await self.db.execute(
            text("""
                UPDATE book_chunks
                SET embeddings = :embedding
                WHERE id = :chunk_id
            """),
            {
                "chunk_id": chunk_id,
                "embedding": embedding,
            },
        )

    async def search_chunks(
        self, embedding: list[float], candidates: int = 50
    ) -> list[dict]:
        result = await self.db.execute(
            text("""
                SELECT
                    id,
                    raw_text,
                    embeddings <=> CAST(:embedding AS vector) AS distance
                FROM book_chunks
                WHERE embeddings IS NOT NULL
                ORDER BY embeddings <=> CAST(:embedding AS vector)
                LIMIT :candidates
            """),
            {
                "embedding": str(embedding),
                "candidates": candidates,
            },
        )
        return [dict(row) for row in result.mappings().all()]

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()
