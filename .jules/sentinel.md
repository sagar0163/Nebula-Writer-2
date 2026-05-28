## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2026-05-28 - [Prevent SQL Injection from Unvalidated Dictionary Keys]
**Vulnerability:** In `nebula_writer/codex.py`, the `update_story_plan` method constructed dynamic SQL strings by directly iterating over dictionary keys provided in the `plan` argument without validation, leading to a SQL injection vulnerability.
**Learning:** Dynamic SQL string construction must explicitly filter and validate all variable inputs, including dictionary keys, against an allowlist, even if the values are parameterized. A dictionary input might contain arbitrary keys injected by a user.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings (such as SET or INSERT clauses) to prevent SQL injection vulnerabilities.
