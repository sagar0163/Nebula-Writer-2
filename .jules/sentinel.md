## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2026-06-04 - [Dynamic SQL Column Name Injection]
**Vulnerability:** In `nebula_writer/codex.py`, the `update_story_plan` method dynamically interpolated dictionary keys (`plan.keys()`) into raw SQL `INSERT` and `UPDATE` strings. Since dictionary keys were not validated, an attacker could potentially inject arbitrary SQL commands by passing a crafted dictionary.
**Learning:** Even when values are properly parameterized (using `?` or `%s`), dynamically constructing SQL statements using dictionary keys from untrusted sources introduces a critical SQL injection risk. This is a common pattern in Python when trying to build dynamic update queries.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings (such as SET or INSERT clauses). Never trust keys directly from input dictionaries.
