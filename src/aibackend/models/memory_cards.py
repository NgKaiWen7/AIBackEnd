import uuid
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MemoryCardImagePrompt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    topic: str
    title: str
    prompt: str
    created_at: datetime | None = None


class MemoryCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    chunk_id: uuid.UUID
    question: str
    answer: str
    keypoint: str
    created_at: datetime | None = None

class MemoryCards(BaseModel):
    cards: list[MemoryCard]
