## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).
## 2025-02-28 - Optimizing string processing loops
**Learning:** Found an O(N*M) performance bottleneck in `nebula_writer/codex.py` where large strings (chapter content) were being converted to lowercase for each entity in the database.
**Action:** When searching for entities in chapter texts, pre-compute `.lower()` values outside of iteration loops to significantly reduce CPU overhead.
