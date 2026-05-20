## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.

## 2026-05-20 - [Fix SQL Injection in update_story_plan]
**Vulnerability:** The `update_story_plan` method in `nebula_writer/codex.py` dynamically constructed SQL queries (`UPDATE` and `INSERT`) using keys from an arbitrary user-supplied dictionary without validation.
**Learning:** Functions accepting dictionaries to create SQL queries (e.g. key-value updates) are vulnerable to SQL Injection if the keys are directly concatenated into the string instead of being validated.
**Prevention:** Always validate and filter dictionary keys against an explicit allowlist of valid column names before interpolating them into SQL strings to prevent SQL injection vulnerabilities.
