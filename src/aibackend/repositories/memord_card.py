import asyncio
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.memory_cards import CardDeck, MemoryConcept
from aibackend.utils.constant import CARD_DECKS_DIR


class MemoryCardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage_root = CARD_DECKS_DIR

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def update_queue(self, ids: list[UUID]) -> int:
        if not ids:
            return 0

        query = text("""
            UPDATE cards
            SET generate = FALSE
            WHERE id IN :ids
            RETURNING id, generate
        """).bindparams(bindparam("ids", expanding=True))

        result = await self.db.execute(query, {"ids": ids})
        updated_rows = result.mappings().all()
        return len(updated_rows)

    async def queue_all(self) -> list[CardDeck]:
        query = text("""
            SELECT
                d.id AS deck_id,
                d.source_id,
                d.system_prompt,
                d.title AS deck_title,
                d.created_at AS deck_created_at,
                c.id AS concept_id,
                c.title AS concept_title,
                c.content,
                c.image_prompt,
                c.image_path
            FROM cards AS c
            JOIN card_decks AS d
                ON d.id = c.deck_id
            WHERE
                c.image_path IS NULL
                AND c.generate = TRUE
            ORDER BY d.id, c.id
        """)

        result = await self.db.execute(query)

        decks: dict[UUID, CardDeck] = {}

        for row in result.mappings():
            deck_id = row["deck_id"]

            if deck_id not in decks:
                decks[deck_id] = CardDeck(
                    id=deck_id,
                    source_id=row["source_id"],
                    system_prompt=row["system_prompt"],
                    title=row["deck_title"],
                    created_at=row["deck_created_at"],
                    concepts=[],
                )

            decks[deck_id].concepts.append(
                MemoryConcept(
                    id=row["concept_id"],
                    title=row["concept_title"],
                    content=row["content"],
                    image_prompt=row["image_prompt"],
                    image_path=row["image_path"],
                )
            )
        return list(decks.values())

    async def get_cards(self, deck_id: UUID) -> CardDeck | None:
        deck_query = text("""
            SELECT id, source_id, system_prompt, title, created_at
            FROM card_decks
            WHERE id = :id
            LIMIT 1
        """)
        result = await self.db.execute(deck_query, {"id": deck_id})
        deck_row = result.mappings().one_or_none()
        if deck_row is None:
            return None
        concepts_query = text("""
            SELECT *
            FROM cards
            WHERE deck_id = :id
            ORDER BY created_at ASC
        """)
        result = await self.db.execute(concepts_query, {"id": deck_row["id"]})
        concepts = [MemoryConcept(**row) for row in result.mappings().all()]
        return CardDeck(**dict(deck_row), concepts=concepts)

    async def create_cards(self, deck_id: UUID, concepts: list[MemoryConcept]) -> int:
        for concept in concepts:
            await self.db.execute(
                text("""
                    INSERT INTO cards (
                        deck_id,
                        title,
                        content,
                        image_prompt,
                        generate
                    )
                    VALUES (
                        :deck_id,
                        :title,
                        :content,
                        :image_prompt,
                        :generate
                    )
                """),
                {
                    "deck_id": deck_id,
                    "title": concept.title,
                    "content": concept.content,
                    "image_prompt": concept.image_prompt,
                    "generate": concept.generate,
                },
            )

        return len(concepts)

    async def create_deck(self, deck: CardDeck) -> CardDeck:
        result = await self.db.execute(
            text("""
                INSERT INTO card_decks (
                    id, source_id, title, system_prompt
                )
                VALUES (
                    :id, :source_id, :title, :system_prompt
                )
                RETURNING id, source_id, title, system_prompt, created_at
            """),
            {
                "id": deck.id,
                "source_id": deck.source_id,
                "title": deck.title,
                "system_prompt": deck.system_prompt,
            },
        )
        deck_row = dict(result.mappings().one())
        for concept in deck.concepts:
            await self.db.execute(
                text("""
                    INSERT INTO cards (
                        deck_id, title, content, image_prompt, generate
                    )
                    VALUES (
                        :deck_id, :title, :content, :image_prompt, :generate
                    )
                """),
                {
                    "deck_id": deck.id,
                    "title": concept.title,
                    "content": concept.content,
                    "image_prompt": concept.image_prompt,
                    "generate": concept.generate,
                },
            )
        return CardDeck(
            **deck_row,
            concepts=deck.concepts,
        )

    async def delete_deck(self, deck_id: UUID) -> bool:
        result = await self.db.execute(
            text("""
                DELETE FROM card_decks
                WHERE id = :deck_id
                RETURNING id
            """),
            {"deck_id": deck_id},
        )

        return result.scalar_one_or_none() is not None

    async def clear_images(self, deck_id: UUID) -> int:
        """Delete generated image files and clear card image paths."""

        result = await self.db.execute(
            text("""
                SELECT c.id, c.image_path
                FROM cards AS c
                JOIN card_decks AS d ON d.id = c.deck_id
                WHERE d.id = :deck_id
                  AND c.image_path IS NOT NULL
            """),
            {"deck_id": deck_id},
        )
        paths = [Path(row["image_path"]) for row in result.mappings().all()]

        deleted_count = 0

        try:
            for path in set(paths):
                try:
                    await asyncio.to_thread(path.unlink)
                    deleted_count += 1
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    raise RuntimeError(f"Failed to delete image: {path}") from exc

            await self.db.execute(
                text("""
                    UPDATE cards AS c
                    SET image_path = NULL
                    WHERE c.deck_id = :deck_id
                """),
                {"deck_id": deck_id},
            )

            await self.commit()

        except Exception:
            await self.rollback()
            raise

        return deleted_count

    async def update_card_image(self, card_id: UUID, file: UploadFile) -> str:
        """Save a card image under its deck folder and update its path."""

        result = await self.db.execute(
            text("""
                SELECT c.deck_id
                FROM cards AS c
                WHERE c.id = :card_id
            """),
            {"card_id": card_id},
        )

        row = result.mappings().one_or_none()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Memory card not found",
            )

        deck_id = row["deck_id"]

        # Restrict extensions rather than trusting arbitrary filenames.
        suffix = Path(file.filename or "").suffix.lower()
        allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}

        if suffix not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image format",
            )

        deck_dir = self.storage_root / str(deck_id)
        deck_dir.mkdir(parents=True, exist_ok=True)

        image_path = deck_dir / f"{card_id}{suffix}"

        try:
            content = await file.read()

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded image is empty",
                )

            await asyncio.to_thread(image_path.write_bytes, content)

            await self.db.execute(
                text("""
                    UPDATE cards
                    SET image_path = :image_path
                    WHERE id = :card_id
                """),
                {
                    "image_path": str(image_path.resolve()),
                    "card_id": card_id,
                },
            )

            await self.db.commit()

            return str(image_path.resolve())

        except Exception:
            await self.db.rollback()

            # Avoid leaving an unreferenced new file on ordinary failures.
            if image_path.exists():
                await asyncio.to_thread(image_path.unlink)

            raise
        finally:
            await file.close()
