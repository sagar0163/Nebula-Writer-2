## 2024-05-18 - Dictionary Key Interpolation SQL Injection
**Vulnerability:** Found dictionary keys being unsafely interpolated into dynamic `INSERT` and `UPDATE` SQL queries without validation in `update_story_plan` inside `nebula_writer/codex.py`.
**Learning:** This specific codebase doesn't use an ORM for the backend, relying on raw SQL strings. Using dict keys directly from method signatures (`plan.keys()`) creates a pathway for attackers to pass arbitrary strings that get executed as part of the statement if input keys are not sanitized or mapped to known valid columns.
**Prevention:** Always use an explicit allowlist of expected and valid database columns to filter input dictionaries before string interpolation into SQL query clauses (e.g., `SET` or `INSERT INTO`).
