## 2024-05-18 - Avoid repeated O(N) string processing in iteration loops
**Learning:** Found an inefficiency in `nebula_writer/audit.py` where long chapter text strings were repeatedly lowercased `chapter_content.lower()` inside a large iteration loop over entities and relationships. This created unnecessary and repetitive overhead for an operation that produces an identical output each time.
**Action:** When performing substring searches against a potentially long block of text across an iteration set, lowercase the text once before entering the loop to ensure O(1) text processing overhead instead of O(N).
## 2024-06-05 - Avoid hidden string allocation overhead in list comprehensions
**Learning:** Python list comprehensions and generator expressions (e.g., `any(c in content.lower() for c in list)`) re-evaluate the target object on every iteration, leading to O(N*M) string allocation overhead if operations like `.lower()` are used.
**Action:** Always pre-compute and cache string transformations into local variables before iterating over them.
