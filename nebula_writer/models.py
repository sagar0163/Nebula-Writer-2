"""
Nebula-Writer Models & LLM Factory

Provides Pydantic models for the application and a LangChain ChatModel factory
with automatic provider detection and fallback chain.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
import os


# =============================================================================
# PYDANTIC MODELS (API schemas)
# =============================================================================

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


# =============================================================================
# LLM PROVIDER DETECTION & FACTORY
# =============================================================================

def _detect_provider() -> str:
    """
    Detect which LLM provider has an API key configured.
    Priority: Mistral > Gemini > OpenAI > Anthropic > HuggingFace
    """
    # Check Mistral first (working key in .env)
    if os.environ.get("MISTRAL_API_KEY"):
        return "mistral"
    
    # Check Google Gemini
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    
    # Check OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    
    # Check Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    
    # Check HuggingFace
    if os.environ.get("HUGGINGFACE_API_KEY"):
        return "huggingface"
    
    # Default to gemini (will fail gracefully if no key)
    return "gemini"


def create_chat_model_with_fallbacks(
    primary_provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> Any:
    """
    Create a LangChain ChatModel with automatic fallback chain.
    
    Falls back through available providers in order:
    Mistral → Gemini → OpenAI → Anthropic → HuggingFace
    
    Args:
        primary_provider: Override auto-detection (mistral, gemini, openai, anthropic, huggingface)
        temperature: Sampling temperature
        max_tokens: Maximum tokens per response
        
    Returns:
        LangChain BaseChatModel with fallback chain
    """
    from langchain_core.language_models import BaseChatModel
    from langchain_core.runnables import RunnableWithFallbacks
    
    # Auto-detect primary if not specified
    if primary_provider is None:
        primary_provider = _detect_provider()
    
    # Build model chain in fallback order
    models = []
    
    # Order: Mistral → Gemini → OpenAI → Anthropic → HuggingFace
    provider_order = ["mistral", "gemini", "openai", "anthropic", "huggingface"]
    
    # Move primary to front
    if primary_provider in provider_order:
        provider_order.remove(primary_provider)
    provider_order.insert(0, primary_provider)
    
    for provider in provider_order:
        model = _create_model(provider, temperature, max_tokens)
        if model is not None:
            models.append(model)
    
    if not models:
        raise ValueError("No LLM provider configured. Set MISTRAL_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or HUGGINGFACE_API_KEY")
    
    # Create fallback chain: primary.with_fallbacks(alternatives)
    if len(models) == 1:
        return models[0]
    
    primary = models[0]
    fallbacks = models[1:]
    
    return primary.with_fallbacks(fallbacks)


def _create_model(provider: str, temperature: float, max_tokens: int):
    """Create a single provider model if API key is available."""
    
    if provider == "mistral":
        api_key = os.environ.get("MISTRAL_API_KEY")
        if api_key:
            try:
                from langchain_mistralai import ChatMistralAI
                return ChatMistralAI(
                    model="mistral-large-latest",
                    mistral_api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except ImportError:
                pass
    
    elif provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=api_key,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            except ImportError:
                pass
    
    elif provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4o",
                    openai_api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except ImportError:
                pass
    
    elif provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model="claude-sonnet-4-20250514",
                    anthropic_api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except ImportError:
                pass
    
    elif provider == "huggingface":
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if api_key:
            try:
                from langchain_huggingface import ChatHuggingFace
                from langchain_huggingface import HuggingFaceEndpoint
                endpoint = HuggingFaceEndpoint(
                    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
                    huggingfacehub_api_token=api_key,
                    temperature=temperature,
                    max_new_tokens=max_tokens,
                )
                return ChatHuggingFace(llm=endpoint)
            except ImportError:
                pass
    
    return None


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_available_providers() -> List[Dict]:
    """Check which providers have API keys configured."""
    providers = []
    
    if os.environ.get("MISTRAL_API_KEY"):
        providers.append({"id": "mistral", "name": "Mistral AI", "available": True})
    if os.environ.get("GEMINI_API_KEY"):
        providers.append({"id": "gemini", "name": "Google Gemini", "available": True})
    if os.environ.get("OPENAI_API_KEY"):
        providers.append({"id": "openai", "name": "OpenAI GPT-4", "available": True})
    if os.environ.get("ANTHROPIC_API_KEY"):
        providers.append({"id": "anthropic", "name": "Anthropic Claude", "available": True})
    if os.environ.get("HUGGINGFACE_API_KEY"):
        providers.append({"id": "huggingface", "name": "Hugging Face", "available": True})
    
    return providers


if __name__ == "__main__":
    print("Available providers:", get_available_providers())
    print("Auto-detected primary:", _detect_provider())