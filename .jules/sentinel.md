## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-05-24 - [Fix Dynamic SQL Injection via Dictionary Keys]
**Vulnerability:** In `nebula_writer/codex.py`, the `update_story_plan` method accepted a dictionary and dynamically constructed `UPDATE` and `INSERT` clauses using the dictionary's keys without validation. This allowed an attacker to inject arbitrary column names or SQL fragments.
**Learning:** Even when using parameterized queries (e.g., `?` or `%s`) for values, if table names or column names are dynamically constructed from unvalidated inputs, SQL injection is still possible.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings (such as `SET` or `INSERT` clauses) to prevent SQL injection vulnerabilities.
