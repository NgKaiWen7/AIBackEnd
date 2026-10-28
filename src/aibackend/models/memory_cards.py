from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CardStyle(StrEnum):
    STUDENT_NOTEBOOK = "student_notebook"
    TECHNICAL_BLUEPRINT = "technical_blueprint"
    EDITORIAL_TEXTBOOK = "editorial_textbook"
    MINIMALIST_TECHNICAL = "minimalist_technical"
    DARK_TECHNICAL = "dark_technical"
    HAND_DRAWN_SCHEMATIC = "hand_drawn_schematic"


class PromptDomain(StrEnum):
    GENERAL = "general"
    CODE = "code"
    MATHEMATICS = "mathematics"
    SYSTEMS = "systems"
    CAR_TECHNICIAN = "car_technician"


STYLE_PROMPTS: dict[CardStyle, str] = {
    CardStyle.STUDENT_NOTEBOOK: """
Warm ivory graph-paper background, hand-drawn black ink sketches,
imperfect pen strokes, pastel blue, lavender, sage green, coral pink,
and soft yellow highlighter accents. Annotated diagrams, handwritten
arrows, underlines, and carefully organized engineering revision notes.
Handmade, approachable, and technically rigorous. Flat 2D illustration.
""".strip(),
    CardStyle.TECHNICAL_BLUEPRINT: """
Deep navy blueprint background, fine cyan grid lines, precise white
and cyan technical drawings, restrained orange highlights, schematic
arrows, dimension marks, and engineering annotations. Emphasize
architecture and structural clarity. Flat technical drafting aesthetic.
""".strip(),
    CardStyle.EDITORIAL_TEXTBOOK: """
Warm off-white paper, refined black typography, muted navy and burgundy
accents, clean geometric diagrams, restrained colored annotations,
and textbook-style information hierarchy. Academically rigorous,
precise, and easy to scan. Generous whitespace.
""".strip(),
    CardStyle.MINIMALIST_TECHNICAL: """
Clean white background, dark graphite linework, muted blue and teal
accents, simple geometric shapes, thin arrows, concise labels, and
precise diagrams. Minimal decoration, high legibility, and generous
whitespace. Modern flat 2D technical illustration.
""".strip(),
    CardStyle.DARK_TECHNICAL: """
Dark indigo background, warm ivory panels, amber and muted teal
accents, crisp technical drawings, compact labeled diagrams, and
carefully structured information blocks. Premium engineering
field-guide aesthetic. High contrast, flat 2D illustration.
""".strip(),
    CardStyle.HAND_DRAWN_SCHEMATIC: """
Light cream paper, expressive black marker lines, rough but clear
component sketches, handwritten annotations, colored arrows, and
pastel yellow, blue, and coral highlights. Use visual metaphors,
exploded diagrams, and process sketches. Informal but technically
accurate study notes.
""".strip(),
}


SYSTEM_PROMPTS: dict[PromptDomain, str] = {
    PromptDomain.GENERAL: """
Create one self-contained technical memory card from the supplied
concept. Establish a clear title, central visual explanation, concise
annotations, and a key takeaway where appropriate. Adapt the layout
to the concept. Preserve technical meaning and relationships; never
invent details. Prioritize legibility, accuracy, and visual hierarchy.
Produce one finished image only.
""".strip(),
    PromptDomain.CODE: """
Create one software engineering memory card. Preserve code syntax,
identifiers, operators, indentation, function signatures, and API
behavior accurately. Use code fragments, execution flows, input-output
examples, or state diagrams when useful. Never invent code or alter
its semantics. Prioritize correctness and legibility.
""".strip(),
    PromptDomain.MATHEMATICS: """
Create one mathematics or machine-learning memory card. Preserve
equations, symbols, variable meanings, assumptions, tensor dimensions,
and mathematical relationships. Use annotated equations, geometric
intuition, computational graphs, or derivations where appropriate.
Never fabricate a derivation or change a formula.
""".strip(),
    PromptDomain.SYSTEMS: """
Create one systems engineering memory card. Explain architecture,
algorithms, or infrastructure using accurate components, boundaries,
dependencies, ownership, data flow, control flow, and failure modes
where relevant. Ensure arrows and labels represent real relationships.
Never invent protocols, guarantees, or system behavior.
""".strip(),
    PromptDomain.CAR_TECHNICIAN: """
Create one automotive technician learning card. Explain vehicle
components, mechanical systems, electrical circuits, or diagnostic
procedures accurately. Use labeled diagrams, wiring schematics, and
troubleshooting flows where useful. Preserve technical specifications
and highlight relevant safety precautions.
""".strip(),
}


def build_system_prompt(
    style: CardStyle = CardStyle.STUDENT_NOTEBOOK,
    domain: PromptDomain = PromptDomain.GENERAL,
) -> str:
    return f"""{SYSTEM_PROMPTS[domain]}
VISUAL STYLE
{STYLE_PROMPTS[style]}

OUTPUT CONSTRAINTS
Use the selected visual style consistently. No contact sheets, multiple
cards, watermarks, mockup frames, or accompanying text. Return one
finished image only.
"""


class MemoryConcept(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    image_prompt: str
    generate: bool = True
    image_path: str | None = None


class CardDeck(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    system_prompt: str
    title: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    concepts: list[MemoryConcept] = Field(default_factory=list)


class MemoryCardResponse(BaseModel):
    title: str | None
    concepts: list[MemoryConcept] = Field(default_factory=list)

    success: int = 0
    failure: int = 0
    empty: int = 0


class MemoryCardImportResponse(BaseModel):
    deck_id: UUID
    source_id: UUID
    topic: str
    cards_imported: int


class MemoryCardImport(BaseModel):
    topic: str = Field(min_length=1)
    concepts: list[MemoryConcept] = Field(min_length=1)
