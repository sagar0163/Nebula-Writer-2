"""Tests for CodexDatabase"""

import pytest

from nebula_writer.supabase_db import SupabaseDB as CodexDatabase


@pytest.fixture
def db():
    database = CodexDatabase()
    return database


@pytest.mark.skip(reason="Requires Supabase test project connection")
def test_add_get_entity(db):
    entity_id = db.add_entity("Test Character", "character", "A test description")
    assert entity_id is not None
