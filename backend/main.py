"""
Nebula-Writer API Server
FastAPI backend for the Codex and writing tools
"""
import os
import json
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# Import Codex
from codex import CodexDatabase

# Initialize app
app = FastAPI(title="Nebula-Writer API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database instance
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
db = CodexDatabase(str(DATA_DIR / "codex.db"))

# ============ MODELS ============

class EntityCreate(BaseModel):
    name: str
    entity_type: str  # character, location, item
    description: Optional[str] = None
    current_location: Optional[str] = None
    is_alive: bool = True
    image_url: Optional[str] = None

class AttributeCreate(BaseModel):
    entity_id: int
    key: str
    value: str

class RelationshipCreate(BaseModel):
    from_entity_id: int
    to_entity_id: int
    relationship_type: str
    strength: float = 0.5
    description: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    chapter: Optional[int] = None
    scene: Optional[str] = None
    significance: str = "normal"

class ChapterCreate(BaseModel):
    number: int
    title: Optional[str] = None
    content: str = ""

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None

class SceneCreate(BaseModel):
    chapter_id: int
    number: int
    beat: Optional[str] = None
    content: str = ""

# ============ ENTITY ENDPOINTS ============

@app.get("/api/entities")
def get_entities(entity_type: Optional[str] = None):
    """Get all entities, optionally filtered by type"""
    return db.get_entities(entity_type)

@app.get("/api/entities/{entity_id}")
def get_entity(entity_id: int):
    """Get a single entity"""
    entity = db.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Include attributes
    entity['attributes'] = db.get_attributes(entity_id)
    return entity

@app.post("/api/entities")
def create_entity(entity: EntityCreate):
    """Create a new entity"""
    entity_id = db.add_entity(
        name=entity.name,
        entity_type=entity.entity_type,
        description=entity.description,
        current_location=entity.current_location,
        is_alive=entity.is_alive,
        image_url=entity.image_url
    )
    return {"id": entity_id, "message": "Entity created"}

@app.put("/api/entities/{entity_id}")
def update_entity(entity_id: int, entity: EntityCreate):
    """Update an entity"""
    success = db.update_entity(
        entity_id,
        name=entity.name,
        description=entity.description,
        current_location=entity.current_location,
        is_alive=entity.is_alive,
        image_url=entity.image_url
    )
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity updated"}

@app.delete("/api/entities/{entity_id}")
def delete_entity(entity_id: int):
    """Delete an entity"""
    success = db.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity deleted"}

# ============ ATTRIBUTE ENDPOINTS ============

@app.post("/api/attributes")
def create_attribute(attr: AttributeCreate):
    """Add an attribute to an entity"""
    attr_id = db.add_attribute(attr.entity_id, attr.key, attr.value)
    return {"id": attr_id, "message": "Attribute added"}

@app.get("/api/entities/{entity_id}/attributes")
def get_entity_attributes(entity_id: int):
    """Get all attributes for an entity"""
    return db.get_attributes(entity_id)

@app.delete("/api/attributes/{attr_id}")
def delete_attribute(attr_id: int):
    """Delete an attribute"""
    success = db.delete_attribute(attr_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return {"message": "Attribute deleted"}

# ============ RELATIONSHIP ENDPOINTS ============

@app.get("/api/relationships")
def get_relationships(entity_id: Optional[int] = None):
    """Get all relationships or those involving an entity"""
    return db.get_relationships(entity_id)

@app.post("/api/relationships")
def create_relationship(rel: RelationshipCreate):
    """Create a new relationship"""
    rel_id = db.add_relationship(
        from_id=rel.from_entity_id,
        to_id=rel.to_entity_id,
        rel_type=rel.relationship_type,
        strength=rel.strength,
        description=rel.description
    )
    return {"id": rel_id, "message": "Relationship created"}

@app.delete("/api/relationships/{rel_id}")
def delete_relationship(rel_id: int):
    """Delete a relationship"""
    success = db.delete_relationship(rel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return {"message": "Relationship deleted"}

# ============ EVENT ENDPOINTS ============

@app.get("/api/events")
def get_events(chapter: Optional[int] = None):
    """Get all events, optionally filtered by chapter"""
    return db.get_events(chapter)

@app.post("/api/events")
def create_event(event: EventCreate):
    """Log a new event"""
    event_id = db.add_event(
        title=event.title,
        description=event.description,
        chapter=event.chapter,
        scene=event.scene,
        significance=event.significance
    )
    return {"id": event_id, "message": "Event logged"}

# ============ CHAPTER ENDPOINTS ============

@app.get("/api/chapters")
def get_chapters():
    """Get all chapters"""
    return db.get_chapters()

@app.get("/api/chapters/{chapter_id}")
def get_chapter(chapter_id: int):
    """Get a single chapter with its scenes"""
    chapter = db.get_chapter(chapter_id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    chapter['scenes'] = db.get_scenes(chapter_id)
    return chapter

@app.post("/api/chapters")
def create_chapter(chapter: ChapterCreate):
    """Create a new chapter"""
    try:
        chapter_id = db.add_chapter(chapter.number, chapter.title, chapter.content)
        return {"id": chapter_id, "message": "Chapter created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/chapters/{chapter_id}")
def update_chapter(chapter_id: int, chapter: ChapterUpdate):
    """Update a chapter"""
    success = db.update_chapter(
        chapter_id,
        content=chapter.content,
        title=chapter.title,
        summary=chapter.summary
    )
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"message": "Chapter updated"}

@app.delete("/api/chapters/{chapter_id}")
def delete_chapter(chapter_id: int):
    """Delete a chapter"""
    success = db.delete_chapter(chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"message": "Chapter deleted"}

# ============ SCENE ENDPOINTS ============

@app.get("/api/chapters/{chapter_id}/scenes")
def get_scenes(chapter_id: int):
    """Get all scenes for a chapter"""
    return db.get_scenes(chapter_id)

@app.post("/api/scenes")
def create_scene(scene: SceneCreate):
    """Create a new scene"""
    scene_id = db.add_scene(scene.chapter_id, scene.number, scene.beat, scene.content)
    return {"id": scene_id, "message": "Scene created"}

# ============ STATS & SEARCH ============

@app.get("/api/stats")
def get_stats():
    """Get overall statistics"""
    return db.get_stats()

@app.get("/api/search")
def search(q: str = Query(..., min_length=2)):
    """Search across entities, chapters, events"""
    return db.search(q)

# ============ EXPORT ============

@app.get("/api/export/mermaid")
def export_mermaid():
    """Export relationship graph as Mermaid.js diagram"""
    relationships = db.get_relationships()
    
    lines = ["graph TD"]
    
    # Get all entities
    entities = db.get_entities()
    entity_map = {e['id']: e for e in entities}
    
    for rel in relationships:
        from_name = entity_map[rel['from_entity_id']]['name'].replace(" ", "_")
        to_name = entity_map[rel['to_entity_id']]['name'].replace(" ", "_")
        rel_type = rel['relationship_type']
        lines.append(f"    {from_name} -->|{rel_type}| {to_name}")
    
    return {"mermaid": "\n".join(lines)}

@app.get("/api/export/json")
def export_json():
    """Export entire Codex as JSON"""
    return {
        "entities": db.get_entities(),
        "relationships": db.get_relationships(),
        "events": db.get_events(),
        "chapters": db.get_chapters(),
        "stats": db.get_stats()
    }

# ============ AI WRITING ENDPOINTS ============

class AIWriteRequest(BaseModel):
    beat: str
    word_count: int = 500
    entity_ids: Optional[List[int]] = None
    chapter: Optional[int] = None

class AIRewriteRequest(BaseModel):
    text: str
    style: str = "noir"

class AIDescribeRequest(BaseModel):
    entity_name: str

class AIShowNotTellRequest(BaseModel):
    text: str

@app.post("/api/ai/write")
def ai_write_scene(req: AIWriteRequest):
    """Write a scene using AI with Codex context"""
    try:
        from ai_writer import AIWriter
        ai = AIWriter()
        result = ai.write_scene(
            db=db,
            beat=req.beat,
            word_count=req.word_count,
            entity_ids=req.entity_ids,
            chapter=req.chapter
        )
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/rewrite")
def ai_rewrite(req: AIRewriteRequest):
    """Rewrite text in a different style"""
    try:
        from ai_writer import AIWriter
        ai = AIWriter()
        result = ai.rewrite_style(req.text, req.style)
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/describe")
def ai_describe(req: AIDescribeRequest):
    """Generate sensory description for an entity"""
    try:
        from ai_writer import AIWriter
        ai = AIWriter()
        result = ai.generate_description(req.entity_name, db)
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/show-not-tell")
def ai_show_not_tell(req: AIShowNotTellRequest):
    """Convert telling to showing"""
    try:
        from ai_writer import AIWriter
        ai = AIWriter()
        result = ai.show_not_tell(req.text)
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ AUDIT ENDPOINTS ============

@app.get("/api/audit")
def audit_story():
    """Run full story audit"""
    try:
        from audit import StoryAuditor
        auditor = StoryAuditor(db)
        return auditor.audit_all_chapters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ MEMORY ENDPOINTS ============

@app.post("/api/memory/rebuild")
def rebuild_memory():
    """Rebuild vector memory index"""
    try:
        from memory import MemorySystem
        mem = MemorySystem()
        return mem.rebuild_index(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/search")
def memory_search(q: str = Query(..., min_length=2)):
    """Semantic search in memory"""
    try:
        from memory import MemorySystem
        mem = MemorySystem()
        return mem.get_relevant_context(q, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ HEALTH CHECK ============

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Nebula-Writer API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
