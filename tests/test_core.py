"""Nebula-Writer Tests"""

import pytest

from nebula_writer.audit import StoryAuditor
from nebula_writer.supabase_db import SupabaseDB as CodexDatabase
from nebula_writer.exporter import StoryExporter
from nebula_writer.search import SearchEngine


@pytest.fixture
def db():
    database = CodexDatabase()

    ravi_id = database.add_entity("Ravi", "character", "Protagonist detective")
    priya_id = database.add_entity("Priya", "character", "Love interest")
    mumbai_id = database.add_entity("Mumbai", "location", "City setting")

    database.add_attribute(ravi_id, "age", "32")
    database.add_attribute(priya_id, "age", "28")

    database.add_relationship(ravi_id, priya_id, "loves", 0.9)
    database.add_relationship(ravi_id, mumbai_id, "lives_in")

    database.add_chapter(1, "The Beginning", "It was a dark night in Mumbai...")
    database.add_event("Ravi meets Priya", "First meeting at crime scene", 1, "major")

    return database


@pytest.mark.skip(reason="Requires Supabase test project connection")
def test_codex(db):
    stats = db.get_stats()
    assert stats["total_entities"] == 3
    assert stats["total_chapters"] == 1
    assert stats["total_words"] == 7


@pytest.mark.skip(reason="Requires Supabase test project connection")
def test_audit(db):
    auditor = StoryAuditor(db)
    results = auditor.audit_all_chapters()
    assert "total_issues" in results
    assert results["total_issues"] >= 0


@pytest.mark.skip(reason="Requires Supabase test project connection")
def test_search(db):
    search = SearchEngine(db)

    results = search.search_all("Mumbai")
    assert len(results["entities"]) > 0
    assert any("Mumbai" in e["name"] for e in results["entities"])

    stats = search.get_story_stats()
    assert "writing_progress" in stats
    assert stats["writing_progress"]["total_words"] == 7


@pytest.mark.skip(reason="Requires Supabase test project connection")
def test_export(db):
    exporter = StoryExporter(db)

    md = exporter.to_markdown()
    assert "# Story" in md
    assert "Ravi" in md

    html = exporter.to_html()
    assert "<html>" in html
    assert "Mumbai" in html

    json_data = exporter.to_json()
    assert "entities" in json_data
    assert len(json_data["entities"]) == 3
