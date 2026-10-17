import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import BookChunks as BookChunks_db
from aibackend.utils.chunk import chunk_text
from aibackend.utils.pdf import get_chapters

logger = logging.getLogger(__name__)


async def ingest_book(book_id: str, db: AsyncSession):
    stmt = (
        select(Book_db)
        .options(selectinload(Book_db.chapters).selectinload(BookChapter_db.chunks))
        .where(Book_db.id == book_id)
    )
    result = await db.execute(stmt)
    book: Book_db = result.scalar_one()
    book.chapters.clear()
    await db.flush()
    pdf_path = Path("/mnt") / book.source.lstrip("/")
    chapters: dict[str, str] = get_chapters(pdf_path)

    for chapter_number, (chapter_title, content) in enumerate(
        chapters.items(), start=1
    ):
        bookchapter_db = BookChapter_db(
            chapter_number=chapter_number, title=chapter_title
        )
        chunks = chunk_text(content, chunk_size=1000, overlap=200)
        for i, chunk in enumerate(chunks):
            bookchunk_db = BookChunks_db(raw_text=chunk, position=i)
            bookchapter_db.chunks.append(bookchunk_db)
        book.chapters.append(bookchapter_db)

    await db.commit()
    await db.refresh(book)

    return {"book_id": book.id}
