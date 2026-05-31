## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2026-05-31 - [SQL Injection via Dynamic Dictionary Keys]
**Vulnerability:** The `update_story_plan` function dynamically interpolated dictionary keys directly into SQL `UPDATE` and `INSERT` clauses without validation, leading to SQL injection risks.
**Learning:** Raw dictionary keys from user inputs or uncontrolled sources should never be directly concatenated into SQL strings.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL queries.
