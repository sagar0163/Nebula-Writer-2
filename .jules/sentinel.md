## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-05-19 - [Critical] SQL Injection via Dynamic Column Names in Dictionary Keys
**Vulnerability:** A SQL injection vulnerability existed in `update_story_plan` where unfiltered dictionary keys were interpolated directly into the SQL `UPDATE` and `INSERT` query strings (e.g. `set_clause = ", ".join([f"{k} = ?" for k in plan.keys()])`). Since the database constructs queries without an ORM, an attacker supplying a dictionary with malicious keys could alter the executed query.
**Learning:** Even if parameter values are safely passed via `?` placeholders, the *keys* of a dictionary used to construct `SET` or `INSERT` clauses can still cause SQL injection if they are derived from external input and directly formatted into the SQL string.
**Prevention:** Always validate and filter dictionary keys against a strict, explicit allowlist of valid column names before interpolating them into SQL statements. Example: `safe_plan = {k: v for k, v in plan.items() if k in allowed_keys}`.
