## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).
## 2024-06-05 - Avoid hidden string allocation overhead in list comprehensions
**Learning:** Python list comprehensions and generator expressions (e.g., `any(c in content.lower() for c in list)`) re-evaluate the target object on every iteration, leading to O(N*M) string allocation overhead if operations like `.lower()` are used.
**Action:** Always pre-compute and cache string transformations into local variables before iterating over them.
## 2024-05-18 - Resolve N+1 query overhead in story auditor
**Learning:** Found an N+1 query issue in `StoryAuditor` where `audit_all_chapters` called `audit_chapter` for every chapter, which in turn queried the database repeatedly for entities, relationships, and events. This caused significant database overhead during full story audits.
**Action:** Always fetch loop-invariant external dependencies outside the loop and pass them in to avoid N+1 queries. Specifically, modified the `audit_chapter` and internal check methods to optionally accept the lists, querying them exactly once in `audit_all_chapters`.
## 2024-05-19 - Add missing indexes to directed graph tables for OR queries
**Learning:** Found a performance bottleneck in `nebula_writer/codex.py` where querying relationships with `WHERE r.from_entity_id = ? OR r.to_entity_id = ?` was causing a full table scan despite having an index on `from_entity_id`.
**Action:** When working with directed graph tables (like relationships) and querying across both directions using an `OR` condition, always ensure both columns are indexed (e.g., `from_entity_id` and `to_entity_id`). This allows SQLite to utilize the `MULTI-INDEX OR` optimization instead of falling back to a full table scan.

## 2024-06-21 - Resolve N+1 query in entity filtering
**Learning:** Found an N+1 query bottleneck in `nebula_writer/search.py` where `filter_entities` retrieved attributes for every entity in a loop to check if they had any attributes (`has_attributes` filter). This scaled poorly as the number of entities grew.
**Action:** Always pre-fetch distinct relationships or existence checks outside of loops. Added a `get_entity_ids_with_attributes` method to `CodexDatabase` that executes a single `SELECT DISTINCT entity_id FROM attributes` query, returning a set of IDs. We check this set in O(1) time within the loop.
