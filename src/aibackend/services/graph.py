import age
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from LLMGraphTransformer import LLMGraphTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aibackend.repositories.knowledge import Book as Book_db
from aibackend.repositories.knowledge import BookChapter as BookChapter_db
from aibackend.repositories.knowledge import BookChunks as BookChunks_db
from aibackend.repositories.knowledge import MemoryCard as MemoryCard_db


async def insert_relations(db, relations: list):
    if not relations:
        return 0

    for relation in relations:
        query = f"""
            MERGE (p:{relation.source.type} {{
                id: "{relation.source.id}"
            }})
            ON CREATE SET
                p.type = "{relation.source.type}",
                p.properties = "{relation.source.properties}"

            MERGE (t:{relation.target.type} {{
                id: "{relation.target.id}"
            }})
            ON CREATE SET
                t.type = "{relation.target.type}",
                t.properties = "{relation.target.properties}"

            MERGE (p)-[r:{relation.type}]->(t)
        """

        if relation.properties:
            query += f"\nSET r += {relation.properties}"

        print(query)
        db.execCypher(query)

    db.commit()
    return len(relations)


async def graph(book_id: str, db: AsyncSession):
    connection = age.connect(
        graph="knowledge_graph",
        dsn=(
            "host=localhost port=5432 dbname=knowledge_db "
            "user=postgres password=postgres"
        ),
    )
    stmt = (
        select(Book_db)
        .options(
            selectinload(Book_db.chapters)
            .selectinload(BookChapter_db.chunks)
            .selectinload(BookChunks_db.memory_cards)
        )
        .where(Book_db.id == book_id)
    )
    book = await db.scalar(stmt)

    if book is None:
        connection.close()
        raise ValueError(f"Book {book_id} not found")

    llm = ChatOllama(
        model="qwen3.5:9b",
        reasoning=False,
        temperature=0,
    )

    transformer = LLMGraphTransformer(llm=llm)

    for chapter in book.chapters:
        for chunk in chapter.chunks:
            try:
                document = Document(page_content=chunk.raw_text)

                graph_documents = transformer.convert_to_graph_documents([document])

                for graph_document in graph_documents:
                    print(graph_document)
                    await insert_relations(connection, graph_document.relationships)
            except Exception:
                logger.exception("Failed to ingest chunk")
