"""Tests for StoryExporter"""

import pytest

from nebula_writer.supabase_db import SupabaseDB as CodexDatabase
from nebula_writer.exporter import StoryExporter


@pytest.fixture
def db():
    database = CodexDatabase()

    database.add_entity("Ravi", "character", "Protagonist detective")
    database.add_chapter(1, "The Beginning", "It was a dark night in Mumbai...")

    return database


@pytest.mark.skip(reason="Requires Supabase test project connection")
def test_export(db):
    exporter = StoryExporter(db)
    md = exporter.to_markdown()
    assert "# Story" in md
