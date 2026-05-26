## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-05-28 - [CRITICAL] SQL Injection via Unfiltered Dictionary Keys
**Vulnerability:** The `update_story_plan` method in `nebula_writer/codex.py` dynamically constructed SQL queries (`UPDATE` and `INSERT`) using keys directly from a user-provided dictionary without any validation or filtering, allowing for arbitrary column modification or SQL injection if malicious keys were provided.
**Learning:** Even when values are properly parameterized (using `?` placeholders), dynamic query construction using raw dictionary keys for column names is a critical vulnerability.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings for SET or INSERT clauses.
