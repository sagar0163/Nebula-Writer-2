"""
Nebula-Writer Models & LLM Factory

Provides Pydantic models for the application and a LangChain ChatModel factory
with automatic provider detection and comprehensive fallback chain including
all free providers from cheahjs/free-llm-api-resources and nherx/free-llm-api-resources.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

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
# LLM PROVIDER DETECTION & FACTORY WITH COMPREHENSIVE FREE PROVIDER FALLBACK
# =============================================================================

# -----------------------------------------------------------------------------
# Provider configurations for free LLM APIs (from cheahjs/nherx free-llm-api-resources)
# -----------------------------------------------------------------------------

FREE_PROVIDER_CONFIGS = {
    # --- OpenRouter (20 req/min, 50/day, 1000/day with $10 topup) ---
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": [
            "google/gemma-4-26b-a4b-it:free",
            "google/gemma-4-31b-it:free",
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "nvidia/nemotron-nano-9b-v2:free",
            "openai/gpt-oss-20b:free",
            "cohere/north-mini-code:free",
            "inclusionai/ling-3.0-flash:free",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "nvidia/nemotron-3.5-content-safety:free",
            "poolside/laguna-m.1:free",
            "poolside/laguna-s-2.1:free",
            "poolside/laguna-xs-2.1:free",
        ],
        "default_model": "google/gemma-4-26b-a4b-it:free",
        "rate_limit": "20 req/min, 50/day",
    },
    # --- Google AI Studio (Gemini) ---
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "models": [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemma-4-31b-instruct",
            "gemma-4-26b-a4b-instruct",
            "gemma-3-27b-instruct",
            "gemma-3-12b-instruct",
            "gemma-3-4b-instruct",
            "gemma-3-1b-instruct",
        ],
        "default_model": "gemini-2.5-flash",
        "rate_limit": "5 req/min (flash), 30 req/min (gemma)",
    },
    # --- NVIDIA NIM ---
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3-super-120b-a12b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nvidia/nemotron-nano-12b-v2-vl",
            "nvidia/nemotron-nano-9b-v2",
        ],
        "default_model": "nvidia/nemotron-3-ultra-550b-a55b",
        "rate_limit": "40 req/min",
        "requires_phone_verification": True,
    },
    # --- Mistral (La Plateforme) ---
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "api_key_env": "MISTRAL_API_KEY",
        "models": [
            "mistral-large-latest",
            "mistral-small-latest",
            "codestral-latest",
            "open-mistral-7b",
            "open-mixtral-8x7b",
        ],
        "default_model": "mistral-large-latest",
        "rate_limit": "25K-20M tokens/min depending on model",
        "requires_phone_verification": True,
        "requires_data_training_opt_in": True,
    },
    # --- Mistral Codestral ---
    "codestral": {
        "base_url": "https://codestral.mistral.ai/v1",
        "api_key_env": "CODESTRAL_API_KEY",
        "models": ["codestral"],
        "default_model": "codestral",
        "rate_limit": "30 req/min, 2000 req/day",
        "requires_phone_verification": True,
    },
    # --- HuggingFace Inference Providers ---
    "huggingface": {
        "base_url": "https://api-inference.huggingface.co/v1",
        "api_key_env": "HUGGINGFACE_API_KEY",
        "models": [
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "google/gemma-2-9b-it",
            "microsoft/Phi-3-mini-4k-instruct",
        ],
        "default_model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "rate_limit": "$0.10/month credits",
        "max_model_size_gb": 10,
    },
    # --- Vercel AI Gateway ---
    "vercel": {
        "base_url": "https://ai-gateway.vercel.sh/v1",
        "api_key_env": "VERCEL_AI_GATEWAY_KEY",
        "models": "varies by provider",
        "default_model": "auto",
        "rate_limit": "$5/month free tier",
    },
    # --- Kilo Gateway ---
    "kilo": {
        "base_url": "https://api.kilo.ai/v1",
        "api_key_env": None,  # No account needed for free models
        "models": [
            "cohere/north-mini-code",
            "kilo/auto-free",
            "kwaipilot/kat-coder-pro-v2.5",
            "inclusionai/ling-3.0-flash",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nvidia/nemotron-3-super-120b-a12b",
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3.5-content-safety",
            "openrouter/free-router",
            "poolside/laguna-m.1",
            "poolside/laguna-s-2.1",
            "poolside/laguna-xs-2.1",
            "stepfun/step-3.7-flash",
        ],
        "default_model": "kilo/auto-free",
        "rate_limit": "200 req/hour per IP shared",
        "uses_data_for_training": True,
    },
    # --- OpenCode Zen ---
    "opencode": {
        "base_url": "https://opencode.ai/api/v1",
        "api_key_env": "OPENCODE_API_KEY",
        "models": [
            "big-pickle",
            "deepseek-v4-flash-free",
            "mimo-v2.5-free",
            "laguna-s-2.1-free",
            "ling-3.0-flash-free",
            "north-mini-code-free",
            "nemotron-3-ultra-free",
        ],
        "default_model": "deepseek-v4-flash-free",
        "uses_data_for_improvement": True,
    },
    # --- Cerebras ---
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "api_key_env": "CEREBRAS_API_KEY",
        "models": [
            "gpt-oss-120b",
            "zai-glm-4.7",
            "gemma-4-31b",
        ],
        "default_model": "gpt-oss-120b",
        "rate_limit": "5 req/min, 30K tokens/min, 1M tokens/hour/day",
    },
    # --- Groq ---
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-safeguard-20b",
            "qwen/qwen3.6-27b",
            "compound",
            "compound-mini",
            "allam-2-7b",
            "meta-llama/llama-prompt-guard-2-22m",
            "meta-llama/llama-prompt-guard-2-86m",
        ],
        "default_model": "llama-3.3-70b-versatile",
        "rate_limit": "14,400 req/day (8B), 1,000 req/day (70B)",
    },
    # --- Cohere ---
    "cohere": {
        "base_url": "https://api.cohere.ai/v1",
        "api_key_env": "COHERE_API_KEY",
        "models": [
            "c4ai-aya-expanse-32b",
            "c4ai-aya-vision-32b",
            "command-a-03-2025",
            "command-a-plus-05-2026",
            "command-a-reasoning-08-2025",
            "command-a-translate-08-2025",
            "command-a-vision-07-2025",
            "command-r-08-2024",
            "command-r-plus-08-2024",
            "command-r7b-12-2024",
            "command-r7b-arabic-02-2025",
        ],
        "default_model": "command-r-plus-08-2024",
        "rate_limit": "20 req/min, 1000 req/month shared",
    },
    # --- Cloudflare Workers AI ---
    "cloudflare": {
        "base_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        "api_key_env": "CLOUDFLARE_API_KEY",
        "account_id_env": "CLOUDFLARE_ACCOUNT_ID",
        "models": [
            "@cf/aisingapore/gemma-sea-lion-v4-27b-it",
            "@cf/google/gemma-4-26b-a4b-it",
            "@cf/ibm-granite/granite-4.0-h-micro",
            "@cf/moonshotai/kimi-k2.6",
            "@cf/moonshotai/kimi-k2.7-code",
            "@cf/nvidia/nemotron-3-120b-a12b",
            "@cf/openai/gpt-oss-120b",
            "@cf/openai/gpt-oss-20b",
            "@cf/qwen/qwen3-30b-a3b-fp8",
            "@cf/zai-org/glm-4.7-flash",
            "@cf/zai-org/glm-5.2",
            "deepseek-r1-distill-qwen-32b",
            "gemma-2b-it-lora",
            "gemma-7b-it-lora",
            "llama-2-7b-chat-lora",
            "llama-3.1-8b-instruct-fp8",
            "llama-3.2-11b-vision-instruct",
            "llama-3.2-1b-instruct",
            "llama-3.2-3b-instruct",
            "llama-3.3-70b-instruct-fp8",
            "llama-4-scout-instruct",
            "llama-guard-3-8b",
            "mistral-7b-instruct-v0.2-lora",
            "mistral-small-3.1-24b-instruct",
            "qwen-2.5-coder-32b-instruct",
            "qwen-qwq-32b",
        ],
        "default_model": "@cf/meta-llama/llama-3.3-70b-instruct-fp8",
        "rate_limit": "10,000 neurons/day",
        "requires_account_id": True,
    },
    # --- Fireworks (trial credits) ---
    "fireworks": {
        "base_url": "https://api.fireworks.ai/inference/v1",
        "api_key_env": "FIREWORKS_API_KEY",
        "models": "various open models",
        "default_model": "auto",
        "trial_credits": "$1",
    },
    # --- Baseten (trial credits) ---
    "baseten": {
        "base_url": "https://app.baseten.co/v1",
        "api_key_env": "BASETEN_API_KEY",
        "models": "pay by compute time",
        "default_model": "auto",
        "trial_credits": "$30",
    },
    # --- Nebius (trial credits) ---
    "nebius": {
        "base_url": "https://api.studio.nebius.com/v1",
        "api_key_env": "NEBIUS_API_KEY",
        "models": "various open models",
        "default_model": "auto",
        "trial_credits": "$1",
    },
    # --- Novita (trial credits) ---
    "novita": {
        "base_url": "https://api.novita.ai/v3/openai",
        "api_key_env": "NOVITA_API_KEY",
        "models": "various open models",
        "default_model": "auto",
        "trial_credits": "$0.50 for 1 year",
    },
    # --- AI21 (trial credits) ---
    "ai21": {
        "base_url": "https://api.ai21.com/studio/v1",
        "api_key_env": "AI21_API_KEY",
        "models": ["jamba-family"],
        "default_model": "jamba-large",
        "trial_credits": "$10 for 3 months",
    },
    # --- Upstage (trial credits) ---
    "upstage": {
        "base_url": "https://api.upstage.ai/v1",
        "api_key_env": "UPSTAGE_API_KEY",
        "models": ["solar-pro", "solar-mini"],
        "default_model": "solar-pro",
        "trial_credits": "$10 for 3 months",
    },
    # --- NLP Cloud (trial credits) ---
    "nlpcloud": {
        "base_url": "https://api.nlpcloud.io",
        "api_key_env": "NLP_CLOUD_API_KEY",
        "models": "various open models",
        "default_model": "auto",
        "trial_credits": "$15",
        "requires_phone_verification": True,
    },
    # --- Alibaba Cloud Model Studio (trial credits) ---
    "alibaba": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "ALIBABA_API_KEY",
        "models": "various Qwen models",
        "default_model": "qwen-max",
        "trial_credits": "1M tokens/model for 90 days (Singapore endpoint)",
    },
    # --- Modal (trial credits) ---
    "modal": {
        "base_url": "https://api.modal.com/v1",
        "api_key_env": "MODAL_API_KEY",
        "models": "any supported model - pay by compute time",
        "default_model": "auto",
        "trial_credits": "$30/month on Starter plan",
    },
    # --- Inference.net (trial credits) ---
    "inferencenet": {
        "base_url": "https://api.inference.net/v1",
        "api_key_env": "INFERENCE_NET_API_KEY",
        "models": "various open models",
        "default_model": "auto",
        "trial_credits": "$1 + $25 on survey",
    },
    # --- Hyperbolic (trial credits) ---
    "hyperbolic": {
        "base_url": "https://api.hyperbolic.xyz/v1",
        "api_key_env": "HYPERBOLIC_API_KEY",
        "models": [
            "deepseek-v3-0324",
            "llama-3.3-70b-instruct",
            "deepseek-ai/deepseek-r1-0528",
            "qwen/qwen3-coder-480b-a35b-instruct",
        ],
        "default_model": "deepseek-v3-0324",
        "trial_credits": "$1",
    },
    # --- SambaNova Cloud (trial credits) ---
    "sambanova": {
        "base_url": "https://api.sambanova.ai/v1",
        "api_key_env": "SAMBANOVA_API_KEY",
        "models": [
            "deepseek-v3.1",
            "deepseek-v3.2",
            "gemma-4-31b-it",
            "gpt-oss-120b",
            "meta-llama-3.3-70b-instruct",
            "minimax-m2.7",
        ],
        "default_model": "deepseek-v3.1",
        "trial_credits": "$5 for 3 months",
    },
    # --- Scaleway (trial credits) ---
    "scaleway": {
        "base_url": "https://api.scaleway.ai/v1",
        "api_key_env": "SCALEWAY_API_KEY",
        "models": [
            "bge-multilingual-gemma2",
            "gemma-3-27b-instruct",
            "llama-3.3-70b-instruct",
            "pixtral-12b-2409",
            "whisper-large-v3",
            "devstral-2-123b-instruct-2512",
            "gemma-4-26b-a4b-it",
            "glm-5.2",
            "gpt-oss-120b",
            "holo2-30b-a3b",
            "mistral-medium-3.5-128b",
            "mistral-small-3.2-24b-instruct-2506",
            "qwen3-235b-a22b-instruct-2507",
            "qwen3-coder-30b-a3b-instruct",
            "qwen3-embedding-8b",
            "qwen3.5-397b-a17b",
            "qwen3.6-35b-a3b",
            "voxtral-small-24b-2507",
        ],
        "default_model": "llama-3.3-70b-instruct",
        "trial_credits": "1M free tokens + 60 min audio transcription",
    },
}

# Fallback order: primary working providers first, then free tier, then trial credits
FALLBACK_PROVIDER_ORDER = [
    "mistral",  # Working (has key in .env)
    "openrouter",  # Free tier, many models
    "gemini",  # Free tier, high limits on Gemma
    "groq",  # Free tier, fast
    "cerebras",  # Free tier, very fast
    "nvidia",  # Free tier, good models
    "kilo",  # No auth needed for free models
    "opencode",  # Free tier
    "huggingface",  # Small free credits
    "vercel",  # $5/month free tier
    "cloudflare",  # Free neurons/day
    "cohere",  # Free tier
    "codestral",  # Free while in beta
    "fireworks",  # Trial credits
    "baseten",  # Trial credits
    "nebius",  # Trial credits
    "novita",  # Trial credits
    "ai21",  # Trial credits
    "upstage",  # Trial credits
    "nlpcloud",  # Trial credits
    "alibaba",  # Trial credits
    "modal",  # Trial credits
    "inferencenet",  # Trial credits
    "hyperbolic",  # Trial credits
    "sambanova",  # Trial credits
    "scaleway",  # Trial credits
]

# Providers that need special handling (multiple API keys, account IDs, etc.)
SPECIAL_HANDLING_PROVIDERS = {
    "cloudflare": ["CLOUDFLARE_ACCOUNT_ID"],
    "vercel": [],  # Uses Vercel project env
    "kilo": [],  # No auth for free models
    "opencode": [],  # Uses OpenCode CLI
}


def _detect_provider() -> str:
    """
    Detect which LLM provider has an API key configured.
    Priority matches FALLBACK_PROVIDER_ORDER.
    """
    for provider in FALLBACK_PROVIDER_ORDER:
        config = FREE_PROVIDER_CONFIGS.get(provider, {})
        api_key_env = config.get("api_key_env")
        if api_key_env and os.environ.get(api_key_env):
            return provider
        # Special case: kilo and opencode don't need API keys for free models
        if provider in ["kilo", "opencode"]:
            return provider

    # Default to mistral (most likely to have key)
    return "mistral"


def _check_provider_available(provider: str) -> bool:
    """Check if a provider has its required credentials available."""
    config = FREE_PROVIDER_CONFIGS.get(provider, {})
    api_key_env = config.get("api_key_env")
    if not api_key_env:
        # No API key needed (kilo, opencode free models)
        return True
    return bool(os.environ.get(api_key_env))


def _get_provider_config(provider: str) -> Dict[str, Any]:
    """Get provider configuration with defaults."""
    return FREE_PROVIDER_CONFIGS.get(provider, {})


def create_chat_model_with_fallbacks(
    primary_provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    allowed_providers: Optional[List[str]] = None,
) -> Any:
    """
    Create a LangChain ChatModel with comprehensive fallback chain.

    Falls back through all available providers in FALLBACK_PROVIDER_ORDER.
    Only includes providers that have API keys configured (or don't need them).

    Args:
        primary_provider: Override auto-detection
        temperature: Sampling temperature
        max_tokens: Maximum tokens per response
        allowed_providers: Limit to specific providers (None = all available)

    Returns:
        LangChain BaseChatModel with fallback chain

    Raises:
        ValueError: If no providers are available
    """

    # Auto-detect primary if not specified
    if primary_provider is None:
        primary_provider = _detect_provider()

    # Build provider order: primary first, then fallback order
    provider_order = [p for p in FALLBACK_PROVIDER_ORDER if p != primary_provider]
    provider_order.insert(0, primary_provider)

    # Filter by allowed_providers if specified
    if allowed_providers:
        provider_order = [p for p in provider_order if p in allowed_providers]

    # Build models for available providers
    models = []
    for provider in provider_order:
        if not _check_provider_available(provider):
            continue
        model = _create_model(provider, temperature, max_tokens)
        if model is not None:
            models.append((provider, model))

    if not models:
        available = [p for p in FALLBACK_PROVIDER_ORDER if _check_provider_available(p)]
        raise ValueError(
            f"No LLM provider available. Configured providers: {available}. "
            f"Set at least one API key from: MISTRAL_API_KEY, OPENROUTER_API_KEY, "
            f"GEMINI_API_KEY, GROQ_API_KEY, CEREBRAS_API_KEY, NVIDIA_API_KEY, etc."
        )

    # Create fallback chain
    primary_provider_name, primary_model = models[0]
    fallback_models = [m for _, m in models[1:]]

    if not fallback_models:
        return primary_model

    # Log the fallback chain
    fallback_names = [name for name, _ in models[1:]]
    print(f"[LLM] Primary: {primary_provider_name}, Fallbacks: {fallback_names}")

    return primary_model.with_fallbacks(fallback_models)


def _create_model(provider: str, temperature: float, max_tokens: int):
    """Create a single provider model if API key is available."""
    config = _get_provider_config(provider)
    api_key_env = config.get("api_key_env")
    api_key = os.environ.get(api_key_env) if api_key_env else None

    # Skip if API key required but not available
    if api_key_env and not api_key:
        return None

    base_url = config.get("base_url")

    try:
        if provider == "mistral":
            from langchain_mistralai import ChatMistralAI

            return ChatMistralAI(
                model="mistral-large-latest",
                mistral_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "openrouter":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "google/gemma-4-26b-a4b-it:free"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
                default_headers={
                    "HTTP-Referer": "https://nebula-writer.app",
                    "X-Title": "Nebula-Writer",
                },
            )

        elif provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=config.get("default_model", "gemini-2.5-flash"),
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

        elif provider == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=config.get("default_model", "llama-3.3-70b-versatile"),
                groq_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "cerebras":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "gpt-oss-120b"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "nvidia":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "nvidia/nemotron-3-ultra-550b-a55b"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "kilo":
            from langchain_openai import ChatOpenAI

            # Kilo free models don't need API key
            return ChatOpenAI(
                model=config.get("default_model", "kilo/auto-free"),
                openai_api_key="dummy",  # Not used for free models
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "opencode":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "deepseek-v4-flash-free"),
                openai_api_key=api_key or "dummy",
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "huggingface":
            from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

            endpoint = HuggingFaceEndpoint(
                repo_id=config.get("default_model", "meta-llama/Meta-Llama-3-8B-Instruct"),
                huggingfacehub_api_token=api_key,
                temperature=temperature,
                max_new_tokens=max_tokens,
            )
            return ChatHuggingFace(llm=endpoint)

        elif provider == "vercel":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "cloudflare":
            from langchain_openai import ChatOpenAI

            account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
            cf_base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"
            return ChatOpenAI(
                model=config.get("default_model", "@cf/meta-llama/llama-3.3-70b-instruct-fp8"),
                openai_api_key=api_key,
                openai_api_base=cf_base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "cohere":
            from langchain_cohere import ChatCohere

            return ChatCohere(
                model=config.get("default_model", "command-r-plus-08-2024"),
                cohere_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "codestral":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "codestral"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "fireworks":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "accounts/fireworks/models/llama-v3p1-70b-instruct"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "baseten":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "nebius":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "novita":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "ai21":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "jamba-large"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "upstage":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "solar-pro"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "nlpcloud":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "alibaba":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "qwen-max"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "modal":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "inferencenet":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "auto"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "hyperbolic":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "deepseek-v3-0324"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "sambanova":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "deepseek-v3.1"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "scaleway":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.get("default_model", "llama-3.3-70b-instruct"),
                openai_api_key=api_key,
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    except ImportError as e:
        print(f"[LLM] Import error for {provider}: {e}")
        return None
    except Exception as e:
        print(f"[LLM] Error creating {provider} model: {e}")
        return None

    return None


def get_available_providers() -> List[Dict]:
    """Check which providers have API keys configured."""
    providers = []

    for provider in FALLBACK_PROVIDER_ORDER:
        config = _get_provider_config(provider)
        api_key_env = config.get("api_key_env")
        has_key = bool(os.environ.get(api_key_env)) if api_key_env else True

        providers.append(
            {
                "id": provider,
                "name": config.get("name", provider.title()),
                "available": has_key,
                "models": config.get("models", []),
                "default_model": config.get("default_model"),
                "rate_limit": config.get("rate_limit", "unknown"),
                "trial_credits": config.get("trial_credits"),
            }
        )

    return providers


def get_provider_models(provider: str) -> List[str]:
    """Get available models for a specific provider."""
    config = _get_provider_config(provider)
    return config.get("models", [])


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


# Backwards compatibility wrappers
def create_chat_model(provider: str = None, temperature: float = 0.7, max_tokens: int = 4096):
    """Backwards compatible wrapper for create_chat_model_with_fallbacks"""
    return create_chat_model_with_fallbacks(primary_provider=provider, temperature=temperature, max_tokens=max_tokens)


def count_tokens(text: str, model_name: str = "mistral-large-latest") -> int:
    """Rough token count approximation"""
    # Approximate: ~4 chars per token for English
    return len(text) // 4


if __name__ == "__main__":
    print("Available providers:", get_available_providers())
    print("Auto-detected primary:", _detect_provider())
