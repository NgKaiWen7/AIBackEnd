PROMPT = """
Extract high-quality memory cards from the book chapter.

Book: {book_title}
Chapter: {chapter_title}

Rules:
- Prioritize information relevant to the book's main subject.
- Use only the provided source text. Do not invent information.
- Extract meaningful concepts, definitions, principles, methods, and explanations.
- Each card must test one distinct idea with a clear, specific question and an accurate, self-contained answer.
- Avoid trivial, duplicate, vague, or overlapping cards.
- Prefer fewer valuable cards over many weak ones.
- Keypoints must explain the concept in greater depth, including reasoning, mechanisms, relationships, examples, or implications when supported by the source. Do not merely repeat the answer.
- Return only valid JSON matching the schema. No Markdown or additional text.

Response in provided json format
"""
