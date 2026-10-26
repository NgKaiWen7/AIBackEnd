import logging
from pathlib import Path
from uuid import UUID

import pymupdf4llm
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.chunking import Chunk
from aibackend.repositories.book_chunks import BookChunkRepository

logger = logging.getLogger(__name__)


async def ingest_book(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookChunkRepository(db)

    try:
        book = await repo.get_book(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        pdf_path = Path("/mnt") / book.source.lstrip("/")
        await repo.delete_chunks(book.id)
        chunks = pymupdf4llm.to_chunks(
            doc=pdf_path,
            show_progress=True,
            table_mode="isolate",
        )
        for i, chunk in enumerate(chunks):
            chunk_py = Chunk(
                book_id=book.id,
                position=i,
                raw_text=chunk.text,
                meta_data=" ".join(chunk.metadata.section_path)
            )
            await repo.create_chunk(chunk_py)

        await repo.commit()
        return {
            "book_id": book_id,
            "chunk_count": len(chunks),
        }

    except Exception:
        await repo.rollback()
        logger.exception("Failed to ingest book %s", book_id)
        raise
