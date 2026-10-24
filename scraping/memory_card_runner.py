#!/usr/bin/env python3
"""Validate compact memory-card JSON and build one image prompt per concept."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT_KEYS = {"topic", "concepts"}
CONCEPT_KEYS = {"title", "content", "image_prompt"}

STYLE_PROMPT = """Create one premium, technically rigorous educational memory card.
Use a consistent editorial design with a dark indigo background, warm ivory content
panels, restrained amber accents, crisp high-contrast typography, precise diagrams,
and a clean 4:5 portrait composition. Keep the layout readable and uncluttered.
The illustration must explain the concept rather than act as decoration.

CARD DESIGN RULES
- One central concept per card. This is a compact memory card, not a giant poster,
  slide, contact sheet, or full-page infographic.
- Use one clear central diagram or visual explanation and concise labels/callouts.
- Make the card understandable on its own, without neighboring cards.
- Prefer mechanisms, accurate relationships, compact examples, equations, and code
  when relevant. Define symbols when needed.
- Use arrows only for real data flow, control flow, algorithm steps, or relationships.
- Use generous whitespace, strong contrast, aligned margins, and readable typography.
- Avoid dense paragraphs, tiny text, decorative code walls, fake dashboards, irrelevant
  icons, photorealism, unnecessary 3D effects, watermarks, logos, and ornament.
- Do not invent facts, benchmark numbers, universal thresholds, APIs, or code behavior.
- Technical accuracy matters more than visual complexity."""


class CardSchemaError(ValueError):
    """Raised when input JSON does not follow the memory-card schema."""


def _require_string(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CardSchemaError(f"{path} must be a non-empty string")


def _require_keys(obj: dict[str, Any], expected: set[str], path: str) -> None:
    missing = expected - obj.keys()
    extra = obj.keys() - expected
    if missing:
        raise CardSchemaError(
            f"{path} is missing required keys: {', '.join(sorted(missing))}"
        )
    if extra:
        raise CardSchemaError(
            f"{path} has unsupported keys: {', '.join(sorted(extra))}"
        )


def validate_cards(data: Any) -> dict[str, Any]:
    """Validate and return a topic/concepts collection."""
    if not isinstance(data, dict):
        raise CardSchemaError("root must be a JSON object")
    _require_keys(data, ROOT_KEYS, "root")
    _require_string(data["topic"], "topic")

    concepts = data["concepts"]
    if not isinstance(concepts, list) or not concepts:
        raise CardSchemaError("concepts must be a non-empty array")

    for index, concept in enumerate(concepts):
        path = f"concepts[{index}]"
        if not isinstance(concept, dict):
            raise CardSchemaError(f"{path} must be an object")
        _require_keys(concept, CONCEPT_KEYS, path)
        for key in CONCEPT_KEYS:
            _require_string(concept[key], f"{path}.{key}")
    return data


def load_cards(path: str | Path) -> dict[str, Any]:
    """Load and validate a memory-card JSON file."""
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Card JSON file not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise CardSchemaError(
            f"Invalid JSON in {source} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    return validate_cards(data)


def _build_one_prompt(topic: str, concept: dict[str, str]) -> str:
    return f"""{STYLE_PROMPT}

TASK
Create exactly ONE finished educational memory-card image. Do not create a contact
sheet, multi-card layout, slide deck, poster, collage, or mockup.

TOPIC
{topic.strip()}

CARD TITLE — render exactly
{concept["title"].strip()}

CARD CONTENT — preserve meaning, spelling, symbols, equations, and code; do not invent facts
--- BEGIN CARD CONTENT ---
{concept["content"].strip()}
--- END CARD CONTENT ---

ILLUSTRATION BRIEF
{concept["image_prompt"].strip()}

FINAL RENDERING INSTRUCTIONS
- Use a clear hierarchy: title, concise content, explanatory illustration, and useful labels.
- Make text readable at normal card-viewing size with strong contrast and clean spacing.
- Preserve code, equations, identifiers, parameters, and arrows as accurately as possible.
- The illustration must explain the stated concept and must not contradict the content.
- Keep comfortable margins; do not crop text or important diagram elements.
- Do not add watermarks, signatures, fake logos, unrelated labels, or filler paragraphs.
- Produce the image only; do not explain the image in text."""


def build_prompts(data: dict[str, Any]) -> list[str]:
    """Build one standalone image prompt per concept, preserving JSON order."""
    data = validate_cards(data)
    return [_build_one_prompt(data["topic"], concept) for concept in data["concepts"]]
