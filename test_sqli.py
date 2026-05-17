from nebula_writer.codex import CodexDatabase

db = CodexDatabase(":memory:")
db.update_story_plan({
    "target_ending": "They all die",
    "invalid_col = 1; DROP TABLE story_plan; --": "bobby tables"
})
