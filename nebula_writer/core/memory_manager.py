"""
Nebula-Writer Memory Manager — LangChain-powered context assembly.
Replaces character-count heuristics with model-aware token counting.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from nebula_writer.core.narrative_state_engine import NarrativeSnapshot
from nebula_writer.models import create_chat_model, count_tokens


class MemoryManager:
    """
    Context assembly with LangChain token-aware budgeting.
    Priorities: Core (Rules) > Active (Recent) > Compressed (Summaries).
    """

    PRIORITIES = {
        "ANCHORS": 1.0,
        "TENSIONS": 0.9,
        "CORE_ENTITIES": 0.8,
        "RECENT_CHAPTERS": 0.7,
        "WORLD_RULES": 0.7,
        "BACKGROUND": 0.4,
    }

    def __init__(self, token_limit: int = 120000, model: BaseChatModel | None = None):
        self.token_limit = token_limit
        self.model = model or create_chat_model()
        self.hard_constraints = []

    def build_context(self, snapshot: NarrativeSnapshot, user_input: str = "") -> str:
        sections = [
            self._format_hard_constraints(snapshot),
            self._trigger_recall(snapshot, user_input),
            self._format_core_memory(snapshot),
            self._format_active_memory(snapshot),
            self._format_compressed_memory(snapshot),
        ]
        if user_input:
            sections.append(f"USER REQUEST: {user_input}")

        full_context = "\n\n".join(sections)
        return self._prune_to_limit(full_context)

    def _format_hard_constraints(self, snapshot: NarrativeSnapshot) -> str:
        anchors = "\n".join([f"- {a['description']}" for a in getattr(snapshot, "anchors", [])])
        critical_rules = "\n".join([f"- {r['rule']}" for r in snapshot.world_rules if r.get("critical")])
        return f"### STORY ANCHORS (NON-NEGOTIABLE)\n{anchors}\n\n### CRITICAL RULES\n{critical_rules}"

    def _trigger_recall(self, snapshot: NarrativeSnapshot, user_input: str) -> str:
        recalled = []
        for entity in snapshot.key_entities:
            if entity["name"].lower() in user_input.lower():
                recalled.append(f"RECALLED PROFILE [{entity['name']}]: {entity.get('description', '')}")
        return "\n".join(recalled) if recalled else ""

    def _format_core_memory(self, snapshot: NarrativeSnapshot) -> str:
        rules = "\n".join([f"- {r['rule']}" for r in snapshot.world_rules])
        return f"### CORE WORLD RULES\n{rules}"

    def _format_active_memory(self, snapshot: NarrativeSnapshot) -> str:
        tensions = "\n".join([f"- {t['description']}" for t in snapshot.unresolved_tensions])
        entities = "\n".join([f"- {e['name']}: {e.get('description', '')[:100]}" for e in snapshot.key_entities])
        return f"### ACTIVE TENSIONS\n{tensions}\n\n### KEY CHARACTERS\n{entities}"

    def _format_compressed_memory(self, snapshot: NarrativeSnapshot) -> str:
        return f"### RECENT SUMMARY\n{snapshot.current_chapter_summary}"

    def _prune_to_limit(self, text: str) -> str:
        """Prune using LangChain model token counting instead of char heuristic."""
        try:
            tokens = count_tokens(self.model, text)
            if tokens <= self.token_limit:
                return text
        except Exception:
            pass
        char_limit = self.token_limit * 4
        if len(text) <= char_limit:
            return text
        return text[:char_limit] + "... [TRUNCATED]"

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4
