import logging
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException
from ollama import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.chunking import Chunk
from aibackend.models.memory_cards import (
    CardDeck,
    CardStyle,
    MemoryCardResponse,
    MemoryConcept,
    PromptDomain,
    build_system_prompt,
)
from aibackend.repositories.book_chunks import BookChunkRepository
from aibackend.repositories.memord_card import MemoryCardRepository
from aibackend.utils.constant import CARD_DECKS_DIR, COMPUTE_SERVER_URL

logger = logging.getLogger(__name__)

client = AsyncClient()

SYSTEM_PROMPT = """
You are an expert technical educator. Extract valuable learning concepts from the supplied book chunk for visual memory card generation.

Focus on:
- Core principles and definitions
- Mechanisms and how things work
- Equations and derivations
- Algorithms and implementation details
- Trade-offs, limitations, and failure modes

Rules:
- Each concept must teach one coherent, self-contained learning objective.
- Preserve technical accuracy, equations, assumptions, and important details.
- Do not invent information or examples unsupported by the source.
- Prefer deep understanding over superficial summaries.
- Make the content concise but sufficiently detailed for learning.
- Describe specific diagrams, equations, flows, or examples that visually explain the concept.
- Extract only genuinely valuable learning concepts.

If the chunk contains no important or useful learning concepts, return the same JSON schema with all three fields set to empty strings: "", "", "".

Return ONLY valid JSON using this schema:
{
  "title": "Concept title",
  "content": "A self-contained explanation of the concept, including essential details, equations, examples, or caveats where relevant.",
  "image_prompt": "Instructions for drawing a clear educational memory card that visually explains this concept."
}

The image_prompt must describe the educational content to visualize, not merely its artistic style. Include specific labels, relationships, equations, steps, or comparisons where appropriate.

Return valid JSON without Markdown fences or additional commentary.
"""


def format_prompt(card_deck: CardDeck):
    concepts = []
    for card in card_deck.concepts:
        prompt = f"""
        {card_deck.system_prompt}
        CARD TITLE
        {card.title}

        LEARNING CONTENT
        {card.content}

        VISUAL INSTRUCTIONS
        {card.image_prompt}

        OUTPUT REQUIREMENTS
        Generate a single, complete learning-card image that fills the
        entire canvas edge to edge, with no external background, outer margins,
        mockups, paper textures, or shadows. Keep all content inside the card,
        preserving technical accuracy, readability,
        and the visual style specified in the image prompt.
        """.strip()
        concepts.append({"id": str(card.id), "prompt": prompt})
    return concepts


async def prompt_memory_card(
    book_id: UUID,
    style: CardStyle,
    domain: PromptDomain,
    db: AsyncSession,
) -> MemoryCardResponse:
    bookchunk_repo = BookChunkRepository(db)
    memory_card_repo = MemoryCardRepository(db)

    book = await bookchunk_repo.get_book(book_id)
    if book is None:
        raise ValueError(f"Book id: {book_id} not found")
    chunks: list[Chunk] = await bookchunk_repo.get_chunks(book_id)
    result = MemoryCardResponse(title=book.title)
    system_prompt = build_system_prompt(style, domain)
    deck = CardDeck(source_id=book.id, title=book.title, system_prompt=system_prompt)
    await memory_card_repo.create_deck(deck)
    for chunk in chunks:
        content = f"Meta data: {chunk.meta_data}\n{chunk.raw_text}"
        try:
            response = await client.chat(
                model="qwen3.5:4b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                think=False,
                options={"temperature": 0.5},
                format=MemoryConcept.model_json_schema(),
            )
            data = MemoryConcept.model_validate_json(response.message.content)
            if not data.title and not data.content and not data.image_prompt:
                result.empty += 1
                continue
            await memory_card_repo.create_cards(deck.id, [data])
            await memory_card_repo.commit()

        except ValidationError as exc:
            print(f"Validation failed for chunk {chunk.id}: {exc}")
            result.failure += 1
            continue

        result.concepts.append(data)
        result.success += 1

    return result


async def send_all_image(db: AsyncSession) -> dict[str, Any]:
    # Upload previously generated images first.
    async with httpx.AsyncClient(timeout=300) as client:
        upload_response = await client.post(
            "http://192.168.0.115:8000/upload-generated-images"
        )
        upload_response.raise_for_status()

    repo = MemoryCardRepository(db)
    card_decks = await repo.queue_all()

    concepts = []
    deck_stats = []

    for card_deck in card_decks:
        deck_concepts = format_prompt(card_deck)
        concepts.extend(deck_concepts)

        deck_stats.append(
            {
                "deck_id": str(card_deck.id),
                "deck_title": card_deck.title,
                "concepts_count": len(deck_concepts),
            }
        )

    # Submit concepts to the image-generation server.
    if len(concepts) > 0:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{COMPUTE_SERVER_URL}/generate",
                json=concepts,
            )
            response.raise_for_status()
        ids = [concept["id"] for concept in concepts]
        await repo.update_queue(ids)
        await db.commit()
        try:
            generation_result = response.json()
        except ValueError:
            generation_result = response.text

        try:
            upload_result = upload_response.json()
        except ValueError:
            upload_result = upload_response.text

        return {
            "status": "success",
            "stats": {
                "decks_found": len(card_decks),
                "concepts_submitted": len(concepts),
                "decks": deck_stats,
            },
            "upload": {
                "status_code": upload_response.status_code,
                "result": upload_result,
            },
            "generation": {
                "status_code": response.status_code,
                "result": generation_result,
            },
        }
    return {"status": "success", "stats": {"decks_found": 0}}


async def generate_memory_card_images(source_id: UUID, db: AsyncSession) -> dict:
    repo = MemoryCardRepository(db)
    card_deck = await repo.get_cards(source_id)

    if not card_deck:
        raise HTTPException(
            status_code=404,
            detail="No memory cards found for this source",
        )

    concepts = format_prompt(card_deck)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{COMPUTE_SERVER_URL}/generate",
                json=concepts,
            )
            response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Timed out waiting for the computing server",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The computing server rejected the generation request",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the computing server",
        ) from exc

    return response.json()
