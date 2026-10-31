import hashlib
import logging
from pathlib import Path
from uuid import UUID

import pymupdf4llm
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.models.chunking import Book, Chunk
from aibackend.repositories.book_chunks import BookChunkRepository

logger = logging.getLogger(__name__)


BOOKS_DIR = Path("/mnt/data")


async def create_book_from_upload(
    file: UploadFile,
    db: AsyncSession,
    title: str | None = None,
    category: list[str] | None = None,
    status: str = "Want to Read",
    description: str | None = None,
) -> Book:
    repo = BookChunkRepository(db)

    filename = Path(file.filename or "Untitled").name
    extension = Path(filename).suffix

    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()
    stored_filename = f"{file_hash}{extension}"

    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = BOOKS_DIR / stored_filename

    try:
        file_path.write_bytes(content)

        book = Book(
            title=title or Path(filename).stem,
            category=category or [],
            status=status,
            description=description,
            source=stored_filename,
        )

        created_book = await repo.create_book(book)
        await repo.commit()

        return created_book

    except Exception:
        await repo.rollback()

        if file_path.exists():
            file_path.unlink()

        raise

    finally:
        await file.close()


async def ingest_book(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookChunkRepository(db)

    try:
        book = await repo.get_book(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        pdf_path = BOOKS_DIR / book.source.lstrip("/")
        await repo.delete_chunks(book.id)
        chunks = pymupdf4llm.to_chunks(
            doc=pdf_path, show_progress=True, table_mode="isolate"
        )
        for i, chunk in enumerate(chunks):
            chunk_py = Chunk(
                book_id=book.id,
                position=i,
                raw_text=chunk.text,
                meta_data=" ".join(chunk.metadata.section_path),
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
