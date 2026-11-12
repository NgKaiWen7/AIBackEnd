from uuid import UUID

from aibackend.models.query import QueryResult
from aibackend.repositories.search_queries import QueryRepository
from sqlalchemy.ext.asyncio import AsyncSession


def _reciprocal_rank_fusion(
    result_sets: list[list[QueryResult]],
    limit: int,
    k: int = 60,
) -> list[QueryResult]:
    """Merge ranked result sets using Reciprocal Rank Fusion.

    RRF avoids comparing raw vector and lexical scores directly because they
    use different scales. A result's contribution depends only on its rank in
    each result set.
    """
    fused: dict[str, tuple[QueryResult, float]] = {}

    for results in result_sets:
        for rank, result in enumerate(results, start=1):
            chunk_id = str(result.chunk.id)
            contribution = 1.0 / (k + rank)

            if chunk_id in fused:
                existing_result, existing_score = fused[chunk_id]
                fused[chunk_id] = (existing_result, existing_score + contribution)
            else:
                fused[chunk_id] = (result, contribution)

    ranked = sorted(fused.values(), key=lambda item: item[1], reverse=True)
    return [
        result.model_copy(update={"similarity": score})
        for result, score in ranked[:limit]
    ]


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


async def fusion_search(
    query: str,
    db: AsyncSession,
    book_id: UUID | None = None,
    limit: int = 5,
    candidate_limit: int | None = None,
    rrf_k: int = 60,
) -> list[QueryResult]:
    """Combine semantic and lexical search with Reciprocal Rank Fusion.

    Each search retrieves a larger candidate pool, then the two ranked lists
    are merged. Results appearing in both lists receive a stronger fused score.
    """
    candidate_limit = candidate_limit or max(limit * 10, 50)

    # Keep both queries on the same AsyncSession sequential; an
    # AsyncSession cannot safely execute concurrent operations.
    semantic_results = await semantic_search(
        query, db, book_id=book_id, limit=candidate_limit
    )
    lexical_results = await lexical_search(
        query, db, book_id=book_id, limit=candidate_limit
    )

    return _reciprocal_rank_fusion(
        [semantic_results, lexical_results], limit=limit, k=rrf_k
    )
