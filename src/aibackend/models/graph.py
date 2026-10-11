
from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str
    type: str
    description: str


class Relation(BaseModel):
    subject: str
    predicate: str
    object: str
    evidence: str


class ExtractionResult(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relations: list[Relation] = Field(default_factory=list)
