import pytest
from fastapi.testclient import TestClient
from nebula_writer.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_project_id():
    return "test_novel_proj_123"

def test_01_project_initialization(client, mock_project_id):
    """Step 1: Initialize project with title and author"""
    pass

def test_02_character_lore_creation(client, mock_project_id):
    """Step 2: Create character lore"""
    pass

def test_03_research_node_generation(client, mock_project_id):
    """Step 3: Generate research nodes"""
    pass

def test_04_lookahead_forecasting(client, mock_project_id):
    """Step 4: Generate lookahead cards"""
    pass

def test_05_sse_chapter_streaming(client, mock_project_id):
    """Step 5: SSE real-time chapter streaming"""
    response = client.post(
        "/api/chat",
        json={"message": "Write Chapter 1", "project_id": mock_project_id, "stream": True}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    content = response.iter_lines()
    first_chunk = next(content)
    assert "data:" in first_chunk

def test_06_quality_gate_evaluation(client, mock_project_id):
    """Step 6: Quality gate evaluation"""
    from nebula_writer.quality_engine import QualityEngine
    import asyncio
    engine = QualityEngine()
    score, rubric = asyncio.run(engine.evaluate_prose("The dark night was very dark and stormy. The end."))
    assert isinstance(score, float)
    assert "narrative_drive" in rubric

def test_07_anti_slop_filtering(client, mock_project_id):
    """Step 7: Anti-slop cliches filtering"""
    from nebula_writer.anti_slop import AntiSlopFilter
    slop_filter = AntiSlopFilter()
    cleaned = slop_filter.clean_prose("A testament to their journey, they navigated the labyrinth of emotions.")
    assert "testament to" not in cleaned
    assert "labyrinth of emotions" not in cleaned

def test_08_natural_language_intent(client, mock_project_id):
    """Step 8: Natural language intent classification"""
    from nebula_writer.conversation import get_conversation_engine, IntentType
    engine = get_conversation_engine()
    
    intent = engine.classify_intent("add a character named John")
    assert intent.intent == IntentType.CREATE_ENTITY
    assert intent.extracted_info.get("name") == "John"
    
    intent_r = engine.classify_intent("Research Victorian London architecture")
    assert intent_r.intent == IntentType.RESEARCH_QUERY
    
    intent_w = engine.classify_intent("Write chapter 1")
    assert intent_w.intent == IntentType.WRITE_CHAPTER

def test_09_websocket_live_sync(client, mock_project_id):
    """Step 9: WebSocket live codex synchronization"""
    with client.websocket_connect(f"/ws/sync/{mock_project_id}") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"
        
        websocket.send_json({"entity_id": 1, "name": "Updated Elena"})
        update = websocket.receive_json()
        assert update["type"] == "sync_update"
        assert update["data"]["name"] == "Updated Elena"

def test_10_anchored_inline_comments(client, mock_project_id):
    """Step 10: Anchored inline comments and targeted revision"""
    response = client.post(
        "/api/comments",
        json={
            "context_type": "chapter",
            "target_id": "ch1",
            "highlighted_text": "dark night",
            "comment": "Make it more descriptive",
            "start_offset": 4,
            "end_offset": 14
        }
    )
    assert response.status_code == 200
    comment_id = response.json().get("comment_id")
    assert comment_id is not None
    
    from nebula_writer.comment_system import create_comment_engine
    engine = create_comment_engine()
    engine.add_comment("chapter", "ch1", "dark night", "Make it more descriptive", start=4, end=14)
    comments = engine.get_open_comments("chapter")
    test_cid = comments[0]["id"]
    
    rev_result = engine.generate_targeted_revision_span(test_cid, "The dark night was cold.")
    assert rev_result["original_span"] == "dark night"
    assert "Make it more descriptive" in rev_result["revised_span"]
    
    class MockDB:
        def get_entities(self): return []
        def get_plot_threads(self): return []
        def get_chapters(self): return []
        def get_relationships(self): return []
        def get_events(self): return []
        
    from nebula_writer.ripple_checker import create_ripple_checker
    ripple = create_ripple_checker(MockDB(), None)
    import asyncio
    report = asyncio.run(ripple.validate_post_revision_ripple("The dark night was cold.", rev_result["new_full_text"]))
    assert report["delta_analyzed"] is True
    assert report["revision_valid"] is True

def test_11_multi_format_export(client, mock_project_id):
    """Step 11: Multi-format document export (EPUB, DOCX, PDF)"""
    res_epub = client.get("/api/export/epub")
    assert res_epub.status_code == 200
    assert res_epub.json().get("type") == "epub"
    assert res_epub.json().get("content") is not None

    res_docx = client.get("/api/export/docx")
    assert res_docx.status_code == 200
    assert res_docx.json().get("type") == "docx"
    assert res_docx.json().get("content") is not None

    res_pdf = client.get("/api/export/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.json().get("type") == "pdf"
    assert res_pdf.json().get("content") is not None
