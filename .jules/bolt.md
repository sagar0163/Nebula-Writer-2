## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).
## 2024-06-03 - Cache transformed strings in loops
**Learning:** Calling `.lower()` inside nested loops over large datasets (like entities and chapter contents) causes O(N*M) processing overhead which is a performance bottleneck specific to how this app handles entity extraction and check consistency.
**Action:** Pre-compute and cache transformed strings (e.g. `.lower()`) outside of iteration loops to prevent repeated string allocations and processing overhead.
