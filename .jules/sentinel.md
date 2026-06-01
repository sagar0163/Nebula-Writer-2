## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-06-01 - [Fix SQL Injection in update_story_plan]
**Vulnerability:** The `update_story_plan` function in `nebula_writer/codex.py` accepted a dictionary of updates and dynamically interpolated its keys directly into the SQL `UPDATE` and `INSERT` statements as column names without prior validation.
**Learning:** Constructing raw SQL queries by directly interpolating dictionary keys makes the application vulnerable to SQL injection if an attacker can manipulate the keys. Even when parameterizing values (using `?`), the column names themselves must be validated.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings (such as SET or INSERT clauses).
