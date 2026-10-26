from uuid import UUID

from ollama import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.repositories.book_chunks import BookChunkRepository

EMBED_MODEL = "bge-m3"

client = AsyncClient()


async def get_embedding(text: str) -> list[float]:
    response = await client.embed(model=EMBED_MODEL, input=text)
    return list(response.embeddings[0])


async def embed(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookChunkRepository(db)

    try:
        chunks = await repo.get_chunks(book_id)
        if len(chunks) == 0:
            raise ValueError(f"book_id: {book_id} not found for book")

        for chunk in chunks:
            embedding = await get_embedding(chunk.raw_text)
            await repo.update_embedding(id=chunk.id, embeddings=embedding)
        await repo.commit()

        return {
            "book_id": book_id,
            "embedded_count": len(chunks),
        }

    except Exception:
        await repo.rollback()
        raise
