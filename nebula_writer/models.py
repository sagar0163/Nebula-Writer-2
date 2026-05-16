from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class ProjectModel(BaseModel):
    id: str
    title: str = "Untitled Novel"
    author: str = "Unknown"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

class CharacterModel(BaseModel):
    id: Optional[int] = None
    project_id: str
    name: str
    role: str = "major"
    core_desire: str = ""
    arc_current_state: str = ""
    relationships: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ResearchNodeModel(BaseModel):
    id: Optional[int] = None
    project_id: str
    topic: str
    queries_used: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    confidence: str = "medium"
    verification_status: str = "unverified"
    summary: str
    linked_entity_ids: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    last_used_in_chapter: Optional[UUID] = None

class LookaheadCardModel(BaseModel):
    id: Optional[int] = None
    project_id: str
    card_index: int
    certainty: str = "medium"
    chapter_number: int
    title: str
    scene_intention: str
    opening_image: str
    character_focus: str
    story_questions_open: List[str] = Field(default_factory=list)
    story_questions_close: List[str] = Field(default_factory=list)
    tension_targeted: str
    seeds_to_advance: List[str] = Field(default_factory=list)
    is_approved: bool = False
    created_at: Optional[datetime] = None

class CommentModel(BaseModel):
    id: Optional[int] = None
    chapter_id: UUID
    anchor_start: int
    anchor_end: int
    anchor_text: str
    comment_text: str
    ai_response: str = ""
    revised_text: str = ""
    status: str = "open"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    project_id: str
    chapter_id: Optional[str] = None
    stream: bool = True

class CommentRequest(BaseModel):
    chapter_id: str
    anchor_start: int
    anchor_end: int
    anchor_text: str
    comment_text: str

class SyncEvent(BaseModel):
    event_type: str
    project_id: str
    payload: Dict[str, Any]
