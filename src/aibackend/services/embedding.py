import asyncio

from FlagEmbedding import FlagReranker
from ollama import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import BookChunks as BookChunks_db

EMBED_MODEL = "bge-m3"

client = AsyncClient()

RERANKER = FlagReranker("./models/bge-reranker-v2-m3", use_fp16=True)


async def get_embedding(text: str) -> list[float]:
    response = await client.embed(model=EMBED_MODEL, input=text)
    return response.embeddings[0]


async def embed(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(
            selectinload(Book_db.chapters)
            .selectinload(BookChapter_db.chunks)
            .selectinload(BookChunks_db.memory_cards)
        )
        .where(Book_db.id == book_id)
    )

    result = await db.execute(stmt)
    book: Book_db = result.scalar_one()

    for chapter in book.chapters:
        for chunk in chapter.chunks:
            chunk.embeddings = await get_embedding(chunk.raw_text)

    await db.commit()


def rerank(query: str, documents: list[str]) -> list[tuple[int, float]]:
    if not documents:
        return []
    pairs = [[query, document] for document in documents]
    scores = RERANKER.compute_score(pairs, normalize=True)
    if isinstance(scores, (int, float)):
        scores = [scores]
    return sorted(enumerate(scores), key=lambda item: item[1], reverse=True)


async def query(query: str, db: AsyncSession, top_k: int = 5, candidates: int = 50):
    embedding = await get_embedding(query)
    distance = BookChunks_db.embeddings.cosine_distance(embedding)
    stmt = (
        select(BookChunks_db)
        .where(BookChunks_db.embeddings.is_not(None))
        .order_by(distance)
        .limit(candidates)
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()

    # Run the CPU/GPU inference outside the async event loop.
    scores = await asyncio.to_thread(
        rerank,
        query,
        [chunk.raw_text for chunk in chunks],
    )
    return [
        {
            "chunk": chunks[index].raw_text,
            "score": score,
        }
        for index, score in scores[:top_k]
    ]
