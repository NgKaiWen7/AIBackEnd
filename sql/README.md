# Database schema

`schema.sql` bootstraps all relational tables used by the repositories:

- `study_source`
- `chunks`
- `card_decks`
- `cards`

Run it against a new PostgreSQL database with the `pgvector` extension
installed:

```bash
psql -d knowledge_db -f sql/schema.sql
```

`create_chunks_lexical_index.sql` remains available as a focused script for
databases created before this consolidated schema.

To remove the previously introduced standalone `memory_card` table and enable
the chunk image queue on an existing database, run:

```bash
psql -d knowledge_db -f sql/remove_memory_card.sql
```
