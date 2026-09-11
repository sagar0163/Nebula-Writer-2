"""Shared fixtures for the nebula-writer test suite.

The Supabase/PostgreSQL integration tests historically used an unconditional
``@pytest.mark.skip`` and were never executed. They are now enabled whenever a
``POSTGRES_CONNECTION_STRING`` is provided (the way ``SupabaseDB`` itself
locates a database). When the variable is absent the modules that opt in via
``pytestmark = pytest.mark.skipif(...)`` skip gracefully, so CI without a
database stays green.
"""

import os

import pytest

from nebula_writer.supabase_db import SupabaseDB


def _public_table_names(database) -> list:
    with database.conn.cursor() as cur:
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        return [r["tablename"] for r in cur.fetchall()]


@pytest.fixture
def codex_db():
    """A SupabaseDB connected to the test project, with all tables wiped.

    Each test that requests this fixture starts from a clean schema, so
    integration tests that plant fixed seed data (entity counts, unique chapter
    numbers, word counts) never collide with rows left by earlier tests.
    """
    database = SupabaseDB()
    tables = _public_table_names(database)
    if tables:
        with database.conn.cursor() as cur:
            quoted = ", ".join(f'"{t}"' for t in tables)
            cur.execute(f"TRUNCATE {quoted} RESTART IDENTITY CASCADE")
            database.conn.commit()
    return database


requires_db = pytest.mark.skipif(
    os.environ.get("POSTGRES_CONNECTION_STRING") is None,
    reason="Requires POSTGRES_CONNECTION_STRING (Supabase/PostgreSQL test project)",
)
