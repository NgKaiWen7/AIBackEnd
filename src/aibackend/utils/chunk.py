def chunk_text(
    text: str,
    chunk_size: int = 30000,
    overlap: int = 2000,
) -> list[str]:
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        if end >= len(text):
            break

        start = end - overlap

    return chunks
