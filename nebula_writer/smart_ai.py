"""
Nebula-Writer Smart AI Client with Context Windowing
Prevents token overflow by only sending relevant context
"""

import os
from typing import Dict, List

from nebula_writer.ai_client import AIClient
from nebula_writer.context_window import ContextWindow, truncate_context_for_budget


class SmartAIClient:
    """
    AI client that automatically manages context window size
    Uses selective retrieval instead of dumping everything
    """

    def __init__(self, provider: str = "gemini", api_key: str = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get(f"{provider.upper()}_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.client = AIClient(provider=provider, api_key=self.api_key)
        self.max_tokens = 204800  # Gemini 2.0 Flash limit
        self.safety_margin = 10000  # Reserve 10k for response

    def generate_with_context(
        self, intent: str, prompt: str, db, conversation_history: List[Dict] = None, extra_context: Dict = None
    ) -> str:
        """
        Generate with smart context windowing
        Only includes relevant story data based on intent
        """
        # Build minimal system prompt
        system_prompt = build_system_prompt(intent, "chat")

        # Build context sections
        context = ContextWindow.build_context(
            intent=intent, db=db, conversation_history=conversation_history or [], **extra_context or {}
        )

        # Truncate to safe budget
        safe_budget = self.max_tokens - self.safety_margin - ContextWindow.estimate_tokens(prompt + system_prompt)
        context = truncate_context_for_budget(context, safe_budget)

        # Construct final prompt
        final_prompt = self._construct_prompt(prompt, context)

        # Check final token count
        total = ContextWindow.estimate_tokens(system_prompt + final_prompt)
        if total > self.max_tokens - self.safety_margin:
            print(f"Warning: Context still large ({total} tokens). Truncating further.")
            # Emergency truncation - keep only conversation
            final_prompt = self._construct_minimal_prompt(prompt, context)

        # Generate
        try:
            return self.client.generate(final_prompt, system_prompt=system_prompt, temperature=0.7)
        except Exception as e:
            if "context length" in str(e).lower():
                # Fallback: ultra-minimal
                return self._generate_minimal(prompt)
            raise

    def _construct_prompt(self, user_prompt: str, context: Dict) -> str:
        """Build prompt from context sections"""
        sections = []

        # Always include conversation first (most recent)
        if "conversation" in context["sections"]:
            sections.append("=== RECENT CONVERSATION ===\n" + context["sections"]["conversation"])

        # Include other context based on availability
        order = ["entities", "chapters", "story_compass", "research"]
        for key in order:
            if key in context["sections"]:
                sections.append(f"\n=== {key.upper()} ===\n{context['sections'][key]}")

        sections.append(f"\n=== USER MESSAGE ===\n{user_prompt}")

        return "\n".join(sections)

    def _construct_minimal_prompt(self, user_prompt: str, context: Dict) -> str:
        """Ultra-minimal fallback"""
        return f"Context summary: {len(context['sections'])} sections available.\n\nUser: {user_prompt}"

    def _generate_minimal(self, prompt: str) -> str:
        """Generate with absolutely minimal context"""
        return "I need to process that, but the context is large. Please be more specific or start a fresh topic."

    def chat_response(self, message: str, history: List[Dict], db) -> str:
        """
        Simple chat interface - main entry for conversation mode
        """
        # Determine intent from message

        # Simple intent detection
        msg_lower = message.lower()
        if any(word in msg_lower for word in ["write", "generate", "draft"]):
            intent = "write_chapter"
        elif any(word in msg_lower for word in ["change", "update", "make"]):
            intent = "update_entity"
        elif any(word in msg_lower for word in ["what", "who", "where", "how"]):
            intent = "answer_question"
        else:
            intent = "general_chat"

        return self.generate_with_context(intent, message, db, history)


# Factory
_smart_client = None


def get_smart_ai_client() -> SmartAIClient:
    global _smart_client
    if _smart_client is None:
        _smart_client = SmartAIClient()
    return _smart_client


if __name__ == "__main__":
    print("Smart AI Client with Context Windowing")
    print("\nTest: estimating token counts")

    test_text = "A" * 1000
    tokens = ContextWindow.estimate_tokens(test_text)
    print(f"  1000 chars ≈ {tokens} tokens")
    print(f"  80,000 chars ≈ {ContextWindow.estimate_tokens('A' * 80000)} tokens")
    print("\nContext windowing active: prevents 200k+ token payloads")
