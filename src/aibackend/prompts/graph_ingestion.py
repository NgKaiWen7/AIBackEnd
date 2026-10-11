PROMPT = """
Extract technical knowledge from the supplied text.

Identify important concepts and meaningful relationships between them.

Rules:
- Extract only information supported by the text.
- Each relation must connect two extracted entities.
- Every relation must include an exact supporting quotation.
- Do not use outside knowledge.
- Use concise, consistent entity names.
- Return empty arrays when no useful knowledge is present.
"""
