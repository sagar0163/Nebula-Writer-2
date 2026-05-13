"""
Tests for CodexDatabase
"""
import pytest
from nebula_writer.codex import CodexDatabase

@pytest.fixture
def db():
    """Fixture for Codex database in memory"""
    database = CodexDatabase(":memory:")
    return database

def test_add_get_entity(db):
    entity_id = db.add_entity("Test Character", "character", "A test description")
    assert entity_id is not None

    entity = db.get_entity(entity_id)
    assert entity["name"] == "Test Character"
    assert entity["type"] == "character"
    assert entity["description"] == "A test description"

def test_update_entity(db):
    entity_id = db.add_entity("Old Name", "character")
    success = db.update_entity(entity_id, name="New Name", description="New description")
    assert success is True

    entity = db.get_entity(entity_id)
    assert entity["name"] == "New Name"
    assert entity["description"] == "New description"

def test_delete_entity(db):
    entity_id = db.add_entity("To Be Deleted", "character")
    success = db.delete_entity(entity_id)
    assert success is True

    entity = db.get_entity(entity_id)
    assert entity is None

def test_add_get_attribute(db):
    entity_id = db.add_entity("Attr Test", "character")
    attr_id = db.add_attribute(entity_id, "age", "25")
    assert attr_id is not None

    attrs = db.get_attributes(entity_id)
    assert len(attrs) == 1
    assert attrs[0]["key"] == "age"
    assert attrs[0]["value"] == "25"

def test_add_get_relationship(db):
    id1 = db.add_entity("Person A", "character")
    id2 = db.add_entity("Person B", "character")

    rel_id = db.add_relationship(id1, id2, "friends")
    assert rel_id is not None

    rels = db.get_relationships(id1)
    assert len(rels) == 1
    assert rels[0]["relationship_type"] == "friends"
    assert rels[0]["to_entity_id"] == id2

def test_chapter_management(db):
    ch_id = db.add_chapter(1, "First Chapter", "It begins.")
    assert ch_id is not None

    chapters = db.get_chapters()
    assert len(chapters) == 1
    assert chapters[0]["title"] == "First Chapter"

    db.update_chapter(ch_id, title="Updated Title", content="New content")
    ch = db.get_chapter(ch_id)
    assert ch["title"] == "Updated Title"
    assert ch["content"] == "New content"

    db.delete_chapter(ch_id)
    assert len(db.get_chapters()) == 0

def test_scene_management(db):
    ch_id = db.add_chapter(1, "Chapter 1", "Content")
    scene_id = db.add_scene(ch_id, 1, "Action beat", "Scene content")
    assert scene_id is not None

    scenes = db.get_scenes(ch_id)
    assert len(scenes) == 1
    assert scenes[0]["beat"] == "Action beat"
    assert scenes[0]["content"] == "Scene content"

def test_event_management(db):
    event_id = db.add_event("Big Event", "Something happened", 1)
    assert event_id is not None

    events = db.get_events()
    assert len(events) == 1
    assert events[0]["title"] == "Big Event"
    assert events[0]["chapter"] == 1
