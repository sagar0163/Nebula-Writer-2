## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2026-05-25 - [Prevent SQL Injection via Dynamic Column Interpolation]
**Vulnerability:** The `update_story_plan` function in `nebula_writer/codex.py` dynamically constructed raw SQL `INSERT` and `UPDATE` statements using unfiltered dictionary keys as column names. This could allow SQL injection if untrusted keys were passed to the function.
**Learning:** When generating dynamic SQL strings without an ORM, always validate and filter dynamic column names (e.g. dictionary keys) against an explicit allowlist before interpolating them into the SQL string to avoid injection vulnerabilities.
**Prevention:** Create an `allowed_columns` set with valid database column names and filter any dynamic dictionaries containing column names (like the `plan` dictionary) against it before using them to construct raw SQL `SET` or `INSERT` clauses.
