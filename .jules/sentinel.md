## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-05-24 - [Fix SQL Injection in Dynamic Queries]
**Vulnerability:** A SQL injection vulnerability existed in `update_story_plan` (in `nebula_writer/codex.py`) due to the direct use of user-supplied dictionary keys to construct dynamic `UPDATE` and `INSERT` clauses.
**Learning:** Constructing raw SQL queries dynamically using untrusted keys as column names circumvents the protection parameterized queries provide for values.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings to prevent injection.
