import asyncio

from aibackend.db.base import Base
from aibackend.db.connection import engine
from aibackend.repositories.knowledge import Book, BookChapter, BookChunks, MemoryCard


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
