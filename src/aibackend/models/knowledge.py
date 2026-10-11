from pydantic import BaseModel


class MemoryCard(BaseModel):
    question: str
    answer: str
    keypoint: str


class MemoryCards(BaseModel):
    cards: list[MemoryCard]
