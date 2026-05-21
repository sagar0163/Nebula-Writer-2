## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-05-24 - [Fix SQL Injection in Dynamic Queries]
**Vulnerability:** The `update_story_plan` method in `nebula_writer/codex.py` dynamically interpolated dictionary keys directly into SQL `INSERT` and `UPDATE` statements without input validation or an allowlist, exposing a SQL injection vulnerability.
**Learning:** Using raw, unfiltered dictionary keys for dynamic SQL clauses (like `SET` or columns in `INSERT`) allows arbitrary columns or SQL syntax to be executed if user input is embedded in those dictionary keys.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of known column names before interpolating them into SQL strings to prevent SQL injection.
