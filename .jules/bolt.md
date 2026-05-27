## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).

## 2024-05-27 - Optimize repeated string lowering in nested loops
**Learning:** Similar to the optimization in `audit.py`, `run_consistency_check` inside `nebula_writer/codex.py` had an O(N*M) inefficiency where chapter content was being converted to lowercase multiple times inside a nested loop over entities and chapters.
**Action:** Extract text preprocessing (like lowercasing) out of nested loops and cache the result. In this case, pre-calculating a list of lowercased chapter contents before the entities loop reduces the string processing time complexity to O(M).
