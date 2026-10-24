from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MemoryCardImagePromptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, topic: str, title: str, prompt: str) -> dict[str, Any]:
        result = await self.db.execute(
            text("""
                INSERT INTO memory_card_prompts (
                    id,
                    topic,
                    title,
                    prompt
                )
                VALUES (
                    :id,
                    :topic,
                    :title,
                    :prompt
                )
                RETURNING id, topic, title, prompt, created_at
            """),
            {
                "id": uuid4(),
                "topic": topic,
                "title": title,
                "prompt": prompt,
            },
        )

        return dict(result.mappings().one())

    async def create_many(self, records: list[dict[str, str]]) -> list[dict[str, Any]]:
        if not records:
            return []

        values = []
        params: dict[str, Any] = {}

        for i, record in enumerate(records):
            values.append(f"(:id_{i}, :topic_{i}, :title_{i}, :prompt_{i})")
            params.update(
                {
                    f"id_{i}": uuid4(),
                    f"topic_{i}": record["topic"],
                    f"title_{i}": record["title"],
                    f"prompt_{i}": record["prompt"],
                }
            )

        stmt = text(f"""
            INSERT INTO memory_card_prompts (
                id,
                topic,
                title,
                prompt
            )
            VALUES {", ".join(values)}
            RETURNING id, topic, title, prompt, created_at
        """)

        result = await self.db.execute(stmt, params)
        return [dict(row) for row in result.mappings().all()]

    async def get_by_topic(self, topic: str) -> list[dict[str, Any]]:
        result = await self.db.execute(
            text("""
                SELECT id, topic, title, prompt, created_at
                FROM memory_card_prompts
                WHERE topic = :topic
                ORDER BY created_at, title
            """),
            {"topic": topic},
        )

        return [dict(row) for row in result.mappings().all()]

    async def delete_by_title(self, title: str) -> int:
        result = await self.db.execute(
            text("""
                DELETE FROM memory_card_prompts
                WHERE title = :title
            """),
            {"title": title},
        )

        return result.rowcount or 0
