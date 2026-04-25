"""
Nebula-Writer Context Windowing System
Prevents token overflow by only including relevant context
"""
from typing import List, Dict, Set
from datetime import datetime, timedelta


class ContextWindow:
    """
    Manages context window for AI calls
    Selects only relevant story graph data for each request type
    AGGRESSIVE TOKEN LIMITS to prevent overflow
    """
    
    # Token budget per request type (conservative, well under 204800)
    BUDGETS = {
        "new_project": 10000,      # Very small - just idea
        "create_entity": 8000,     # Minimal context
        "update_entity": 8000,     # Minimal context
        "write_chapter": 40000,    # Chapter + recent history
        "revise_chapter": 50000,   # Chapter + specific context
        "answer_question": 15000,  # Targeted lookup
        "research_query": 12000,   # Research only
        "approve_chapter": 10000,  # Quick check
        "plot_direction": 30000,   # Compass + recent
        "add_comment": 10000,     # Comment-specific
        "general_chat": 12000,    # Just chat
        "idea_processing": 15000, # Q&A flow
    }
    
    # What to include per intent
    CONTEXT_SPECS = {
        "new_project": {
            "include_history": False,
            "include_entities": False,
            "include_chapters": False,
            "include_research": False,
            "include_conversation": True,  # last 5 turns
            "budget": 20000
        },
        "create_entity": {
            "include_history": False,
            "include_entities": True,  # last 10 only
            "include_chapters": False,
            "include_research": False,
            "include_conversation": True,  # last 3 turns
            "budget": 15000
        },
        "write_chapter": {
            "include_history": True,  # recent chapters only
            "include_entities": True,  # relevant characters
            "include_chapters": True,  # last 3 chapters
            "include_research": True,  # relevant research
            "include_conversation": True,  # last 5 turns
            "budget": 80000
        },
        "revise_chapter": {
            "include_history": True,
            "include_entities": True,
            "include_chapters": True,  # current chapter only
            "include_research": True,
            "include_conversation": True,
            "budget": 100000
        },
        "answer_question": {
            "include_history": False,
            "include_entities": True,  # relevant ones
            "include_chapters": False,
            "include_research": True,
            "include_conversation": True,
            "budget": 40000
        },
        "update_codex": {
            "include_history": False,
            "include_entities": True,
            "include_chapters": False,
            "include_research": False,
            "include_conversation": True,
            "budget": 20000
        }
    }
    
    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Rough token estimate (1 token ≈ 4 chars)"""
        return len(text) // 4
    
    @classmethod
    def build_context(cls, intent: str, db, conversation_history: List[Dict] = None, **kwargs) -> Dict:
        """
        Build optimized context for AI call
        Returns dict with context sections and total token count
        """
        spec = cls.CONTEXT_SPECS.get(intent, cls.CONTEXT_SPECS["general_chat"])
        context = {
            "sections": {},
            "total_tokens": 0,
            "budget": spec["budget"]
        }
        
        # 1. Conversation history (most recent)
        if spec["include_conversation"] and conversation_history:
            recent = conversation_history[-10:]  # last 10 turns
            # Convert to text
            conv_text = cls._format_conversation(recent)
            if cls.estimate_tokens(conv_text) < spec["budget"] // 3:
                context["sections"]["conversation"] = conv_text
                context["total_tokens"] += cls.estimate_tokens(conv_text)
        
        # 2. Entities (only relevant ones)
        if spec["include_entities"]:
            entities_text = cls._build_entities_context(db, kwargs.get("relevant_entity_ids"))
            if context["total_tokens"] + cls.estimate_tokens(entities_text) < spec["budget"]:
                context["sections"]["entities"] = entities_text
                context["total_tokens"] += cls.estimate_tokens(entities_text)
        
        # 3. Chapters (only recent/relevant)
        if spec["include_chapters"]:
            chapters_text = cls._build_chapters_context(db, kwargs.get("chapter_id"), kwargs.get("recent_count", 3))
            projected = context["total_tokens"] + cls.estimate_tokens(chapters_text)
            if projected < spec["budget"]:
                context["sections"]["chapters"] = chapters_text
                context["total_tokens"] += cls.estimate_tokens(chapters_text)
        
        # 4. Research (only relevant topics)
        if spec["include_research"]:
            research_text = cls._build_research_context(db, kwargs.get("research_topics"))
            projected = context["total_tokens"] + cls.estimate_tokens(research_text)
            if projected < spec["budget"]:
                context["sections"]["research"] = research_text
                context["total_tokens"] += cls.estimate_tokens(research_text)
        
        # Story context (compass state)
        if intent in ["write_chapter", "revise_chapter"]:
            compass_text = cls._build_compass_context(db)
            projected = context["total_tokens"] + cls.estimate_tokens(compass_text)
            if projected < spec["budget"]:
                context["sections"]["story_compass"] = compass_text
                context["total_tokens"] += cls.estimate_tokens(compass_text)
        
        return context
    
    @classmethod
    def _format_conversation(cls, turns: List[Dict]) -> str:
        """Format conversation history"""
        lines = ["CONVERSATION HISTORY:"]
        for turn in turns:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            lines.append(f"{role.upper()}: {content[:500]}")  # truncate long messages
        return "\n".join(lines)
    
    @classmethod
    def _build_entities_context(cls, db, entity_ids: List[int] = None) -> str:
        """Build entity context (limited)"""
        entities = db.get_entities()
        lines = ["CODEX - KEY ENTITIES:"]
        
        # If specific IDs given, filter
        if entity_ids:
            entities = [e for e in entities if e["id"] in entity_ids]
        else:
            # Only last 10 created (most recent)
            entities = sorted(entities, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
        
        for e in entities:
            attrs = db.get_attributes(e["id"])[:5]  # max 5 attrs
            lines.append(f"\n- {e['name']} ({e['type']})")
            if e.get("description"):
                lines.append(f"  Desc: {e['description'][:100]}")
            if attrs:
                lines.append("  Attrs: " + ", ".join([f"{a['key']}={a['value']}" for a in attrs]))
        
        return "\n".join(lines)
    
    @classmethod
    def _build_chapters_context(cls, db, chapter_id: int = None, recent_count: int = 3) -> str:
        """Build chapter context (recent only)"""
        chapters = db.get_chapters()
        lines = ["CHAPTER CONTEXT:"]
        
        if chapter_id:
            # Specific chapter
            chap = db.get_chapter(chapter_id=chapter_id)
            if chap:
                lines.append(f"\nCurrent Chapter {chap.get('number')}: {chap.get('title', 'Untitled')}")
                content = chap.get('content', '')[:2000]  # first 2k chars
                lines.append(content)
        else:
            # Recent chapters
            sorted_chaps = sorted(chapters, key=lambda x: x.get("number", 0), reverse=True)
            for chap in sorted_chaps[:recent_count]:
                lines.append(f"\nChapter {chap.get('number')}: {chap.get('title', 'Untitled')}")
                lines.append(f"Words: {chap.get('word_count', 0)}, Summary: {chap.get('summary', '')[:200]}")
        
        return "\n".join(lines)
    
    @classmethod
    def _build_research_context(cls, db, topics: List[str] = None) -> str:
        """Build research context (topic-based)"""
        from plot_manager import create_plot_manager
        pm = create_plot_manager()
        
        citations = []
        if topics:
            for topic in topics[:3]:  # max 3 topics
                citations.extend(pm.get_citations(topic))
        else:
            citations = pm.get_citations()[:10]  # only 10 most recent
        
        lines = ["RESEARCH CITATIONS:"]
        for c in citations[:5]:  # max 5 citations
            lines.append(f"\n- {c.get('fact', '')[:150]}")
            if c.get("source_url"):
                lines.append(f"  Source: {c['source_url'][:80]}")
        
        return "\n".join(lines)
    
    @classmethod
    def _build_compass_context(cls, db) -> str:
        """Build story compass state"""
        from plot_manager import create_plot_manager
        pm = create_plot_manager()
        
        tensions = pm.get_plot_threads()
        open_tensions = [t for t in tensions if t.get("status") == "open"]
        
        lines = ["STORY COMPASS:"]
        lines.append(f"Open tensions: {len(open_tensions)}")
        lines.append("Recent plot threads:")
        for t in open_tensions[:3]:
            lines.append(f"  - {t['title']} (planted Ch.{t.get('planted_chapter', '?')})")
        
        return "\n".join(lines)


def truncate_context_for_budget(context: Dict, max_budget: int) -> Dict:
    """
    If context exceeds budget, truncate from the end
    """
    if context["total_tokens"] <= max_budget:
        return context
    
    # Priority order: conversation > entities > chapters > research > compass
    sections = context["sections"]
    to_remove = []
    
    for section in ["compass", "research", "chapters", "entities", "conversation"]:
        if section in sections and context["total_tokens"] > max_budget:
            del sections[section]
            context["total_tokens"] = sum(ContextWindow.estimate_tokens(v) for v in sections.values())
    
    return context


def build_system_prompt(intent: str, context_type: str = "chat") -> str:
    """
    Build system prompt with context window awareness
    """
    base = "You are AutoNovelist, an AI novel writing assistant. "
    
    if context_type == "chat":
        base += "You are in Chat Mode - the user talks to you naturally. "
        base += "You understand their intent and update the Story Graph silently. "
        base += "Respond conversationally but concisely."
    else:
        base += "You are in Studio Mode - providing structured assistance."
    
    # Intent-specific guidance
    intent_guides = {
        "new_project": "Help the user flesh out their idea through natural Q&A. Ask 1 question at a time.",
        "write_chapter": "Write a scene of 1500-4000 words. Use the story compass for direction.",
        "revise_chapter": "Revise based on user feedback. Keep changes minimal and targeted.",
        "update_entity": "Update the Codex entry based on user's natural language request.",
        "answer_question": "Answer questions about the story world using the Codex and research."
    }
    
    if intent in intent_guides:
        base += " " + intent_guides[intent]
    
    return base


if __name__ == "__main__":
    print("Context Window System Ready")
    print("\nExample budgets:")
    for intent, budget in ContextWindow.BUDGETS.items():
        print(f"  {intent}: {budget:,} tokens")
    
    print("\nToken estimation test:")
    sample = "The detective walked into the room. He knew something was wrong. " * 100
    tokens = ContextWindow.estimate_tokens(sample)
    print(f"  4000 chars ≈ {tokens} tokens")
    print(f"  Rule of thumb: 1 token ≈ 4 characters")