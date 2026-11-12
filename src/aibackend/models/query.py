from uuid import UUID

from pydantic import BaseModel, Field

from aibackend.models.chunking import Chunk


class QueryRequest(BaseModel):
    """Input for semantic chunk search."""

    query: str = Field(min_length=1)
    book_id: UUID | None = None
    limit: int = Field(default=5, ge=1, le=50)


class QueryResult(BaseModel):
    chunk: Chunk
    similarity: float


class QueryResponse(BaseModel):
    results: list[QueryResult] = Field(default_factory=list)
    count: int = 0
