## 2024-05-24 - [Remove Hardcoded Supabase Credentials]
**Vulnerability:** A hardcoded connection string template (including project ID and hostname) existed in `nebula_writer/postgres_db.py` as a fallback mechanism.
**Learning:** Legacy fallback mechanisms often leak infrastructure details and pose a security risk. They can linger in the codebase if not actively reviewed.
**Prevention:** Strictly enforce the use of environment variables (`POSTGRES_CONNECTION_STRING`) for all database connections and avoid hardcoding any parts of connection URIs, even for fallback purposes.
## 2024-05-23 - [SQL Injection via Dynamic Keys]
**Vulnerability:** SQL Injection in `update_story_plan` via unsanitized dictionary keys used to construct dynamic `UPDATE` and `INSERT` clauses. The keys were joined and directly formatted into the SQL query without validating if they matched the columns in the database schema.
**Learning:** In a codebase avoiding an ORM, dynamic query construction that relies entirely on input dictionary keys is extremely dangerous and can lead to arbitrary SQL injection. It is not enough to parameterize the values; the keys (column names) must also be validated or strictly allowlisted.
**Prevention:** Always maintain a hardcoded allowlist of valid column names for a given table and explicitly filter incoming dictionary keys against this allowlist before interpolating them into a SQL string.
