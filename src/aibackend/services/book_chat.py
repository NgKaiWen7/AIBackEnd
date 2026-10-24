from ollama import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from aibackend.repositories.book_chunks import BookChunkRepository

# Import query from the module containing your existing embedding/retrieval service.
from aibackend.services.embedding import query

SYSTEM_PROMPT = """
You are a book question-answering assistant.

You have access to the following tool:

- search_book(q): Searches the selected book for relevant passages
  using semantic retrieval. The returned passages contain information
  extracted from the book.

Instructions:
1. Use search_book when answering questions about the book's content.
2. Formulate a meaningful search query based on the user's question.
3. Base your answer on the retrieved passages.
4. If the retrieved passages do not contain sufficient information,
   state that the available context is insufficient.
5. Do not invent quotations, facts, or references.
6. After receiving the tool results, synthesize the information into
   a clear and accurate answer.
"""


def tool_factory(
    db: AsyncSession, book_id: str | None = None, chapter_id: str | None = None
):
    async def search_book(q: str):
        return await query(q, db)

    return search_book


async def chat(
    question: str,
    db: AsyncSession,
    book_id: str | None = None,
    chapter_id: str | None = None,
):
    client = AsyncClient()
    repo = BookChunkRepository(db)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if chapter_id and not book_id:
        raise ValueError("book_id is required when chapter_id is provided")
    if book_id:
        book = await repo.get_book_context(book_id=book_id, chapter_id=chapter_id)
        if book is None:
            raise ValueError(f"Book {book_id} not found")
        book_info = f"Book: {book['title']}"
        for chapter in book["chapters"]:
            book_info += f"\n{chapter['title']}"
        messages.append({"role": "user", "content": book_info})
    messages.append({"role": "user", "content": question})
    search_book = tool_factory(db, book_id=book_id, chapter_id=chapter_id)
    tools = [search_book]
    for i in range(5):
        response = await client.chat(
            model="qwen3.5:4b",
            messages=messages,
            think=True,
            tools=tools,
            options={"temperature": 0.5},
        )
        if not response.message.tool_calls:
            return response.message.content
        for tool_call in response.message.tool_calls:
            if tool_call.function.name == "search_book":
                result = await search_book(**tool_call.function.arguments)
            else:
                result = "Unknown tool."
            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_call.function.name,
                    "content": str(result),
                }
            )

    return "Stopped after reaching the tool-call limit."
