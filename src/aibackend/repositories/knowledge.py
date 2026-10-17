import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aibackend.db.base import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=True)
    category: Mapped[list[str]] = mapped_column(
        ARRAY(String), server_default="{}", nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), server_default="Want to Read", nullable=True
    )
    last_read: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    chapters: Mapped[list["BookChapter"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
        order_by="BookChapter.chapter_number",
    )


class BookChapter(Base):
    __tablename__ = "book_chapters"
    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "chapter_number",
            name="uq_book_chapters_book_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), index=True
    )
    chapter_number: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column(String(500))

    book: Mapped["Book"] = relationship(back_populates="chapters")
    chunks: Mapped[list["BookChunks"]] = relationship(
        back_populates="chapters",
        cascade="all, delete-orphan",
        order_by="BookChunks.position",
    )


class BookChunks(Base):
    __tablename__ = "book_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("book_chapters.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    raw_text: Mapped[Text] = mapped_column(Text, nullable=True)
    embeddings: Mapped[list[float] | None] = mapped_column(Vector(4096), nullable=True)
    chapters: Mapped["BookChapter"] = relationship(back_populates="chunks")
    memory_cards: Mapped[list["MemoryCard"]] = relationship(
        back_populates="chunks", cascade="all, delete-orphan"
    )


class MemoryCard(Base):
    __tablename__ = "memory_cards"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    chunk_id: Mapped[int] = mapped_column(
        ForeignKey("book_chunks.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    keypoint: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    chunks: Mapped["BookChunks"] = relationship(back_populates="memory_cards")
