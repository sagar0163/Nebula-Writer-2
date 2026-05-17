from nebula_writer.postgres_db import PostgresDB, create_postgres_db

db = PostgresDB()
try:
    db.update_chapter("1", **{"invalid_col = 1; DROP TABLE chapters; --": "bobby tables"})
except Exception as e:
    print(e)
