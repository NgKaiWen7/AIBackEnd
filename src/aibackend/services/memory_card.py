import logging
from uuid import UUID

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


async def memory_card(
    card_deck_dir, book_id: UUID, style: CardStyle, domain: PromptDomain, db: AsyncSession
) -> MemoryCardResponse:
    bookchunk_repo = BookChunkRepository(db)
    memory_card_repo = MemoryCardRepository(db, card_deck_dir)

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
                model="qwen3.5:9b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                think=False,
                options={"temperature": 0.5},
                format=MemoryConcept.model_json_schema(),
            )
            data = MemoryConcept.model_validate_json(response.message.content)
            await memory_card_repo.create_cards(deck.id, [data])
            await memory_card_repo.commit()

        except ValidationError as exc:
            print(f"Validation failed for chunk {chunk.id}: {exc}")
            result.failure += 1
            continue

        if not data.title and not data.content and not data.image_prompt:
            result.empty += 1
            continue

        result.concepts.append(data)
        result.success += 1

    return result
