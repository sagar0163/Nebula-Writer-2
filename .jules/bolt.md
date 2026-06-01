## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).

## 2024-05-18 - Repeated O(N) string processing in run_consistency_check
**Learning:** Found the same inefficiency in `nebula_writer/codex.py` within the `run_consistency_check` method, where chapter contents were lowercased inside a loop iterating over all entities.
**Action:** Pre-compute the lowercased chapter content before the entity loop.
