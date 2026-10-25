import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Book(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    position: int
    raw_text: str
    meta_data: str | None
    embeddings: list[float] | None = None
    created_at: datetime = Field(default_factory=datetime.now)
