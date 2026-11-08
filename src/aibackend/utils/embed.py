from ollama import AsyncClient

EMBED_MODEL = "bge-m3"

client = AsyncClient()


async def get_embedding(text: str) -> list[float]:
    response = await client.embed(model=EMBED_MODEL, input=text)
    return list(response.embeddings[0])
