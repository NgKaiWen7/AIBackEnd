import uuid
from datetime import datetime

from pydantic import BaseModel, Field, JsonValue


class Book(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str | None = None
    category: list[str] | None = Field(default_factory=list)
    status: str | None = "Want to Read"
    last_read: datetime | None = None
    description: str | None = None
    source: str | None = None
    created_at: datetime | None = None


class Chunk(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    book_id: uuid.UUID
    position: int | None = None
    level: int = -1
    raw_text: str
    meta_data: JsonValue = None
    card_path: str | None = None
    embeddings: list[float] | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class Cluster(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    book_id: uuid.UUID
    parent_id: uuid.UUID
    membership: list[int]
    total_length: int
    level: int = 0
    summary: str | None = None
