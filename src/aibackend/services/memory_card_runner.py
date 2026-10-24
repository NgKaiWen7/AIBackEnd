#!/usr/bin/env python3
"""Load topic/concepts JSON and build one image prompt per concept.

No third-party packages are needed to validate the input or export prompts.

Examples:
    python memory_card_runner.py cards.example.json
    python memory_card_runner.py cards.example.json --output prompts.json
    python memory_card_runner.py cards.json --runner my_playwright_script:run

A runner passed with --runner must expose: run(playwright, prompts)
where prompts is a list[str].
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

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
    """Raised when the input JSON does not follow the memory-card schema."""


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
        with source.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Card JSON file not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise CardSchemaError(
            f"Invalid JSON in {source} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    return validate_cards(data)


def build_prompts(data: dict[str, Any]) -> list[str]:
    """Build one standalone image-generation prompt per concept."""
    data = validate_cards(data)
    topic = data["topic"].strip()
    prompts = []

    for concept in data["concepts"]:
        prompt = f"""{STYLE_PROMPT}

TOPIC
{topic}

CARD TITLE
{concept["title"].strip()}

CARD CONTENT
--- BEGIN ---
{concept["content"].strip()}
--- END ---

ILLUSTRATION BRIEF
--- BEGIN ---
{concept["image_prompt"].strip()}
--- END ---
"""
        prompts.append(prompt)

    return prompts
