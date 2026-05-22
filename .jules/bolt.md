## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).
## 2024-05-22 - SQLite Multi-Index OR Optimization
**Learning:** In the SQLite database (Codex), `get_relationships` filters using an `OR` condition on two foreign keys (`from_entity_id = ? OR to_entity_id = ?`). SQLite requires both columns to be indexed to use the efficient "Multi-Index OR" strategy. Otherwise, it falls back to a full table scan.
**Action:** Always ensure that both columns involved in an `OR` condition are individually indexed when using SQLite to avoid full table scans.
