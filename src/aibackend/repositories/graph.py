import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def age_query(db: AsyncSession, query: str, params: dict):
    await db.execute(text("LOAD 'age'"))
    await db.execute(
        text('SET search_path = ag_catalog, "$user", public')
    )

    result = await db.execute(
        text("""
            SELECT *
            FROM ag_catalog.cypher(
                :graph,
                :query,
                :params
            ) AS (result ag_catalog.agtype)
        """),
        {
            "graph": "knowledge_graph",
            "query": query,
            "params": json.dumps(params),
        },
    )
    return result.fetchall()
