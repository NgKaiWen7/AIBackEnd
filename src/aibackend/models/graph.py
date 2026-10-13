from typing import Literal

from pydantic import BaseModel, Field

EntityType = Literal[
    "Concept",  # Abstract ideas, principles, theories, and mathematical concepts.
    "System",  # Complete systems, platforms, frameworks, and technologies.
    "Component",  # Parts of a larger system or architecture.
    "Algorithm",  # Algorithms, procedures, and computational methods.
    "DataStructure",  # Structures used to organize, store, or represent data.
]


class Entity(BaseModel):
    name: str
    type: EntityType


class EntityExtractionResult(BaseModel):
    entities: list[Entity] = Field(default_factory=list)

RelationType = Literal[
    "IS_A",        # Entity is a specific kind or instance of another concept.
    "PART_OF",     # Entity is a constituent part of a larger system or structure.
    "USES",        # Entity uses another entity to perform an operation or provide functionality.
    "IMPLEMENTS",  # Entity implements an algorithm, interface, protocol, or specification.
    "DEPENDS_ON",  # Entity requires another entity to function correctly.
    "RELATED_TO",  # Entities have a meaningful relationship not covered by other predicates.
    "PRODUCES",    # Entity generates, creates, or outputs another entity.
    "TRANSFORMS",  # Entity converts input data or state into another form.
    "STORES",      # Entity stores data or information.
    "ENABLES",     # Entity makes a capability or operation possible.
]

class Relation(BaseModel):
    subject: str
    predicate: RelationType
    object: str
    evidence: str

class RelationExtractionResult(BaseModel):
    relations: list[Relation] = Field(default_factory=list)
