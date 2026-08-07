## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2024-05-24 - Critical SQL Injection in Dynamic Query Generation
**Vulnerability:** Found a critical SQL injection vulnerability in `update_story_plan` (in `nebula_writer/codex.py`). The method directly interpolated dictionary keys from user input (`plan.keys()`) into `UPDATE` and `INSERT` query clauses (e.g. `SET k1 = ?, k2 = ?` or `INSERT INTO story_plan (k1, k2)`).
**Learning:** Even when values are properly parameterized (using `?` placeholders), dynamically constructing column names from unvalidated user input exposes the database to structural injection, allowing attackers to manipulate the query schema or execute arbitrary commands. This is a common pattern in Python when building flexible update methods without an ORM.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of expected column names before using them to construct any part of an SQL query string dynamically.

## 2024-05-24 - [Fix Permissive CORS Configuration]
**Vulnerability:** The FastAPI application used `allow_origins=["*"]` while `allow_credentials=True` was enabled. This is a major security risk that could allow Cross-Site Request Forgery (CSRF) and data read vulnerabilities. Modern browsers often block this configuration anyway.
**Learning:** Permissive wildcard origins should never be used when credentials (like cookies or authorization headers) are allowed.
**Prevention:** Always use an environment variable (e.g., `ALLOWED_ORIGINS`) with a safe local fallback to strictly govern allowed origins, especially when `allow_credentials=True` is enabled.
