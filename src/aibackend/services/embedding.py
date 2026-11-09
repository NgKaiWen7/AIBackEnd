from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.chunking import Chunk
from aibackend.repositories.book_chunks import BookChunkRepository
from aibackend.services.chunking import ingest_book
from aibackend.utils.embed import get_embedding


async def embed(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookChunkRepository(db)

    try:
        chunks: list[Chunk] = await repo.get_chunks(book_id)
        if len(chunks) == 0:
            await ingest_book(book_id, db)

        for chunk in chunks:
            embedding = await get_embedding(chunk.raw_text)
            await repo.update_embedding(id=chunk.id, embeddings=embedding, table='chunks')
        await repo.commit()

        return {"book_id": book_id, "embedded_count": len(chunks)}

    except Exception:
        await repo.rollback()
        raise
