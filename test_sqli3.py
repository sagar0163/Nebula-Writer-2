from nebula_writer.codex import CodexDatabase

db = CodexDatabase(":memory:")
db.update_entity(1, **{"invalid_col = 1; DROP TABLE entities; --": "bobby tables"})
