from uuid import UUID

from aibackend.models.query import QueryResult
from aibackend.repositories.search_queries import QueryRepository
from sqlalchemy.ext.asyncio import AsyncSession

async def semantic_search(
    query: str, db: AsyncSession, book_id: UUID | None = None, limit: int = 5
) -> list[QueryResult]:
    repo = QueryRepository(db)
    return await repo.vector_search(query, book_id=book_id, limit=limit)


async def lexical_search(
    query: str, db: AsyncSession, book_id: UUID | None = None, limit: int = 5
) -> list[QueryResult]:
    repo = QueryRepository(db)
    return await repo.lexical_search(query, book_id=book_id, limit=limit)
