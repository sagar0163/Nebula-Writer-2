"""Tests for CodexDatabase"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("POSTGRES_CONNECTION_STRING") is None,
    reason="Requires POSTGRES_CONNECTION_STRING (Supabase/PostgreSQL test project)",
)


@pytest.fixture
def db(codex_db):
    return codex_db


def test_add_get_entity(db):
    entity_id = db.add_entity("Test Character", "character", "A test description")
    assert entity_id is not None
