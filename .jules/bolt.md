## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).

## 2024-05-19 - Pre-computing data before nested loops for substring search
**Learning:** Found an inefficiency in `nebula_writer/codex.py` within `run_consistency_check` where chapter text strings were repeatedly lowercased `chapter.get("content").lower()` and entity names were also repeatedly lowercased inside a nested iteration loop of chapters over entities. This created unnecessary overhead of string creations and allocations O(N*M) where N is entities and M is chapters.
**Action:** When performing substring searches against a potentially long block of text across nested iteration sets, pre-compute the target strings into optimal lowercased forms (or hashed collections if exact match) outside the nested loop to ensure better runtime performance and to reduce overhead.
