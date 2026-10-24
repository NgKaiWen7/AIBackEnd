import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from aibackend.models.memory_cards import MemoryCard


class BookChunks(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    chapter_id: uuid.UUID
    position: int
    raw_text: str | None = None
    embeddings: list[float] | None = None

    memory_cards: list[MemoryCard] = Field(default_factory=list)


class BookChapter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    book_id: uuid.UUID
    chapter_number: int
    title: str

    chunks: list[BookChunks] = Field(default_factory=list)


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

    chapters: list[BookChapter] = Field(default_factory=list)
