"""
Nebula-Writer API Server
FastAPI backend for the Codex and writing tools
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import Subsystems
from nebula_writer.codex import CodexDatabase
from nebula_writer.comment_system import create_comment_engine, create_quality_layer
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from nebula_writer.idea_processor import create_story_architect
from nebula_writer.lookahead_engine import LookaheadEngine
from pydantic import BaseModel

load_dotenv()

import importlib.metadata

try:
    __version__ = importlib.metadata.version("nebula-writer")
except importlib.metadata.PackageNotFoundError:
    __version__ = "2.1.0"

# Initialize app
app = FastAPI(title="Nebula-Writer API", version=__version__)


def main():
    """CLI entry point to run the server"""
    import uvicorn

    uvicorn.run("nebula_writer.main:app", host="0.0.0.0", port=8000, reload=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database - SQLite or Supabase
db_type = os.environ.get("NEBULA_DB", "sqlite")

if db_type == "supabase":
    print("[OK] Using Supabase PostgreSQL database")
    from postgres_db import PostgresDB

    db = PostgresDB()
else:
    print("[OK] Using SQLite local database")
    DATA_DIR = Path(__file__).parent.parent / "data"
    DATA_DIR.mkdir(exist_ok=True)
    db = CodexDatabase(str(DATA_DIR / "codex.db"))

# Initialize Orchestrator (Step 7)
from nebula_writer.services.orchestrator import NarrativeOrchestrator

orchestrator = NarrativeOrchestrator()

# Keep direct access for simple CRUD (backwards compatibility)
db = orchestrator.db
plot_manager = orchestrator.pm
ai_writer = orchestrator.ai
lookahead_engine = LookaheadEngine(db, plot_manager, ai_writer)
story_architect = create_story_architect(ai_writer)
ripple_checker = orchestrator.ripple
comment_engine = create_comment_engine(ripple_checker)
quality_layer = create_quality_layer()
conversation_engine = orchestrator.conv

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


# v2.1 Models
class StoryAnchorCreate(BaseModel):
    anchor_type: str  # beginning, midpoint, end
    description: str


class OpenTensionCreate(BaseModel):
    description: str
    priority: str = "normal"


class LookaheadCardStatus(BaseModel):
    status: str  # approved, discarded


class CommentCreate(BaseModel):
    context_type: str
    target_id: str
    highlighted_text: str
    user_comment: str
    start: Optional[int] = None
    end: Optional[int] = None


class CommentAIResponse(BaseModel):
    response: str


class CommentResolve(BaseModel):
    notes: Optional[str] = ""


class CommentPushback(BaseModel):
    feedback: str


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
    entity["attributes"] = db.get_attributes(entity_id)
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
        image_url=entity.image_url,
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
        image_url=entity.image_url,
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
        description=rel.description,
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
        significance=event.significance,
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

    chapter["scenes"] = db.get_scenes(chapter_id)
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
    success = db.update_chapter(chapter_id, content=chapter.content, title=chapter.title, summary=chapter.summary)
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
    entity_map = {e["id"]: e for e in entities}

    for rel in relationships:
        from_name = entity_map[rel["from_entity_id"]]["name"].replace(" ", "_")
        to_name = entity_map[rel["to_entity_id"]]["name"].replace(" ", "_")
        rel_type = rel["relationship_type"]
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
        "stats": db.get_stats(),
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
        from nebula_writer.ai_writer import AIWriter

        ai = AIWriter()
        result = ai.write_scene(
            db=db, beat=req.beat, word_count=req.word_count, entity_ids=req.entity_ids, chapter=req.chapter
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


# ============ VERSION HISTORY ============


@app.get("/api/chapters/{chapter_id}/versions")
def get_chapter_versions(chapter_id: int):
    """Get all versions of a chapter"""
    return db.get_versions(chapter_id)


@app.get("/api/versions/{version_id}")
def get_version(version_id: int):
    """Get a specific chapter version"""
    version = db.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


class VersionCreate(BaseModel):
    chapter_id: int
    content: str


@app.post("/api/versions")
def save_version(req: VersionCreate):
    """Save a new chapter version"""
    version_id = db.save_version(req.chapter_id, req.content)
    return {"id": version_id, "message": "Version saved"}


# ============ CHARACTER KNOWLEDGE ============


class CharacterKnowledgeUpdate(BaseModel):
    entity_id: int
    chapter_id: int
    knowledge: str


@app.post("/api/character-knowledge")
def update_character_knowledge(req: CharacterKnowledgeUpdate):
    """Update what a character knows at a specific chapter"""
    knowledge_id = db.update_character_knowledge(req.entity_id, req.chapter_id, req.knowledge)
    return {"id": knowledge_id, "message": "Knowledge updated"}


@app.get("/api/character-knowledge/{entity_id}")
def get_character_knowledge(entity_id: int, chapter_id: Optional[int] = None):
    """Get what a character knows"""
    return db.get_character_knowledge(entity_id, chapter_id)


# ============ STORY TEMPLATES ============


@app.get("/api/templates")
def get_templates():
    """Get all story structure templates"""
    templates = db.get_templates()
    for t in templates:
        if t.get("structure"):
            t["structure"] = json.loads(t["structure"])
    return templates


@app.get("/api/templates/{template_id}")
def get_template(template_id: int):
    """Get a specific template"""
    template = db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.get("structure"):
        template["structure"] = json.loads(template["structure"])
    return template


# ============ CONSISTENCY CHECKING ============


@app.get("/api/consistency")
def get_consistency_issues(chapter_id: Optional[int] = None, unresolved_only: bool = False):
    """Get consistency issues"""
    return db.get_consistency_issues(chapter_id, unresolved_only)


@app.post("/api/consistency/check")
def run_consistency_check():
    """Run full consistency check"""
    return db.run_consistency_check()


@app.post("/api/consistency/{issue_id}/resolve")
def resolve_consistency_issue(issue_id: int):
    """Mark a consistency issue as resolved"""
    success = db.resolve_consistency_issue(issue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"message": "Issue resolved"}


# ============ AUTO-EXTRACT ============


class ExtractRequest(BaseModel):
    text: str


@app.post("/api/extract")
def extract_entities(req: ExtractRequest):
    """Extract potential entities from prose text"""
    return db.extract_entities_from_text(req.text)


# ============ MULTI-AI CLIENT ============


class AIClientRequest(BaseModel):
    provider: str = "gemini"
    prompt: str
    system_prompt: Optional[str] = None


@app.post("/api/ai/client")
def ai_client_generate(req: AIClientRequest):
    """Generate using any configured AI provider"""
    try:
        import os

        from ai_client import AIClient

        api_key = os.environ.get(f"{req.provider.upper()}_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail=f"No API key for {req.provider}")

        client = AIClient(provider=req.provider, api_key=api_key)
        result = client.generate(req.prompt, req.system_prompt)
        return {"text": result, "provider": req.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/providers")
def get_ai_providers():
    """Get available AI providers"""
    from ai_client import get_available_providers

    return get_available_providers()


# ============ NEW EXPORT FORMATS ============


@app.get("/api/export/markdown")
def export_markdown():
    """Export story as Markdown"""
    from exporter import StoryExporter

    exporter = StoryExporter(db)
    return {"content": exporter.to_plain_text()}


@app.get("/api/export/html")
def export_html():
    """Export story as HTML"""
    from exporter import StoryExporter

    exporter = StoryExporter(db)
    return {"content": exporter.to_html()}


@app.get("/api/export/text")
def export_text():
    """Export story as plain text"""
    from exporter import StoryExporter

    exporter = StoryExporter(db)
    return {"content": exporter.to_plain_text()}


@app.get("/api/export/epub")
def export_epub():
    """Export story as EPUB (returns base64)"""
    import base64

    from exporter import StoryExporter

    exporter = StoryExporter(db)
    epub_bytes = exporter.to_epub_bytes(title="My Novel", author="Author")
    return {"content": base64.b64encode(epub_bytes).decode(), "type": "epub"}


@app.get("/api/export/pdf")
def export_pdf():
    """Export story as HTML optimized for PDF"""
    from exporter import StoryExporter

    exporter = StoryExporter(db)
    return {"content": exporter.to_pdf_html()}


# ============ RESEARCH ENGINE ============


@app.get("/api/research/search")
def research_search(q: str = Query(..., min_length=2), num_results: int = 5):
    """Search the web for research (no API key required)"""
    try:
        from research import ResearchEngine

        engine = ResearchEngine()
        results = engine.search(q, num_results)
        return {"results": [r.to_dict() for r in results], "query": q}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/research/fiction")
def research_fiction(req: dict):
    """Research topic for fiction writing"""
    try:
        from research import ResearchEngine

        engine = ResearchEngine()
        result = engine.research_for_fiction(req.get("topic", ""), context=req.get("context", {}))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/research/history")
def research_history(period: str = Query(...), location: str = None):
    """Get historical context for a time period"""
    try:
        from research import ResearchEngine

        engine = ResearchEngine()
        result = engine.get_historical_context(period, location)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PLOT THREADS ============


@app.get("/api/plot-threads")
def get_plot_threads(status: str = None):
    """Get plot threads"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        return pm.get_plot_threads(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plot-threads")
def create_plot_thread(req: dict):
    """Create a new plot thread"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        thread_id = pm.add_plot_thread(
            req.get("title", ""), req.get("description"), req.get("planted_chapter"), req.get("importance", "normal")
        )
        return {"id": thread_id, "message": "Plot thread created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plot-threads/{thread_id}/resolve")
def resolve_plot_thread(thread_id: int, resolved_chapter: int = None):
    """Mark plot thread as resolved"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        success = pm.resolve_plot_thread(thread_id, resolved_chapter)
        return {"message": "Plot thread resolved" if success else "Not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ FORESHADOWING ============


@app.post("/api/foreshadowing")
def add_foreshadowing(req: dict):
    """Add foreshadowing element"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        foreshadow_id = pm.add_foreshadowing(
            req.get("plot_thread_id"),
            req.get("chapter_id"),
            req.get("content"),
            req.get("hint_level", "subtle"),
            req.get("payoff_chapter"),
        )
        return {"id": foreshadow_id, "message": "Foreshadowing added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/foreshadowing")
def get_foreshadowing(plot_thread_id: int = None):
    """Get foreshadowing elements"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        return pm.get_foreshadowing(plot_thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ WORLD RULES ============


@app.get("/api/world-rules")
def get_world_rules(category: str = None):
    """Get world rules"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        return pm.get_world_rules(category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/world-rules")
def add_world_rule(req: dict):
    """Add a world rule"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        rule_id = pm.add_world_rule(
            req.get("category", ""),
            req.get("rule", ""),
            req.get("description"),
            req.get("exceptions"),
            req.get("applies_to"),
        )
        return {"id": rule_id, "message": "World rule added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/world-rules/check")
def check_world_rules(req: dict):
    """Check text for world rule violations"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        violations = pm.check_world_rule_violation(req.get("text", ""))
        return {"violations": violations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ VOICE PROFILES ============


@app.post("/api/voice-profiles")
def set_voice_profile(req: dict):
    """Set character voice profile"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        profile_id = pm.set_voice_profile(
            req.get("entity_id"),
            req.get("vocabulary_level", "average"),
            req.get("speech_patterns"),
            req.get("common_phrases"),
            req.get("emotional_register", "neutral"),
            req.get("formal_level", "neutral"),
            req.get("dialect"),
            req.get("quirks"),
            req.get("sample_dialogue"),
        )
        return {"id": profile_id, "message": "Voice profile set"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice-profiles/{entity_id}")
def get_voice_profile(entity_id: int):
    """Get character voice profile"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        return pm.get_voice_profile(entity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice-profiles/{entity_id}/prompt")
def get_voice_prompt(entity_id: int):
    """Get voice profile as AI prompt"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        prompt = pm.generate_voice_prompt(entity_id)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ CONTINUITY CHECK ============


@app.post("/api/continuity/check-chapter")
def check_chapter_continuity(req: dict):
    """Check continuity for a chapter"""
    try:
        from plot_manager import create_plot_manager

        pm = create_plot_manager()
        result = pm.check_continuity(
            req.get("chapter_id"), req.get("chapter_text", ""), req.get("entities", []), req.get("events", [])
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ v2.1 STORY COMPASS & LOOKAHEAD ============


@app.post("/api/lookahead/generate")
def generate_lookahead():
    """Generate 3-chapter lookahead cards"""
    try:
        cards = lookahead_engine.generate_lookahead()
        return {"cards": cards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/lookahead/cards")
def get_lookahead_cards(status: str = "draft"):
    """Get lookahead cards"""
    return db.get_lookahead_cards(status)


@app.put("/api/lookahead/cards/{card_id}/status")
def update_lookahead_card_status(card_id: int, status_update: LookaheadCardStatus):
    """Update card status (approved, discarded)"""
    success = db.update_lookahead_card_status(card_id, status_update.status)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"message": "Card updated"}


@app.get("/api/story-compass/anchors")
def get_story_anchors():
    """Get all story anchors"""
    return db.get_story_anchors()


@app.post("/api/story-compass/anchors")
def add_story_anchor(anchor: StoryAnchorCreate):
    """Add a story anchor"""
    anchor_id = db.add_story_anchor(anchor.anchor_type, anchor.description)
    return {"id": anchor_id, "message": "Anchor added"}


@app.get("/api/story-compass/tensions")
def get_open_tensions(status: str = "open"):
    """Get open tensions"""
    return db.get_open_tensions(status)


@app.post("/api/story-compass/tensions")
def add_open_tension(tension: OpenTensionCreate):
    """Add an open tension"""
    tension_id = db.add_open_tension(tension.description, tension.priority)
    return {"id": tension_id, "message": "Tension added"}


@app.get("/api/story-compass/momentum")
def get_narrative_momentum():
    """Get narrative momentum score"""
    score = db.get_narrative_momentum()
    return {"momentum_score": score}


@app.post("/api/ripple-check")
def run_ripple_check(req: dict):
    """Run ripple check after a change"""
    try:
        context_type = req.get("context_type")
        target_id = req.get("target_id")
        changes = req.get("changes", {})
        report = comment_engine.ripple_check(context_type, target_id, changes)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ v2.1 INLINE COMMENTS ============


@app.get("/api/comments")
def get_comments(context_type: Optional[str] = None, target_id: Optional[str] = None):
    """Get comments"""
    return comment_engine.get_comments(context_type, target_id)


@app.post("/api/comments")
def add_comment(comment: CommentCreate):
    """Add a new inline comment"""
    comment_id = comment_engine.add_comment(
        comment.context_type,
        comment.target_id,
        comment.highlighted_text,
        comment.user_comment,
        comment.start,
        comment.end,
    )
    return {"id": comment_id, "message": "Comment added"}


@app.post("/api/comments/{comment_id}/ai-respond")
def comment_ai_respond(comment_id: str, req: CommentAIResponse):
    """AI responds to a comment"""
    success = comment_engine.ai_respond(comment_id, req.response)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "AI responded"}


@app.post("/api/comments/{comment_id}/resolve")
def comment_resolve(comment_id: str, req: CommentResolve):
    """User resolves a comment"""
    result = comment_engine.resolve_comment(comment_id, req.notes)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/api/comments/{comment_id}/pushback")
def comment_pushback(comment_id: str, req: CommentPushback):
    """User pushes back on AI response"""
    success = comment_engine.pushback(comment_id, req.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Pushback recorded"}


# ============ v2.1 STORY ARCHITECT CHAT ============


class ArchitectChatRequest(BaseModel):
    """
    Request model for the Story Architect chat session.
    Contains the full message history and optionally the current story state.
    """

    history: List[Dict]
    current_state: Optional[Dict] = {}


@app.post("/api/architect/chat")
def architect_chat(req: ArchitectChatRequest):
    """
    Primary endpoint for the Conversational Story Architect.

    Processes the chat history using the StoryArchitect engine and returns:
    1. A natural language response for the chat UI.
    2. A list of suggested story elements (extractions) to add to the project.
    """
    try:
        # Build the current project state from the database if not provided by the client.
        # This state provides the AI with context about existing characters and plot points.
        state = req.current_state or {
            "entities": db.get_entities(),
            "anchors": db.get_story_anchors(),
            "tensions": db.get_open_tensions(),
            "plot_threads": db.get_plot_threads(),
        }

        # Invoke the architect logic
        result = story_architect.process_chat(req.history, state)
        return result
    except Exception as e:
        # Log the error and return a 500 status code
        print(f"API Error in Architect Chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process architect session")


# ============ v2.1 CONVERSATION-DRIVEN OPERATIONS ============


@app.get("/api/conversation/history")
def get_conversation_history(limit: int = 20):
    """Get recent conversation"""
    engine = get_conversation_engine()
    return {"history": engine.get_conversation_history(limit)}


@app.post("/api/conversation/clear")
def clear_conversation():
    """Clear chat history"""
    engine = get_conversation_engine()
    engine.clear_history()
    return {"message": "Conversation cleared"}


# ============ v2.1 CONVERSATION-DRIVEN OPERATIONS ============


@app.post("/api/idea/start")
def start_idea_processing(req: dict):
    """Start new project - process idea and begin Q&A"""
    try:
        from idea_processor import IdeaProcessor

        processor = IdeaProcessor()
        result = processor.process_idea(req.get("idea", ""))
        return {
            "detected": result["detected"],
            "questions": result["questions"][:1],  # Ask first question only
            "progress": result["questions_remaining"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/idea/answer")
def process_idea_answer(req: dict):
    """Answer clarifying question"""
    try:
        from idea_processor import IdeaProcessor

        processor = IdeaProcessor()

        # Restore state from session (simplified - in prod use DB/session)
        answer = processor.answer_question(req.get("question_id", ""), req.get("answer", ""))

        result = {"answer": answer, "ready": processor.is_ready()}

        if processor.is_ready():
            # Generate world proposal
            world = processor.generate_world_proposal()
            characters = processor.generate_character_proposals()
            result["world_proposal"] = world
            result["character_proposals"] = characters
            result["next_step"] = "review_world"
        else:
            # Get next question
            next_q = next((q for q in processor.questions if not q.user_answer), None)
            if next_q:
                result["next_question"] = next_q.to_dict()
                result["progress"] = (
                    f"{sum(1 for q in processor.questions if q.user_answer)}/{len(processor.questions)}"
                )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compass")
def get_story_compass():
    """Get current Story Compass state"""
    try:
        from outline_engine import create_evolution_engine

        engine = create_evolution_engine()
        # Initialize with default if fresh
        if not engine.story_anchors.emotional_start:
            engine.initialize()
        return engine.get_compass()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/lookahead")
def get_lookahead_evolution():
    """Get rolling 3-chapter lookahead"""
    try:
        from outline_engine import create_evolution_engine

        engine = create_evolution_engine()
        return {"cards": engine.get_lookahead_cards()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lookahead/approve")
def approve_lookahead(chapter_num: int):
    """Approve lookahead card before writing"""
    try:
        from outline_engine import create_evolution_engine

        engine = create_evolution_engine()
        success = engine.approve_lookahead_card(chapter_num)
        return {"approved": success, "chapter": chapter_num}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plot/redirect")
def redirect_story_direction(req: dict):
    """User redirects story direction"""
    try:
        from outline_engine import create_evolution_engine

        engine = create_evolution_engine()
        result = engine.redirect_story(req.get("type", "user_redirect"), req.get("details", ""))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments")
def create_inline_comment(req: dict):
    """Add inline comment to chapter/codex/lookahead"""
    try:
        from comment_system import create_comment_engine

        engine = create_comment_engine()
        comment_id = engine.add_comment(
            context_type=req.get("context_type", "chapter"),
            target_id=str(req.get("target_id", "")),
            highlighted_text=req.get("highlighted_text", ""),
            user_comment=req.get("comment", ""),
            start=req.get("start_offset"),
            end=req.get("end_offset"),
        )
        return {"comment_id": comment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/comments")
def get_inline_comments(context_type: str = None, target_id: str = None):
    """Get comments"""
    try:
        from comment_system import create_comment_engine

        engine = create_comment_engine()
        comments = engine.get_comments(context_type, target_id)
        open_count = len([c for c in comments if c["status"] in ["open", "ai_responded", "pushback", "ripple_pending"]])
        return {"comments": comments, "open_count": open_count, "can_approve": open_count == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/{comment_id}/ai-respond")
def ai_respond_to_comment(comment_id: str, req: dict):
    """AI responds to comment"""
    try:
        from comment_system import create_comment_engine

        engine = create_comment_engine()
        success = engine.ai_respond(comment_id, req.get("response", ""))
        return {"responded": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/{comment_id}/resolve")
def resolve_inline_comment(comment_id: str, req: dict = None):
    """Resolve comment and trigger ripple check"""
    try:
        from comment_system import create_comment_engine

        engine = create_comment_engine()
        notes = req.get("notes", "") if req else ""
        result = engine.resolve_comment(comment_id, notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/pushback")
def pushback_comment(comment_id: str, req: dict):
    """User pushes back on AI response"""
    try:
        from comment_system import create_comment_engine

        engine = create_comment_engine()
        success = engine.pushback(comment_id, req.get("feedback", ""))
        return {"pushback_recorded": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quality/analyze")
def analyze_chapter_quality(chapter_id: int = None, content: str = None):
    """Analyze chapter quality (anti-slop)"""
    try:
        from comment_system import create_quality_layer

        quality = create_quality_layer()

        if content:
            result = quality.analyze_chapter(content)
        elif chapter_id:
            chapter = db.get_chapter(chapter_id=chapter_id)
            if chapter:
                result = quality.analyze_chapter(chapter.get("content", ""))
            else:
                raise HTTPException(status_code=404, detail="Chapter not found")
        else:
            raise HTTPException(status_code=400, detail="Provide chapter_id or content")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chapter/{chapter_id}/can-approve")
def can_approve_chapter(chapter_id: int):
    """Check if chapter can be approved (no blocking comments)"""
    try:
        from comment_system import create_comment_engine

        engine = create_comment_engine()
        return engine.can_approve_chapter(str(chapter_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ CHAT MODE (v2.1) ============


class ChatRequest(BaseModel):
    message: str
    project_state: Optional[Dict] = None


@app.post("/api/chat")
async def chat_with_ai(req: ChatRequest):
    """
    Main chat endpoint (Step 3)
    Routes through NarrativeOrchestrator for stateful, priority-aware generation.
    """
    try:
        response = await orchestrator.handle_chat(req.message)
        return response
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history")
def get_chat_history():
    """Get recent chat history"""
    try:
        return conversation_engine.get_conversation_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/clear")
def clear_chat_history():
    """Clear chat history"""
    try:
        conversation_engine.clear_history()
        return {"cleared": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ HEALTH CHECK ============


@app.get("/api/system/stability")
def check_stability():
    """Verify core narrative engine integrity"""
    required_files = [
        "backend/core/narrative_state_engine.py",
        "backend/core/memory_manager.py",
        "backend/services/orchestrator.py",
    ]
    status = {file: os.path.exists(Path(__file__).parent.parent / file) for file in required_files}
    is_stable = all(status.values())
    return {"stable": is_stable, "files_checked": status, "timestamp": datetime.now().isoformat()}


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": __version__,
        "mode": "chat-first",
        "database": os.environ.get("NEBULA_DB", "sqlite"),
    }


@app.get("/")
async def read_index():
    """Serve the frontend index.html"""
    return FileResponse(Path(__file__).parent.parent / "frontend" / "index.html")


if __name__ == "__main__":
    import uvicorn

    print("Starting Nebula-Writer API server v2.1 (Chat-First)...")
    print("Using database:", os.environ.get("NEBULA_DB", "sqlite"))
    uvicorn.run(app, host="0.0.0.0", port=8000)
