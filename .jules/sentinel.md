## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.
## 2024-05-24 - SQL Injection in Dynamic Updates
**Vulnerability:** SQL Injection in `update_story_plan` via unsanitized dictionary keys used directly in `INSERT` and `UPDATE` column definitions.
**Learning:** Python dictionary keys passed directly into SQL statements without an explicit allowlist validation create a direct vector for SQL injection, especially in functions designed to accept dynamic kwargs/dict arguments.
**Prevention:** Always validate and filter dictionary keys against an explicit, hardcoded list of valid column names before interpolating them into dynamic SQL strings.
