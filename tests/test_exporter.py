"""Tests for StoryExporter"""

import os

import pytest

from nebula_writer.exporter import StoryExporter

pytestmark = pytest.mark.skipif(
    os.environ.get("POSTGRES_CONNECTION_STRING") is None,
    reason="Requires POSTGRES_CONNECTION_STRING (Supabase/PostgreSQL test project)",
)


@pytest.fixture
def db(codex_db):
    database = codex_db

    database.add_entity("Ravi", "character", "Protagonist detective")
    database.add_chapter(1, "The Beginning", "It was a dark night in Mumbai...")

    return database


def test_export(db):
    exporter = StoryExporter(db)
    md = exporter.to_markdown()
    assert "# Story" in md
