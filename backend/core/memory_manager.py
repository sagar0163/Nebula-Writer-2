"""
Nebula-Writer Memory Manager (Refactored from ContextWindow)
Manages token budgets with importance-based prioritization.
"""

from core.narrative_state_engine import NarrativeSnapshot


class MemoryManager:
    """
    Upgraded context system with priority-based inclusion.
    Layers: Core (Rules) > Active (Recent) > Compressed (Summaries).
    """

    # Priority-based Token Budgeting
    PRIORITIES = {
        "ANCHORS": 1.0,
        "TENSIONS": 0.9,
        "CORE_ENTITIES": 0.8,
        "RECENT_CHAPTERS": 0.7,
        "WORLD_RULES": 0.7,
        "BACKGROUND": 0.4,
    }

    def __init__(self, token_limit: int = 120000):
        self.token_limit = token_limit

    def build_context(self, snapshot: NarrativeSnapshot, user_input: str = "") -> str:
        """
        Builds optimized context string based on snapshot priorities.
        """
        sections = []

        # 1. CORE MEMORY (Highest Priority)
        sections.append(self._format_core_memory(snapshot))

        # 2. ACTIVE MEMORY
        sections.append(self._format_active_memory(snapshot))

        # 3. COMPRESSED MEMORY
        sections.append(self._format_compressed_memory(snapshot))

        # 4. CURRENT INTENT
        if user_input:
            sections.append(f"USER REQUEST: {user_input}")

        full_context = "\n\n".join(sections)
        return self._prune_to_limit(full_context)

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
        """Dynamic pruning based on character count (approximate tokens)."""
        char_limit = self.token_limit * 4
        if len(text) <= char_limit:
            return text

        # In a real implementation, this would prune by section priority
        return text[:char_limit] + "... [TRUNCATED]"

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4
