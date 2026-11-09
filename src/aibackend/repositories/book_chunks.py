from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict

from aibackend.models.chunking import Book, Chunk, Cluster
import json


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
                DELETE FROM clusters
                WHERE book_id = :book_id
            """),
            {"book_id": str(book_id)},
        )

    async def create_chunk(self, chunk: Chunk) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO chunks (
                    book_id,
                    position,
                    raw_text,
                    meta_data
                )
                VALUES (
                    :book_id,
                    :position,
                    :raw_text,
                    :meta_data
                )
                RETURNING id
            """),
            {
                "book_id": str(chunk.book_id),
                "position": chunk.position,
                "raw_text": chunk.raw_text,
                "meta_data": chunk.meta_data,
            },
        )
        return result.scalar_one()

    async def get_chunks(self, id: UUID) -> list[Chunk]:
        result = await self.db.execute(
            text("""
                SELECT * FROM chunks
                WHERE book_id = :book_id
                """),
            {"book_id": id},
        )
        chunks = []
        for row in result.mappings():
            data = dict(row)
            data["embeddings"] = (
                json.loads(data["embeddings"])
                if data["embeddings"] is not None
                else None
            )
            chunks.append(Chunk(**data))
        return chunks

    async def update_embedding(self, id: UUID, embeddings: list[float], table: str):
        await self.db.execute(
            text(f"""
                UPDATE {table} SET
                embeddings = :embeddings
                WHERE id = :id
                """),
            {"embeddings": str(embeddings), "id": id},
        )

    async def query(self, embeddings: list[float], book_id):
        query = text("""
            SELECT *
            FROM chunks ORDER BY embeddings <=> CAST(:embeddings AS vector) ASC
            LIMIT 5
            """)
        chunks = []
        result = await self.db.execute(query, {"embeddings": str(embeddings)})
        for row in result.mappings():
            data = dict(row)
            data.pop("embeddings")
            chunks.append(Chunk(**data))
        return chunks

    async def create_cluster(self, cluster: Cluster) -> UUID:
        result = await self.db.execute(
            text("""
                INSERT INTO clusters (book_id, level)
                VALUES (:book_id, :level)
                RETURNING id
            """),
            {
                "book_id": str(cluster.book_id),
                "level": cluster.level,
            },
        )
        return result.scalar_one()

    async def update_cluster(self, id: str, summary: str):
        await self.db.execute(
            text("""
                UPDATE clusters
                SET summary = :summary
                WHERE id = :id
            """),
            {"id": id, "summary": summary},
        )

    async def get_cluster_leafs(self, book_id: str, level: int) -> dict[str, str]:
        await self.db.execute(text("LOAD 'age';"))
        await self.db.execute(text('SET search_path = ag_catalog, "$user", public;'))
        summary_dict = defaultdict(str)
        query = text(f"""
            SELECT
                (result.source_id::text)::UUID AS cluster_id,
                ch.meta_data AS meta_data,
                COALESCE(cl.summary, ch.raw_text) AS content
            FROM cypher('raptor_graph', $$
                MATCH (book:Book {{id: '{book_id}'}})
                    -[*1..]->(c:Cluster {{level:{level}}})
                    -[r]->(d)
                RETURN
                    c.id,
                    c.level,
                    label(r),
                    d.id,
                    label(d),
                    d.level
            $$) AS result(
                source_id agtype,
                source_level agtype,
                relationship_label agtype,
                target_id agtype,
                target_label agtype,
                target_level agtype
            )
            LEFT JOIN clusters cl
                ON result.target_label::text = 'Cluster'
                AND cl.id = (result.target_id::text)::UUID
            LEFT JOIN chunks ch
                ON result.target_label::text = 'Chunk'
                AND ch.id = (result.target_id::text)::UUID;
            """)
        results = await self.db.execute(query)
        for i, result in enumerate(results.mappings()):
            context = f"Chunk: {i + 1}"
            if result['meta_data'] is not None:
                context += f"\n{result['meta_data']}"
            context += f"\n{result['content']}"
            summary_dict[result["cluster_id"]] += context
        return summary_dict

    async def get_largest_cluster_level(self, book_id: str) -> int | None:
        result = await self.db.execute(
            text("""
                SELECT max(level) FROM clusters
                WHERE book_id = :book_id
            """),
            {"book_id": book_id},
        )
        result = result.one_or_none()
        if result is None:
            return None
        return result[0]

    async def get_clusters(self, book_id: str) -> list[tuple[str, str]]:
        results = await self.db.execute(
            text("""
                 SELECT id, summary
                 FROM clusters
                 WHERE book_id = :book_id
                 """),
            {"book_id": book_id},
        )
        results_list = []
        for result in results.mappings():
            if result["summary"] is None:
                raise ValueError("Summary contains null value")
            results_list.append((result["id"], result["summary"]))
        return results_list
