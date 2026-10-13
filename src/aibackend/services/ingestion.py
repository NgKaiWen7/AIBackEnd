import json
import logging
from pathlib import Path

import json_repair
import ollama
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.models.graph import (
    Entity,
    EntityExtractionResult,
    RelationExtractionResult,
)
from aibackend.models.knowledge import MemoryCards as MemoryCardSchema
from aibackend.prompts.graph_ingestion import ENTITY_PROMPT, RELATION_PROMPT
from aibackend.prompts.memory_card import PROMPT as MEMORY_CARD_PROMPT
from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import BookChunks as BookChunks_db
from aibackend.repositories.knowledge import MemoryCard as MemoryCardDB
from aibackend.utils.chunk import chunk_text
from aibackend.utils.pdf import get_chapters

logger = logging.getLogger(__name__)


async def ingest_book(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(selectinload(Book_db.chapters).selectinload(BookChapter_db.chunks))
        .where(Book_db.id == book_id)
    )
    result = await db.execute(stmt)
    book: Book_db = result.scalar_one()
    book.chapters.clear()
    await db.flush()
    pdf_path = Path("/mnt") / book.source.lstrip("/")
    chapters: dict[str, str] = get_chapters(pdf_path)

    for chapter_number, (chapter_title, content) in enumerate(
        chapters.items(), start=1
    ):
        bookchapter_db = BookChapter_db(
            chapter_number=chapter_number, title=chapter_title
        )
        chunks = chunk_text(content, chunk_size=1000, overlap=200)
        for i, chunk in enumerate(chunks):
            bookchunk_db = BookChunks_db(raw_text=chunk, position=i)
            bookchapter_db.chunks.append(bookchunk_db)
        book.chapters.append(bookchapter_db)

    await db.commit()
    await db.refresh(book)

    return {
        "book_id": book.id,
    }


async def memory_card(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(
            selectinload(Book_db.chapters)
            .selectinload(BookChapter_db.chunks)
            .selectinload(BookChunks_db.memory_cards)
        )
        .where(Book_db.id == book_id)
    )
    book = await db.scalar(stmt)
    if book is None:
        raise ValueError(f"Book {book_id} not found")
    for chapter in book.chapters:
        for chunk in chapter.chunks:
            chunk_id = chunk.id
            chunk.memory_cards.clear()
            await db.flush()
            system_prompt = MEMORY_CARD_PROMPT.format(
                book_title=book.title, chapter_title=chapter.title
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk.raw_text},
            ]
            json_format = MemoryCardSchema.model_json_schema()
            try:
                response = ollama.chat(
                    model="qwen3.5:9b",
                    messages=messages,
                    think=False,
                    format=json_format,
                    options={"temperature": 0.5},
                )
                content = response["message"]["content"]
                cards = MemoryCardSchema.model_validate_json(
                    json_repair.repair_json(content)
                )
                for card in cards.cards:
                    db_memory_card = MemoryCardDB(
                        question=card.question,
                        answer=card.answer,
                        keypoint=card.keypoint,
                    )
                    chunk.memory_cards.append(db_memory_card)
                await db.commit()
            except ValidationError as e:
                print(f"Pydantic validation failed: {e}, chunk {chunk_id}")
                await db.rollback()
                continue
    return "OK"


import traceback
import uuid

ENTITY_NAMESPACE = uuid.UUID("d2f91ef4-6b7c-4b82-a8bc-64f7ddf197b1")

ALLOWED_RELATIONS = {
    "IS_A",
    "PART_OF",
    "USES",
    "IMPLEMENTS",
    "DEPENDS_ON",
    "RELATED_TO",
    "PRODUCES",
    "TRANSFORMS",
    "STORES",
    "ENABLES",
}
import age


def cypher_literal(value: str) -> str:
    value = value.replace("\\", "\\\\")
    value = value.replace("'", "\\'")
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    return f"'{value}'"


def entity_key(name: str) -> str:
    return name.strip().casefold()


def get_entity_id(entity: Entity) -> str:
    normalized = f"{entity.type}:{entity_key(entity.name)}"
    return str(uuid.uuid5(ENTITY_NAMESPACE, normalized))


async def graph(book_id: str, db: AsyncSession):
    connection = age.connect(
        graph="knowledge_graph",
        dsn="host=localhost port=5432 dbname=knowledge_db user=postgres password=postgres",
    )
    entity_count = 0
    relation_count = 0
    stmt = (
        select(Book_db)
        .options(selectinload(Book_db.chapters).selectinload(BookChapter_db.chunks))
        .where(Book_db.id == book_id)
    )
    book = await db.scalar(stmt)
    if book is None:
        raise ValueError(f"Book {book_id} not found")
    for chapter in book.chapters:
        for chunk in chapter.chunks:
            chunk_id = chunk.id
            try:
                response = ollama.chat(
                    model="qwen3.5:9b",
                    messages=[
                        {"role": "system", "content": ENTITY_PROMPT},
                        {"role": "user", "content": chunk.raw_text},
                    ],
                    think=False,
                    format=EntityExtractionResult.model_json_schema(),
                    options={"temperature": 0.5},
                )
                content = json_repair.repair_json(response["message"]["content"])
                entities: EntityExtractionResult = (
                    EntityExtractionResult.model_validate_json(content)
                )
                entity_ids: dict[str, str] = {}

                for entity in entities.entities:
                    name = entity.name.strip()

                    if not name:
                        continue

                    entity_id = get_entity_id(entity)
                    entity_ids[entity_key(name)] = entity_id

                    query = f"""
                        MERGE (e:Entity {{id: {cypher_literal(entity_id)}}})
                        SET e.name = {cypher_literal(name)},
                            e.type = {cypher_literal(entity.type)}
                        RETURN e.id
                    """

                    cursor = connection.execCypher(query)
                    list(cursor)  # Consume the result.
                    entity_count += 1
                # Stage 2: Extract relations using known entities
                relation_input = (
                    f"Source text:\n{chunk.raw_text}\n\n"
                    f"Known entities:\n"
                    f"{json.dumps([e.model_dump() for e in entities.entities])}"
                )

                relation_response = ollama.chat(
                    model="qwen3.5:9b",
                    messages=[
                        {"role": "system", "content": RELATION_PROMPT},
                        {"role": "user", "content": relation_input},
                    ],
                    think=False,
                    format=RelationExtractionResult.model_json_schema(),
                    options={"temperature": 0.5},
                )

                relations = RelationExtractionResult.model_validate_json(
                    json_repair.repair_json(relation_response["message"]["content"])
                )

                # 3. Create edges between existing entity vertices.
                for relation in relations.relations:
                    predicate = relation.predicate

                    if predicate not in ALLOWED_RELATIONS:
                        continue

                    subject_id = entity_ids.get(entity_key(relation.subject))
                    object_id = entity_ids.get(entity_key(relation.object))

                    if subject_id is None or object_id is None:
                        print(
                            "Skipping relation with unknown entity:",
                            relation.model_dump(),
                        )
                        continue

                    query = f"""
                    MATCH (s:Entity {{id: '{subject_id}'}})
                    MATCH (o:Entity {{id: '{object_id}'}})
                    MERGE (s)-[r:{predicate} {{chunk_id: '{chunk.id}'}}]->(o)
                    SET r.evidence = 'test'
                    RETURN type(r)
                    """
                    cursor = connection.execCypher(query)
                    list(cursor)
                    connection.commit()
                    relation_count += 1
            except Exception:
                traceback.print_exc()
                raise
