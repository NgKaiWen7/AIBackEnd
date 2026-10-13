ENTITY_PROMPT = """
Extract important technical entities from the supplied text for a knowledge graph.

Rules:
- Prioritize important concepts, systems, components, algorithms, and technologies.
- Ignore generic terms, minor details, and incidental examples.
- Use concise, canonical entity names.
- Assign each entity exactly one type from the allowed types: Concept, System, Component, Algorithm, Technology, DataStructure, Resource, Task.
- Do not create duplicate entities or synonyms.
- Use only information explicitly supported by the text.
- Return an empty array if no useful entities are found.
"""

RELATION_PROMPT = """
Extract semantic relationships between the supplied entities using only the source text.

Rules:
- Both `subject` and `object` must exactly match entity names in the provided entity list.
- Never use entity types such as `Concept`, `System`, `Component`, `Algorithm`, or `DataStructure` as relationship endpoints unless they are explicitly listed as entities.
- Do not create relationships from an entity to its entity type.
- Use `IS_A` only for genuine semantic relationships between entities.
- Extract only relationships supported by the source text.
- If no valid relationships exist, return an empty list.
- Keep evidence short and quote or closely follow the source text.
"""
