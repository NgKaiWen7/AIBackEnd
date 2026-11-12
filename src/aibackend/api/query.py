from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.db.connection import get_db
from aibackend.models.query import QueryResponse
from aibackend.services.query import fusion_search, lexical_search, semantic_search

router = APIRouter()

@router.post("/query/semantic", response_model=QueryResponse)
async def query_chunks(
    query: str,
    book_id: UUID | None = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    results = await semantic_search(query, db, book_id=book_id, limit=limit)
    return QueryResponse(results=results, count=len(results))


@router.post("/query/lexical", response_model=QueryResponse)
async def lexical_query_chunks(
    query: str,
    book_id: UUID | None = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    results = await lexical_search(query, db, book_id=book_id, limit=limit)
    return QueryResponse(results=results, count=len(results))


@router.post("/query/fusion", response_model=QueryResponse)
async def fusion_query_chunks(
    query: str,
    book_id: UUID | None = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    results = await fusion_search(query, db, book_id=book_id, limit=limit)
    return QueryResponse(results=results, count=len(results))
