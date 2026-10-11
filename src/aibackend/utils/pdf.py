from pathlib import Path

import pymupdf


def get_chapters(pdf_path: str | Path) -> dict[str, str]:
    doc = pymupdf.open(pdf_path)
    toc = doc.get_toc()

    if not toc:
        doc.close()
        return {}

    chapters = {}
    top_level = [(title.strip(), page) for level, title, page in toc if level == 1]

    for i, (title, start_page) in enumerate(top_level):
        end_page = top_level[i + 1][1] if i + 1 < len(top_level) else len(doc) + 1

        text = "\n".join(doc[p - 1].get_text() for p in range(start_page, end_page))

        chapters[title] = text

    doc.close()
    return chapters


def get_title(pdf_bytes: bytes) -> str:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        metadata = doc.metadata
        return metadata.get("title") or ""
