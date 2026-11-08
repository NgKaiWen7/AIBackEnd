import json
import uuid
import warnings
from uuid import UUID
import ollama
import asyncio
import age
import numpy as np
from pydantic import BaseModel, Field
from sklearn.mixture import GaussianMixture
from sqlalchemy.ext.asyncio import AsyncSession
from umap import UMAP
from aibackend.models.chunking import Chunk, Cluster
from aibackend.repositories.book_chunks import BookChunkRepository
from aibackend.services.chunking import ingest_book
from aibackend.utils.embed import get_embedding

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


def select_gmm_by_bic(
    embeddings: np.ndarray, max_components: int = 50
) -> tuple[GaussianMixture, dict[int, float]]:
    n_samples, n_dimensions = embeddings.shape

    if n_samples < 2:
        raise ValueError("At least 2 samples are required.")

    if max_components < 1:
        raise ValueError("max_components must be at least 1.")

    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings contain NaN or infinity.")

    upper_bound = min(max_components, n_samples - 1)

    best_model = None
    best_bic = float("inf")

    bic_scores = {}

    for n_components in range(1, upper_bound + 1):
        model = GaussianMixture(
            n_components=n_components,
            covariance_type="full",
            reg_covar=1e-6,
            n_init=3,
            max_iter=300,
            random_state=224,
        )

        try:
            model.fit(embeddings)

        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            warnings.warn(f"GMM with K={n_components} failed: {exc}", stacklevel=2)
            continue
        if not model.converged_:
            warnings.warn(f"GMM with K={n_components} did not converge.", stacklevel=2)
        bic = float(model.bic(embeddings))
        bic_scores[n_components] = bic
        print(f"GMM components: {n_components:3d} | BIC: {bic:.4f}")
        if bic < best_bic:
            best_bic = bic
            best_model = model
    if best_model is None:
        raise RuntimeError("Unable to fit a valid GMM model.")

    selected_k = best_model.n_components
    if selected_k == upper_bound:
        warnings.warn(
            "The selected K is at the upper search boundary. Consider increasing max_components."
        )
    return best_model, bic_scores


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


def insert_raptor_graph(
    connection, root_clusters: list[Cluster], chunks: list[Chunk], book_id: str
):
    def cypher_string(value):
        return str(value).replace("\\", "\\\\").replace("'", "\\'")

    book_id = cypher_string(book_id)

    # Delete existing book and related graph nodes.
    delete_query = f"""
        MATCH (b:Book {{id: '{book_id}'}})
        OPTIONAL MATCH (b)-[*0..]->(related)
        DETACH DELETE b, related
    """
    connection.execCypher(delete_query)

    # Create Book node.
    create_book_query = f"""
        CREATE (:Book {{
            id: '{book_id}'
        }})
    """
    connection.execCypher(create_book_query)

    stack = []

    for cluster in reversed(root_clusters):
        stack.append((cluster, None))

    while stack:
        cluster, parent_id = stack.pop()

        cluster_id = str(UUID(str(cluster.id)))
        cluster_id = cypher_string(cluster_id)

        # Create the cluster and connect it to its parent.
        if parent_id is None:
            query = f"""
                MATCH (b:Book {{id: '{book_id}'}})
                CREATE (c:Cluster {{
                    id: '{cluster_id}',
                    level: {cluster.level}
                }})
                CREATE (b)-[:CONTAINS]->(c)
            """
        else:
            parent_id = cypher_string(parent_id)

            query = f"""
                MATCH (p:Cluster {{id: '{parent_id}'}})
                CREATE (c:Cluster {{
                    id: '{cluster_id}',
                    level: {cluster.level}
                }})
                CREATE (p)-[:CONTAINS]->(c)
            """

        connection.execCypher(query)

        # Connect leaf clusters to their chunks.
        if not cluster.children:
            for chunk_id in cluster.membership:
                chunk_uuid = cypher_string(chunks[chunk_id].id)

                query = f"""
                    MATCH (c:Cluster {{id: '{cluster_id}'}})
                    MERGE (ch:Chunk {{id: '{chunk_uuid}'}})
                    MERGE (c)-[:SUMMARIZES]->(ch)
                """

                connection.execCypher(query)

        # Process children.
        for child in reversed(cluster.children):
            stack.append((child, cluster_id))


async def raptor_embed(book_id: UUID, db: AsyncSession) -> dict:
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
            await repo.update_embedding(id=chunk.id, embeddings=chunk.embeddings)
    await repo.delete_clusters(book_id)

    # Connect to the graph database
    connection = age.connect(graph=GRAPH_NAME, dsn=DSN)

    # Gather chunks
    embeddings = []
    for chunk in chunks:
        embeddings.append(chunk.embeddings)
    embeddings = np.stack(embeddings)
    # reduced_embeddings = reduce_embeddings(embeddings, n_components=10, n_neighbors=30)
    memberships = gmm_cluster(embeddings, threshold=0.1)

    clusters: list[Cluster] = []
    for membership in memberships:
        chunk_ids = membership.tolist()
        total_length = sum(len(chunks[i].raw_text) for i in membership)
        clusters.append(
            Cluster(
                book_id=book.id,
                membership=chunk_ids,
                total_length=total_length,
                level=0,
            )
        )
    print(f"Initial clusters: {len(clusters)}")
    # Build hierarchical clusters
    root_clusters = clusters
    current_level = root_clusters
    while True:
        next_level: list[Cluster] = []
        for cluster in current_level:
            if cluster.total_length <= 8000:
                continue
            cluster_embeddings = embeddings[cluster.membership]
            sub_memberships = gmm_cluster(
                cluster_embeddings,
                threshold=0.1,
                n_components=min(5, len(cluster.membership)),
            )
            print(f"Cluster {cluster.id} produced {len(sub_memberships)} sub-clusters.")
            children: list[Cluster] = []
            for sub_membership in sub_memberships:
                sub_chunk_ids = []
                for i in sub_membership:
                    sub_chunk_ids.append(cluster.membership[i])
                total_length = 0
                for chunk_id in sub_chunk_ids:
                    total_length += len(chunks[chunk_id].raw_text)
                children.append(
                    Cluster(
                        book_id=book.id,
                        membership=sub_chunk_ids,
                        total_length=total_length,
                        level=cluster.level + 1,
                    )
                )
            if not children:
                raise RuntimeError("Clustering produced no children.")
            cluster.children = children
            next_level.extend(children)
        if not next_level:
            break
        current_level = next_level

    # Ingest clusters into clusters table
    def iter_clusters(cluster: Cluster):
        yield cluster

        for child in cluster.children:
            yield from iter_clusters(child)

    total_clusters = 0
    clusters_by_level: dict[int, int] = {}
    for root in root_clusters:
        for cluster in iter_clusters(root):
            total_clusters += 1
            clusters_by_level[cluster.level] = (
                clusters_by_level.get(cluster.level, 0) + 1
            )
            id = await repo.create_cluster(cluster)
            cluster.id = id
    await repo.commit()
    insert_raptor_graph(
        connection, root_clusters=root_clusters, chunks=chunks, book_id=str(book.id)
    )
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
    pass
