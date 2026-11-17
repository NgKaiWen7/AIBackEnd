from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.chunking import Chunk
from aibackend.models.query import QueryResult
from aibackend.utils.embed import get_embedding

class QueryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def vector_search(
        self, query: str, book_id: UUID | None = None, limit: int = 5
    ) -> list[QueryResult]:
        query_embedding = await get_embedding(query)

        result = await self.db.execute(
            text("""
                SELECT id, book_id, position, level, raw_text, meta_data,
                       card_path, generate, created_at,
                       1 - (embeddings <=> CAST(:embedding AS vector)) AS similarity
                FROM chunks
                WHERE embeddings IS NOT NULL
                  AND raw_text <> ''
                  AND (
                      CAST(:book_id AS uuid) IS NULL
                      OR book_id = CAST(:book_id AS uuid)
                  )
                ORDER BY embeddings <=> CAST(:embedding AS vector)
                LIMIT :limit
            """),
            {
                "embedding": str(query_embedding),
                "book_id": book_id,
                "limit": limit,
            },
        )

        return [
            QueryResult(chunk=Chunk(**row), similarity=row["similarity"])
            for row in result.mappings()
        ]

    async def lexical_search(
        self, query: str, book_id: UUID | None = None, limit: int = 5
    ) -> list[QueryResult]:
        """Search chunk text using PostgreSQL full-text search."""
        result = await self.db.execute(
            text("""
                SELECT id, book_id, position, level, raw_text, meta_data,
                       card_path, generate, created_at,
                       ts_rank_cd(
                           to_tsvector('english', coalesce(raw_text, '')),
                           websearch_to_tsquery('english', :query)
                       ) AS similarity
                FROM chunks
                WHERE to_tsvector('english', coalesce(raw_text, ''))
                      @@ websearch_to_tsquery('english', :query)
                  AND (
                      CAST(:book_id AS uuid) IS NULL
                      OR book_id = CAST(:book_id AS uuid)
                  )
                ORDER BY similarity DESC
                LIMIT :limit
            """),
            {
                "query": query,
                "book_id": str(book_id) if book_id else None,
                "limit": limit,
            },
        )

        return [
            QueryResult(chunk=Chunk(**row), similarity=row["similarity"])
            for row in result.mappings()
        ]
