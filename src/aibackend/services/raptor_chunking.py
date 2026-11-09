import warnings
from uuid import UUID
import ollama
import asyncio
from collections import defaultdict
from sqlalchemy import text
import age
import numpy as np
from sklearn.mixture import GaussianMixture
from sqlalchemy.ext.asyncio import AsyncSession
from umap import UMAP
import httpx
from aibackend.models.chunking import Chunk, Cluster
from aibackend.repositories.book_chunks import BookChunkRepository
from aibackend.services.chunking import ingest_book
from aibackend.utils.embed import get_embedding
from aibackend.models.memory_cards import PromptDomain, CardStyle, STYLE_PROMPTS, SYSTEM_PROMPTS, CardDeck
from aibackend.utils.constant import (
    CARD_DECKS_DIR,
    CARD_DECKS_EXPORT_DIR,
    COMPUTE_SERVER_URL,
)

DSN = "host=localhost port=5433 dbname=knowledge_db user=postgres password=postgres"
GRAPH_NAME = "raptor_graph"


def reduce_embeddings(
    embeddings: np.ndarray, n_components: int = 10, n_neighbors: int = 30
) -> np.ndarray:
    n_samples = embeddings.shape[0]
    if n_samples < 4:
        raise ValueError("UMAP requires at least 4 samples.")
    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings contain NaN or infinity.")
    reducer = UMAP(
        n_neighbors=min(n_neighbors, n_samples - 1),
        n_components=min(n_components, n_samples - 2),
        metric="cosine",
        min_dist=0.0,
        random_state=224,
        n_jobs=1,
    )
    reduced_embeddings = reducer.fit_transform(embeddings)
    return reduced_embeddings.astype(np.float32)


def gmm_cluster(
    embeddings: np.ndarray,
    threshold: float = 0.1,
    n_components: int = 5,
) -> list[np.ndarray]:

    if not 0 < threshold <= 1:
        raise ValueError("threshold must be between 0 and 1.")

    if len(embeddings) < n_components:
        raise ValueError("Number of samples must be >= n_components.")

    model = GaussianMixture(
        n_components=n_components,
        covariance_type="full",
        reg_covar=1e-6,
        n_init=3,
        max_iter=300,
        random_state=224,
    )

    model.fit(embeddings)
    probabilities = model.predict_proba(embeddings)

    # Soft cluster assignment.
    assignments = probabilities > threshold

    # Ensure every chunk belongs to at least one cluster.
    for i in range(len(assignments)):
        if not assignments[i].any():
            best_cluster = np.argmax(probabilities[i])
            assignments[i, best_cluster] = True

    memberships = []

    for cluster_id in range(n_components):
        chunk_indices = np.flatnonzero(assignments[:, cluster_id])

        if len(chunk_indices) > 0:
            memberships.append(chunk_indices)

    return memberships


async def raptor_clustering(book_id: UUID, db: AsyncSession) -> dict:
    repo = BookChunkRepository(db)
    book = await repo.get_book(book_id)
    if book is None:
        raise ValueError(f"Book not found: {book_id}")
    chunks: list[Chunk] = await repo.get_chunks(book_id)
    if len(chunks) == 0:
        await ingest_book(book_id, db)

    for chunk in chunks:
        if chunk.embeddings is None:
            chunk.embeddings = await get_embedding(chunk.raw_text)
            await repo.update_embedding(
                id=chunk.id, embeddings=chunk.embeddings, table="chunks"
            )
    await repo.delete_clusters(book_id)

    # Connect to the graph database
    connection = age.connect(graph=GRAPH_NAME, dsn=DSN)

    # Delete existing book and related graph nodes.
    delete_query = f"""
        MATCH (b:Book {{id: '{book_id}'}})
        OPTIONAL MATCH (b)-[*0..]->(related)
        DETACH DELETE b, related
    """
    connection.execCypher(delete_query)

    # Create Book node.
    create_book_query = f"""
        CREATE (:Book {{id: '{book_id}'}})
    """
    connection.execCypher(create_book_query)

    # Gather chunks
    embeddings = []
    for chunk in chunks:
        embeddings.append(chunk.embeddings)
    embeddings = np.stack(embeddings)
    embeddings = reduce_embeddings(embeddings, n_components=100, n_neighbors=30)
    memberships = gmm_cluster(embeddings, threshold=0.1)

    clusters: list[Cluster] = []
    for membership in memberships:
        chunk_ids = membership.tolist()
        total_length = sum(len(chunks[i].raw_text) for i in membership)
        cluster = Cluster(
            book_id=book.id,
            parent_id=book.id,
            membership=chunk_ids,
            total_length=total_length,
            level=0,
        )
        clusters.append(cluster)

    print(f"Initial clusters: {len(clusters)}")
    # Build hierarchical clusters
    root_clusters = clusters
    current_level = root_clusters
    total_clusters = len(root_clusters)
    clusters_by_level: dict[int, int] = defaultdict(int)
    while True:
        next_level: list[Cluster] = []
        for parent_cluster in current_level:
            total_clusters += 1
            clusters_by_level[parent_cluster.level] += 1
            parent_cluster.id = await repo.create_cluster(parent_cluster)
            query = f"""
                MATCH (p:{'Book' if parent_cluster.level == 0 else 'Cluster'}
                 {{id: '{parent_cluster.parent_id}'}})
                CREATE (c:Cluster {{
                    id: '{parent_cluster.id}',
                    level: {parent_cluster.level}
                }})
                CREATE (p)-[:CONTAINS]->(c)
            """
            connection.execCypher(query)
            if parent_cluster.total_length <= 8000:
                for child in parent_cluster.membership:
                    query = f"""
                        MATCH (p:Cluster
                        {{id: '{parent_cluster.id}'}})
                        CREATE (c:Chunk {{
                            id: '{chunks[child].id}'
                        }})
                        CREATE (p)-[:SUMMARIZES]->(c)
                    """
                    connection.execCypher(query)
                continue
            cluster_embeddings = embeddings[parent_cluster.membership]
            sub_memberships = gmm_cluster(
                cluster_embeddings,
                threshold=0.1,
                n_components=min(5, len(parent_cluster.membership)),
            )
            print(
                f"Cluster {parent_cluster.id} produced {len(sub_memberships)} sub-clusters in level {parent_cluster.level}"
            )
            children: list[Cluster] = []
            for sub_membership in sub_memberships:
                sub_chunk_ids = []
                for i in sub_membership:
                    sub_chunk_ids.append(parent_cluster.membership[i])
                total_length = 0
                for chunk_id in sub_chunk_ids:
                    total_length += len(chunks[chunk_id].raw_text)
                cluster = Cluster(
                    book_id=book.id,
                    parent_id=parent_cluster.id,
                    membership=sub_chunk_ids,
                    total_length=total_length,
                    level=parent_cluster.level + 1,
                )
                print(cluster)
                children.append(cluster)
            if not children:
                raise RuntimeError("Clustering produced no children.")
            next_level.extend(children)

        if not next_level:
            break
        current_level = next_level

    await repo.commit()
    connection.commit()
    return {
        "book_id": str(book.id),
        "total_chunks": len(chunks),
        "total_clusters": total_clusters,
        "total_levels": len(clusters_by_level),
        "root_clusters": len(root_clusters),
        "clusters_by_level": clusters_by_level,
        "status": "completed",
    }


async def raptor_summarize(book_id: UUID, db: AsyncSession):
    SYSTEM_PROMPT = """
    Summarize the text below, keep the main idea and keep the summary short
    """.strip()
    # First step is to gather the chunks
    repo = BookChunkRepository(db)
    await db.execute(text("LOAD 'age';"))
    await db.execute(text('SET search_path = ag_catalog, "$user", public;'))
    max_level = await repo.get_largest_cluster_level(str(book_id))
    if max_level is None:
        raise ValueError("Unable to get any cluster levels")
    level = max_level
    while level >= 0:
        summaries = await repo.get_cluster_leafs(str(book_id), level)
        for id, context in summaries.items():
            response = await ollama.AsyncClient().chat(
                model="qwen3.5:4b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                think=False,
                options={"temperature": 0.5},
            )
            if response.message.content is None:
                print("Failed to generate summary")
                continue
            summary = response.message.content
            await repo.update_cluster(id, summary)
        level -= 1
    await repo.commit()


async def raptor_embedding(book_id: UUID, db: AsyncSession):
    repo = BookChunkRepository(db)
    clusters = await repo.get_clusters(str(book_id))
    for id, summary in clusters:
        embedding = await get_embedding(summary)
        await repo.update_embedding(id=id, embeddings=embedding, table="clusters")
    await repo.commit()


async def raptor_memory_cards(
    book_id: UUID, style: CardStyle, domain: PromptDomain, db: AsyncSession
):
    bookchunk_repo = BookChunkRepository(db)
    book = await bookchunk_repo.get_book(book_id)
    if book is None:
        raise ValueError(f"Book id: {book_id} not found")
    clusters = await bookchunk_repo.get_clusters(str(book_id))
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = []
        for id, summary in clusters:
            prompt = f"""
            CARD STYLE
            {STYLE_PROMPTS[style]}

            CARD DOMAIN
            {SYSTEM_PROMPTS[domain]}
            
            OUTPUT REQUIREMENTS
            Generate a single, complete learning-card image that fills the
            entire canvas edge to edge, with no external background, outer margins,
            mockups, paper textures, or shadows. Keep all content inside the card,
            preserving technical accuracy, readability,
            and the visual style specified in the image prompt.
            Visualize the card content below:
            {summary}
            """.strip()
            payload.append({"id": str(id), "prompt": prompt})
        response = await client.post(
            f"{COMPUTE_SERVER_URL}/generate",
            json=payload,
        )
        response.raise_for_status()
