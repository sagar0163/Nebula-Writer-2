"""
Nebula-Writer Tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from codex import CodexDatabase
from audit import StoryAuditor
from search import SearchEngine
from exporter import StoryExporter


def test_codex():
    """Test Codex database"""
    print("Testing Codex...")
    db = CodexDatabase()
    
    # Add entities
    ravi_id = db.add_entity("Ravi", "character", "Protagonist detective")
    priya_id = db.add_entity("Priya", "character", "Love interest")
    mumbai_id = db.add_entity("Mumbai", "location", "City setting")
    
    # Add attributes
    db.add_attribute(ravi_id, "age", "32")
    db.add_attribute(priya_id, "age", "28")
    
    # Add relationship
    db.add_relationship(ravi_id, priya_id, "loves", 0.9)
    db.add_relationship(ravi_id, mumbai_id, "lives_in")
    
    # Add chapter
    db.add_chapter(1, "The Beginning", "It was a dark night in Mumbai...")
    
    # Add event
    db.add_event("Ravi meets Priya", "First meeting at crime scene", 1, "major")
    
    # Get stats
    stats = db.get_stats()
    assert stats['total_entities'] == 3
    assert stats['total_chapters'] == 1
    
    print("✅ Codex tests passed!")
    return db


def test_audit(db):
    """Test Story Auditor"""
    print("Testing Auditor...")
    auditor = StoryAuditor(db)
    results = auditor.audit_all_chapters()
    assert results['total_issues'] >= 0
    print("✅ Auditor tests passed!")


def test_search(db):
    """Test Search Engine"""
    print("Testing Search...")
    search = SearchEngine(db)
    
    results = search.search_all("Mumbai")
    assert len(results['entities']) > 0
    
    stats = search.get_story_stats()
    assert 'writing_progress' in stats
    
    print("✅ Search tests passed!")


def test_export(db):
    """Test Exporter"""
    print("Testing Exporter...")
    exporter = StoryExporter(db)
    
    md = exporter.to_markdown()
    assert "# Story" in md
    
    html = exporter.to_html()
    assert "<html>" in html
    
    json_data = exporter.to_json()
    assert 'entities' in json_data
    
    print("✅ Exporter tests passed!")


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Running Nebula-Writer Tests")
    print("=" * 50)
    
    db = test_codex()
    test_audit(db)
    test_search(db)
    test_export(db)
    
    print("=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
