from uuid import UUID
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from fastapi import HTTPException, UploadFile
from aibackend.models.chunking import Book, Chunk, Cluster
import json
from pathlib import Path
from aibackend.utils.constant import RAPTOR_CARD_DECKS_DIR


class BookChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def create_book(self, book: Book) -> Book:
        result = await self.db.execute(
            text("""
                INSERT INTO books (
                    id,
                    title,
                    category,
                    status,
                    last_read,
                    description,
                    source,
                    created_at
                )
                VALUES (
                    :id,
                    :title,
                    :category,
                    :status,
                    :last_read,
                    :description,
                    :source,
                    COALESCE(:created_at, NOW())
                )
                RETURNING *
            """),
            {
                "id": book.id,
                "title": book.title,
                "category": book.category,
                "status": book.status,
                "last_read": book.last_read,
                "description": book.description,
                "source": book.source,
                "created_at": book.created_at,
            },
        )

        row = result.mappings().one()
        return Book(**row)

    async def get_book(self, book_id: UUID) -> Book | None:
        result = await self.db.execute(
            text("""
                SELECT *
                FROM books
                WHERE id = :book_id
            """),
            {"book_id": book_id},
        )
        row = result.mappings().one_or_none()
        return Book(**row) if row else None

    async def delete_chunks(self, book_id: UUID) -> None:
        await self.db.execute(
            text("""
                DELETE FROM chunks
                WHERE book_id = :book_id
            """),
            {"book_id": str(book_id)},
        )

    async def delete_clusters(self, book_id: UUID) -> None:
        await self.db.execute(
            text("""
                DELETE FROM chunks
                WHERE book_id = :book_id
                  AND level >= 0
            """),
            {"book_id": str(book_id)},
        )

    async def create_chunk(self, chunk: Chunk) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO chunks (
                    book_id,
                    position,
                    level,
                    raw_text,
                    meta_data,
                    card_path
                )
                VALUES (
                    :book_id,
                    :position,
                    :level,
                    :raw_text,
                    CAST(:meta_data AS jsonb),
                    :card_path
                )
                RETURNING id
            """),
            {
                "book_id": str(chunk.book_id),
                "position": chunk.position,
                "level": chunk.level,
                "raw_text": chunk.raw_text,
                "meta_data": (
                    json.dumps(chunk.meta_data) if chunk.meta_data is not None else None
                ),
                "card_path": chunk.card_path,
            },
        )
        return result.scalar_one()

    async def get_chunks(self, id: UUID) -> list[Chunk]:
        """Get original passages, excluding Raptor summaries."""
        result = await self.db.execute(
            text("""
                SELECT * FROM chunks
                WHERE book_id = :book_id
                  AND level = -1
                ORDER BY position, id
                """),
            {"book_id": id},
        )
        chunks = []
        for row in result.mappings():
            data = dict(row)
            data["embeddings"] = (
                json.loads(data["embeddings"])
                if isinstance(data["embeddings"], str)
                else data["embeddings"]
            )
            chunks.append(Chunk(**data))
        return chunks

    async def update_embedding(self, id: UUID | str, embeddings: list[float]):
        await self.db.execute(
            text("""
                UPDATE chunks SET
                embeddings = :embeddings
                WHERE id = :id
                """),
            {"embeddings": str(embeddings), "id": str(id)},
        )

    async def query(self, embeddings: list[float], book_id):
        query = text("""
            SELECT *
            FROM chunks
            WHERE book_id = :book_id
              AND embeddings IS NOT NULL
              AND raw_text <> ''
            ORDER BY embeddings <=> CAST(:embeddings AS vector) ASC
            LIMIT 5
            """)
        chunks = []
        result = await self.db.execute(
            query, {"embeddings": str(embeddings), "book_id": book_id}
        )
        for row in result.mappings():
            data = dict(row)
            data.pop("embeddings")
            chunks.append(Chunk(**data))
        return chunks

    async def create_cluster(self, cluster: Cluster) -> UUID:
        return await self.create_chunk(
            Chunk(
                book_id=cluster.book_id,
                level=cluster.level,
                raw_text=cluster.summary or "",
            )
        )

    async def update_cluster(self, id: str, summary: str):
        await self.db.execute(
            text("""
                UPDATE chunks
                SET raw_text = :summary, embeddings = NULL
                WHERE id = :id
                  AND level >= 0
            """),
            {"id": id, "summary": summary},
        )

    async def update_chunk_image(self, id: str, file: UploadFile):
        suffix = Path(file.filename or "").suffix.lower()
        allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
        if suffix not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported image format")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded image is empty")
        try:
            result = await self.db.execute(
                text("""
                    SELECT book_id
                    FROM chunks
                    WHERE id = :id
                    FOR UPDATE
                """),
                {"id": id},
            )
            row = result.mappings().one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail="Memory card not found")
            card_path = RAPTOR_CARD_DECKS_DIR / str(row["book_id"]) / f"{id}{suffix}"
            await self.db.execute(
                text("""
                    UPDATE chunks
                    SET card_path = :card_path
                    WHERE id = :id
                """),
                {"id": id, "card_path": str(card_path)},
            )
            card_path.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(card_path.write_bytes, content)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return str(card_path)

    async def get_cluster_leafs(self, book_id: str, level: int) -> dict[str, str]:
        await self.db.execute(text("LOAD 'age';"))
        await self.db.execute(text('SET search_path = ag_catalog, "$user", public;'))
        summary_dict = defaultdict(str)
        query = text(f"""
            SELECT
                (result.source_id::text)::UUID AS cluster_id,
                ch.meta_data AS meta_data,
                ch.raw_text AS content
            FROM cypher('raptor_graph', $$
                MATCH (book:Book {{id: '{book_id}'}})
                    -[*1..]->(c:Cluster {{level:{level}}})
                    -[r]->(d)
                RETURN DISTINCT
                    c.id,
                    d.id
            $$) AS result(
                source_id agtype,
                target_id agtype
            )
            JOIN public.chunks ch
                ON ch.id = (result.target_id::text)::UUID
            WHERE ch.book_id = :book_id
            ORDER BY cluster_id, ch.level, ch.position, ch.id;
            """)
        results = await self.db.execute(query, {"book_id": book_id})
        for i, result in enumerate(results.mappings()):
            context = f"Chunk: {i + 1}"
            if result["meta_data"] is not None:
                context += f"\n{result['meta_data']}"
            context += f"\n{result['content']}"
            summary_dict[result["cluster_id"]] += context + "\n\n"
        return summary_dict

    async def get_largest_cluster_level(self, book_id: str) -> int | None:
        result = await self.db.execute(
            text("""
                SELECT max(level) FROM chunks
                WHERE book_id = :book_id
                  AND level >= 0
            """),
            {"book_id": book_id},
        )
        result = result.one_or_none()
        if result is None:
            return None
        return result[0]

    async def get_chunk_images(self, book_id: UUID) -> list[tuple[UUID, str | None]]:
        results = await self.db.execute(
            text("""
                SELECT id, card_path
                FROM chunks
                WHERE book_id = :book_id
                  AND card_path IS NOT NULL
                ORDER BY level, id
            """),
            {"book_id": book_id},
        )
        return [(row["id"], row["card_path"]) for row in results.mappings()]

    async def get_clusters(self, book_id: str) -> list[tuple[str, str]]:
        results = await self.db.execute(
            text("""
                 SELECT id, raw_text
                 FROM chunks
                 WHERE book_id = :book_id
                   AND level >= 0
                 ORDER BY level, id
                 """),
            {"book_id": book_id},
        )
        results_list = []
        for result in results.mappings():
            if not result["raw_text"]:
                raise ValueError("Cluster summary is empty; run raptor_summarize first")
            results_list.append((result["id"], result["raw_text"]))
        return results_list
