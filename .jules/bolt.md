## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).

## 2024-05-18 - Resolve N+1 query overhead in story auditor
**Learning:** Found an N+1 query issue in `StoryAuditor` where `audit_all_chapters` called `audit_chapter` for every chapter, which in turn queried the database repeatedly for entities, relationships, and events. This caused significant database overhead during full story audits.
**Action:** Always fetch loop-invariant external dependencies outside the loop and pass them in to avoid N+1 queries. Specifically, modified the `audit_chapter` and internal check methods to optionally accept the lists, querying them exactly once in `audit_all_chapters`.
