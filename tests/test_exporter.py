"""
Tests for StoryExporter
"""
import pytest
from nebula_writer.codex import CodexDatabase
from nebula_writer.exporter import StoryExporter

@pytest.fixture
def db():
    """Fixture for Codex database in memory"""
    database = CodexDatabase(":memory:")

    ravi_id = database.add_entity("Ravi", "character", "Protagonist detective")
    database.add_chapter(1, "The Beginning", "It was a dark night in Mumbai...")

    return database

def test_exporter_markdown(db):
    exporter = StoryExporter(db)
    md = exporter.to_markdown()
    assert "# Story" in md
    assert "Ravi" in md
    assert "The Beginning" in md

def test_exporter_html(db):
    exporter = StoryExporter(db)
    html = exporter.to_html()
    assert "<html>" in html
    assert "Ravi" in html
    assert "The Beginning" in html

def test_exporter_json(db):
    exporter = StoryExporter(db)
    json_data = exporter.to_json()
    assert "entities" in json_data
    assert len(json_data["entities"]) == 1
    assert "chapters" in json_data
    assert len(json_data["chapters"]) == 1

def test_exporter_plain_text(db):
    exporter = StoryExporter(db)
    text = exporter.to_plain_text()
    assert "MY NOVEL" in text
    assert "Ravi" in text
    assert "The Beginning" in text

def test_exporter_epub_bytes(db):
    exporter = StoryExporter(db)
    epub = exporter.to_epub_bytes()
    assert isinstance(epub, bytes)
    assert len(epub) > 0
