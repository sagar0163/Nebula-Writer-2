## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).

## 2024-05-18 - SQLite `OR` conditions require indexes on all involved columns to avoid full table scans
**Learning:** Found a performance bottleneck in `nebula_writer/codex.py` where `get_relationships` filtered by `WHERE r.from_entity_id = ? OR r.to_entity_id = ?`. Because there was only an index on `from_entity_id`, the `OR` condition forced SQLite to perform a full table scan. Adding an index on `to_entity_id` resolved this issue, taking query time down from ~7.5s to ~0.2s for large datasets.
**Action:** When writing SQL queries with `OR` conditions across multiple columns, ensure that indexes exist for *each* of the columns involved to prevent performance degradations.
