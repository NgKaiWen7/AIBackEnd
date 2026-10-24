import asyncio
from uuid import UUID

from ollama import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.repositories.book_embedding_repository import BookEmbeddingRepository

EMBED_MODEL = "bge-m3"

client = AsyncClient()

async def get_embedding(text: str) -> list[float]:
    response = await client.embed(model=EMBED_MODEL, input=text)
    return response.embeddings[0]


async def embed(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookEmbeddingRepository(db)

    try:
        chunks = await repo.get_chunks_for_embedding(book_id)
        embedded_count = 0

        for chunk in chunks:
            embedding = await get_embedding(chunk["raw_text"])

            await repo.update_embedding(
                chunk_id=chunk["id"],
                embedding=embedding,
            )
            embedded_count += 1

        await repo.commit()

        return {
            "book_id": book_id,
            "embedded_count": embedded_count,
        }

    except Exception:
        await repo.rollback()
        raise


def rerank(query: str, documents: list[str]) -> list[tuple[int, float]]:
    if not documents:
        return []

    pairs = [[query, document] for document in documents]
    scores = RERANKER.compute_score(pairs, normalize=True)

    if isinstance(scores, (int, float)):
        scores = [scores]

    return sorted(
        enumerate(scores),
        key=lambda item: item[1],
        reverse=True,
    )


async def query(
    query: str, db: AsyncSession, top_k: int = 5, candidates: int = 50
) -> list[dict]:
    repo = BookEmbeddingRepository(db)

    embedding = await get_embedding(query)
    chunks = await repo.search_chunks(
        embedding=embedding,
        candidates=candidates,
    )

    scores = await asyncio.to_thread(
        rerank,
        query,
        [chunk["raw_text"] for chunk in chunks],
    )

    return [
        {
            "chunk_id": chunks[index]["id"],
            "chunk": chunks[index]["raw_text"],
            "score": float(score),
        }
        for index, score in scores[:top_k]
    ]
