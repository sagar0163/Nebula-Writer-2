## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2026-05-24 - [Fix SQL Injection in Dynamic Queries]
**Vulnerability:** The `update_story_plan` method in `nebula_writer/codex.py` dynamically interpolated keys from an unfiltered dictionary directly into SQL `INSERT` and `UPDATE` queries. This created a critical SQL injection vulnerability where an attacker could provide maliciously crafted dictionary keys to execute arbitrary SQL commands.
**Learning:** Even when avoiding ORMs, dynamically building SQL queries requires extreme caution. Interpolating input keys without validation bypasses parameterized query protections, exposing the database to manipulation.
**Prevention:** Always validate and filter dynamic column names against a strict allowlist of known, valid columns before incorporating them into SQL strings.
