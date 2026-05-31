## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).

## 2024-05-19 - Add missing indexes to directed graph tables for OR queries
**Learning:** Found a performance bottleneck in `nebula_writer/codex.py` where querying relationships with `WHERE r.from_entity_id = ? OR r.to_entity_id = ?` was causing a full table scan despite having an index on `from_entity_id`.
**Action:** When working with directed graph tables (like relationships) and querying across both directions using an `OR` condition, always ensure both columns are indexed (e.g., `from_entity_id` and `to_entity_id`). This allows SQLite to utilize the `MULTI-INDEX OR` optimization instead of falling back to a full table scan.
