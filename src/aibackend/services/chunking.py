import logging
import unicodedata
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.repositories.book_chunks import BookChunkRepository
from aibackend.utils.chunk import chunk_text
from aibackend.utils.pdf import get_chapters

logger = logging.getLogger(__name__)


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    return unicodedata.normalize("NFC", value.replace("\x00", "")).strip()


async def ingest_book(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookChunkRepository(db)

    try:
        book = await repo.get_book(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        pdf_path = Path("/mnt") / book["source"].lstrip("/")
        chapters = get_chapters(pdf_path)

        await repo.delete_chapters(book_id)

        chapter_count = 0
        chunk_count = 0

        for chapter_number, (title, content) in enumerate(chapters.items(), start=1):
            chapter_id = await repo.create_chapter(
                book_id=book_id,
                chapter_number=chapter_number,
                title=normalize_text(title) or "",
            )
            chapter_count += 1

            for position, chunk in enumerate(
                chunk_text(content, chunk_size=1000, overlap=200)
            ):
                await repo.create_chunk(
                    chapter_id=chapter_id,
                    position=position,
                    raw_text=normalize_text(chunk),
                )
                chunk_count += 1

        await repo.commit()

        return {
            "book_id": book_id,
            "chapter_count": chapter_count,
            "chunk_count": chunk_count,
        }

    except Exception:
        await repo.rollback()
        logger.exception("Failed to ingest book %s", book_id)
        raise
