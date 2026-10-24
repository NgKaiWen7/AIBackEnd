
import json
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.repositories.memory_card_prompt_repository import (
    MemoryCardPromptRepository,
)


ROOT_KEYS = {"topic", "concepts"}
CONCEPT_KEYS = {"title", "content", "image_prompt"}

STYLE_PROMPT = """Create exactly ONE premium, technically rigorous educational memory card as a finished raster image.

OUTPUT
- Return exactly one completed image and nothing else.
- Never output explanations outside the image, SVG, HTML, XML, Markdown, JSON, code, or image source markup.
- Do not create multiple cards, contact sheets, collages, slide decks, posters, or mockups.

VISUAL STYLE
- Dark indigo background, warm ivory content panels, restrained amber accents, and crisp, high-contrast typography.
- Clean 4:5 portrait composition with precise spacing, clear visual hierarchy, and comfortable margins.
- Use accurate technical diagrams, schematic illustrations, equations, symbols, and visual relationships.
- Every visual element must contribute directly to understanding the concept.

CONTENT AND ACCURACY
- Render the supplied title exactly.
- Preserve the meaning, terminology, spelling, symbols, equations, identifiers, and code in the supplied content.
- Follow the illustration brief and ensure the illustration does not contradict the supplied information.
- Communicate visually using diagrams, symbols, and concise labels rather than lengthy explanations or paragraphs.
- Include only relevant content. Never invent facts or add generic introductions, conclusions, filler, watermarks, signatures, or fake logos.
- Keep all text and important diagram elements readable and within the image boundaries.
"""


class CardSchemaError(ValueError):
    """Raised when input JSON does not follow the expected schema."""


def _require_string(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CardSchemaError(
            f"{path} must be a non-empty string"
        )


def _require_keys(
    obj: dict[str, Any],
    expected: set[str],
    path: str,
) -> None:
    missing = expected - obj.keys()
    extra = obj.keys() - expected

    if missing:
        raise CardSchemaError(
            f"{path} is missing required keys: "
            f"{', '.join(sorted(missing))}"
        )

    if extra:
        raise CardSchemaError(
            f"{path} has unsupported keys: "
            f"{', '.join(sorted(extra))}"
        )


def validate_cards(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise CardSchemaError("root must be a JSON object")

    _require_keys(data, ROOT_KEYS, "root")
    _require_string(data["topic"], "topic")

    concepts = data["concepts"]

    if not isinstance(concepts, list) or not concepts:
        raise CardSchemaError(
            "concepts must be a non-empty array"
        )

    for index, concept in enumerate(concepts):
        path = f"concepts[{index}]"

        if not isinstance(concept, dict):
            raise CardSchemaError(f"{path} must be an object")

        _require_keys(concept, CONCEPT_KEYS, path)

        for key in CONCEPT_KEYS:
            _require_string(concept[key], f"{path}.{key}")

    return data


def load_cards(path: str | Path) -> dict[str, Any]:
    source = Path(path)

    try:
        with source.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Card JSON file not found: {source}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise CardSchemaError(
            f"Invalid JSON in {source} at line "
            f"{exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    return validate_cards(data)


def build_prompt_records(
    data: dict[str, Any],
) -> list[dict[str, str]]:
    """Build one database-ready record per concept."""
    data = validate_cards(data)
    topic = data["topic"].strip()
    records = []

    for concept in data["concepts"]:
        title = concept["title"].strip()
        content = concept["content"].strip()
        image_prompt = concept["image_prompt"].strip()

        prompt = f"""{STYLE_PROMPT}

TOPIC
{topic}

CARD TITLE
{title}

CARD CONTENT
--- BEGIN ---
{content}
--- END ---

ILLUSTRATION BRIEF
--- BEGIN ---
{image_prompt}
--- END ---
"""

        records.append({
            "topic": topic,
            "title": title,
            "prompt": prompt,
        })

    return records


def build_prompts(data: dict[str, Any]) -> list[str]:
    """Preserve the original API for callers needing only prompts."""
    return [
        record["prompt"]
        for record in build_prompt_records(data)
    ]


class MemoryCardPromptService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MemoryCardPromptRepository(db)

    async def save_data(self, data: Any) -> dict[str, Any]:
        """Validate input, generate prompts, and save atomically."""
        data = validate_cards(data)
        records = build_prompt_records(data)

        try:
            saved = await self.repo.create_many(records)
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return {
            "topic": data["topic"].strip(),
            "inserted_count": len(saved),
            "ids": [str(record.id) for record in saved],
            "titles": [record.title for record in saved],
        }

    async def save_file(self, path: str | Path) -> dict[str, Any]:
        """Load a JSON file and persist all generated prompts."""
        data = load_cards(path)
        return await self.save_data(data)
