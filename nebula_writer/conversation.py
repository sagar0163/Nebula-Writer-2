import asyncio
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from nebula_writer.ai_writer import AIWriter


class IntentType(Enum):
    """User message intent classification"""

    NEW_PROJECT = "new_project"
    CREATE_ENTITY = "create_entity"
    UPDATE_ENTITY = "update_entity"
    WRITE_CHAPTER = "write_chapter"
    REVISE_CHAPTER = "revise_chapter"
    ANSWER_QUESTION = "answer_question"
    RESEARCH_QUERY = "research_query"
    APPROVE_CHAPTER = "approve_chapter"
    ADD_COMMENT = "add_comment"
    PLOT_DIRECTION = "plot_direction"
    GENERAL_CHAT = "general_chat"
    CONSISTENCY_CHECK = "consistency_check"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedIntent:
    """Result of intent classification"""

    intent: IntentType
    confidence: float
    extracted_info: Dict
    needs_clarification: bool = False
    clarification_question: str = ""


class ConversationEngine:
    """
    Main conversation router for Chat Mode
    Understands user intent and routes to appropriate subsystem
    """

    def __init__(self, db, ai_writer=None):
        self.db = db
        self.ai = ai_writer or AIWriter()
        # Load history from DB on init
        self.conversation_history: List[Dict] = self.db.load_conversation()
        self.current_focus: Optional[Dict] = None  # What we're currently working on

    def classify_intent(self, message: str, project_state: Dict = None) -> ClassifiedIntent:
        """
        Classify user message intent
        Uses keyword matching + AI classification for ambiguous cases
        """
        message_lower = message.lower().strip()

        # Keyword-based fast path
        patterns = {
            IntentType.NEW_PROJECT: [
                r"^(i want to|let's|start|begin|new|write) (write|create|build|start) (a|the)",
                r"^(idea|concept|brainstorm)",
                r"^(detective|protagonist|character) (in|from|who)",
            ],
            IntentType.CREATE_ENTITY: [
                r"^(add|create|new|make) (a|an) (character|person|location|place|item|thing)",
                r"^(there'?s) (also|also a|a)",
            ],
            IntentType.UPDATE_ENTITY: [
                r"(make|change|update|set) (him|her|it|them|this) (to|as|into)",
                r"(older|younger| taller|shorter|richer|poorer)",
                r"(change|update|modify|adjust)",
            ],
            IntentType.WRITE_CHAPTER: [
                r"(write|generate|create|draft) (chapter|the chapter|next)",
                r"(go ahead|start writing|begin chapter)",
                r"(write it|let'?s write)",
            ],
            IntentType.REVISE_CHAPTER: [
                r"(revise|rewrite|change|fix|edit) (this|the) (chapter|section|part)",
                r"(this feels|it seems|too slow|too fast|abrupt)",
                r"(extend|shorten|cut)",
            ],
            IntentType.ANSWER_QUESTION: [
                r"^(what|who|where|when|why|how) (do we|does|is|are|was)",
                r"^(tell me about|explain|describe)",
                r"^(i don'?t understand|what'?s|clarify)",
            ],
            IntentType.RESEARCH_QUERY: [
                r"(research|look up|search|find out about|what do we know)",
                r"(historical|accurate|factual|actually)",
            ],
            IntentType.APPROVE_CHAPTER: [
                r"(yes|looks good|great| perfect|approve|keep going)",
                r"(this is good|i like it|proceed)",
                r"(forward|next|continue)",
            ],
            IntentType.PLOT_DIRECTION: [
                r"(don'?t reveal|skip|jump|avoid|instead)",
                r"(change|redirect|different)",
                r"(ending|conclusion|final)",
            ],
            IntentType.ADD_COMMENT: [
                r"(comment|note|feedback|suggestion)",
                r"(should be|would be better if)",
            ],
            IntentType.CONSISTENCY_CHECK: [
                r"(audit|consistency|conflict|contradiction|check|verify|logic|issue)",
                r"(is it consistent|any issues|check for conflicts)",
            ],
        }

        # Check each intent
        for intent_type, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, message_lower):
                    return ClassifiedIntent(
                        intent=intent_type, confidence=0.8, extracted_info=self._extract_info(message, intent_type)
                    )

        # Use AI for ambiguous cases (Moved to process_message for async support)
        return ClassifiedIntent(intent=IntentType.GENERAL_CHAT, confidence=0.5, extracted_info={})

    def _extract_info(self, message: str, intent: IntentType) -> Dict:
        """Extract structured info from message"""
        info = {}

        if intent == IntentType.CREATE_ENTITY:
            # Extract entity type
            if "character" in message.lower():
                info["entity_type"] = "character"
            elif "location" in message.lower():
                info["entity_type"] = "location"
            else:
                info["entity_type"] = "item"

            # Extract name (capitalized words)
            words = message.split()
            caps = [w for w in words if w[0].isupper() and len(w) > 1 and w.isalpha()]
            if caps:
                info["name"] = caps[0]

        elif intent == IntentType.UPDATE_ENTITY:
            # Extract attribute changes
            if "older" in message.lower() or "younger" in message.lower():
                info["attribute"] = "age"
            elif "taller" in message.lower() or "shorter" in message.lower():
                info["attribute"] = "height"

        elif intent == IntentType.WRITE_CHAPTER:
            # Extract word count if specified
            match = re.search(r"(\d+)\s*(words|word count)", message.lower())
            if match:
                info["word_count"] = int(match.group(1))

        return info

    async def _ai_classify_intent(self, message: str, project_state: Dict) -> ClassifiedIntent:
        """Use AI to classify ambiguous intent"""
        prompt = f"""
Classify this user message into one intent type:

User message: "{message}"

Available intents:
- new_project: Starting a new novel idea
- create_entity: Adding character/location/item
- update_entity: Changing entity attributes
- write_chapter: Requesting chapter generation
- revise_chapter: Asking to revise existing chapter
- answer_question: Asking about story details
- research_query: Wanting to research something
- approve_chapter: Approving current chapter
- plot_direction: Changing story direction
- add_comment: Leaving feedback/comment
- consistency_check: Auditing story for contradictions
- general_chat: Everything else

Also extract any relevant info (entity names, attributes, etc.) in JSON format.

Respond as: intent|confidence|{{"key": "value"}}
        """

        try:
            # Use 'architect' agent for intent classification
            response = await self.ai.generate(
                prompt,
                system_prompt="You are a story project assistant. Classify the user intent.",
                role="architect",
                temperature=0.1,
            )
            parts = response.strip().split("|")
            if len(parts) >= 2:
                intent_name = parts[0].strip()
                confidence = float(parts[1])
                try:
                    import json

                    extracted = json.loads(parts[2]) if len(parts) > 2 else {}
                except:
                    extracted = {}

                try:
                    intent = IntentType(intent_name)
                except:
                    intent = IntentType.GENERAL_CHAT

                return ClassifiedIntent(intent, confidence, extracted)
        except:
            pass

        return ClassifiedIntent(IntentType.UNKNOWN, 0.3, {})

    async def process_message(self, message: str, project_state: Dict = None) -> Dict:
        """
        Main entry point - process user message
        Returns AI response and any actions taken
        Uses context windowing to prevent token overflow
        """
        # Add to history
        self.conversation_history.append({"role": "user", "content": message, "timestamp": datetime.now().isoformat()})

        # Classify intent (deterministic)
        intent = self.classify_intent(message, project_state)

        # If unknown, try AI classification
        if intent.intent == IntentType.GENERAL_CHAT and project_state:
            ai_intent = await self._ai_classify_intent(message, project_state)
            if ai_intent.confidence > 0.6:
                intent = ai_intent

        # Route to appropriate handler
        response = await self.route_intent(intent, message, project_state)

        # Add AI response to history (truncated for token savings)
        self.conversation_history.append(
            {
                "role": "assistant",
                "content": response["message"][:500],  # Truncate in memory
                "timestamp": datetime.now().isoformat(),
                "actions": response.get("actions", []),
            }
        )

        # Save to DB
        self.db.save_conversation(self.conversation_history)

        return response

    async def route_intent(self, intent: ClassifiedIntent, message: str, state: Dict) -> Dict:
        """Route to appropriate handler"""
        handlers = {
            IntentType.NEW_PROJECT: self._handle_new_project,
            IntentType.CREATE_ENTITY: self._handle_create_entity,
            IntentType.UPDATE_ENTITY: self._handle_update_entity,
            IntentType.WRITE_CHAPTER: self._handle_write_chapter,
            IntentType.REVISE_CHAPTER: self._handle_revise_chapter,
            IntentType.ANSWER_QUESTION: self._handle_question,
            IntentType.RESEARCH_QUERY: self._handle_research_query,
            IntentType.APPROVE_CHAPTER: self._handle_approve,
            IntentType.PLOT_DIRECTION: self._handle_plot_direction,
            IntentType.ADD_COMMENT: self._handle_comment,
            IntentType.CONSISTENCY_CHECK: self._handle_consistency_check,
            IntentType.GENERAL_CHAT: self._handle_general_chat,
        }

        handler = handlers.get(intent.intent, self._handle_unknown)
        if asyncio.iscoroutinefunction(handler):
            return await handler(message, intent, state)
        return handler(message, intent, state)

    def _handle_new_project(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Start new project - trigger Q&A flow"""
        from nebula_writer.idea_processor import IdeaProcessor

        processor = IdeaProcessor()
        if not state or not state.get("processor"):
            result = processor.process_idea(message)
            return {
                "message": f"Great idea! Let me ask a few questions to understand your vision.\n\n{result['questions'][0]['question']}",
                "actions": [{"type": "start_qa", "data": result}],
                "ui_update": {"show_qa": True, "current_question": result["questions"][0]},
            }

        return {"message": "Project already started. Let's continue building."}

    def _handle_create_entity(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Create new entity"""
        info = intent.extracted_info
        entity_type = info.get("entity_type", "character")
        name = info.get("name", "New Character")

        # Create entity
        entity_id = self.db.add_entity(name, entity_type)

        return {
            "message": f"Created {entity_type} '{name}' in the Codex. I've given them a basic profile. Would you like to add any specific details?",
            "actions": [{"type": "entity_created", "entity_id": entity_id, "entity_type": entity_type, "name": name}],
            "ui_update": {"refresh_codex": True},
        }

    def _handle_update_entity(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Update entity attribute"""
        # This needs more sophistication - for now, acknowledge
        return {
            "message": "I'll update the character profile based on your note. Let me make that change...",
            "actions": [{"type": "entity_update_pending", "details": message}],
            "ui_update": {"refresh_codex": True},
        }

    def _handle_write_chapter(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Write a chapter"""
        word_count = intent.extracted_info.get("word_count", 2500)

        # Get lookahead cards
        from nebula_writer.outline_engine import create_evolution_engine

        engine = create_evolution_engine()
        cards = engine.get_lookahead_cards()

        if cards:
            next_card = cards[0]
            return {
                "message": f"Writing Chapter {next_card['chapter_num']} based on the lookahead. Target: ~{word_count} words.\n\nChapter direction: {next_card['scene_intention']}\n\nThis will take about 60 seconds...",
                "actions": [{"type": "chapter_generation_started", "word_count": word_count, "direction": next_card}],
                "ui_update": {"show_generation": True},
            }
        else:
            return {
                "message": "Let me generate the rolling lookahead first, then write the chapter.",
                "actions": [{"type": "generate_lookahead_first"}],
            }

    def _handle_revise_chapter(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Revise current chapter"""
        return {
            "message": "I'll revise the chapter based on your feedback. Let me address that...",
            "actions": [{"type": "chapter_revision_started", "feedback": message}],
            "ui_update": {"show_revision": True},
        }

    async def _handle_question(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Answer question about story using RAG and AI"""
        # 1. Semantic search for context
        from nebula_writer.memory import MemorySystem

        memory = MemorySystem()

        # Search entities and chapters
        entity_context = memory.search_entities(message, n_results=3)
        chapter_context = memory.search_chapters(message, n_results=2)

        context_str = "RELEVANT CONTEXT:\n"
        for e in entity_context:
            context_str += f"- Entity: {e['metadata'].get('name')} ({e['metadata'].get('type')}): {e['document']}\n"
        for c in chapter_context:
            context_str += f"- Chapter {c['metadata'].get('chapter_id')} Summary: {c['document']}\n"

        # 2. Generate response with AI
        system_prompt = f"""You are the Nebula-Writer Story Oracle.
Your goal is to answer questions about the user's novel based on the provided context.
If the information is not in the context, say you don't know yet, but offer to help brainstorm it.

{context_str}
"""
        try:
            response = await self.ai.generate(message, system_prompt=system_prompt, role="architect", temperature=0.3)
            return {
                "message": response,
                "actions": [{"type": "rag_query", "context_used": True}],
            }
        except Exception as e:
            # Fallback to simple matching if AI fails
            entities = self.db.get_entities()
            for e in entities:
                if e["name"].lower() in message.lower():
                    attrs = self.db.get_attributes(e["id"])
                    return {
                        "message": f"[Fallback] {e['name']}: {e.get('description', 'No description')}\nAttributes: {', '.join([a['key'] + ': ' + a['value'] for a in attrs])}",
                        "actions": [],
                    }
            return {
                "message": "I'm having trouble accessing my creative core right now, but I'm here to help with your novel! You can ask me about characters, plot, or say 'write the next chapter'.",
                "actions": [],
            }

    def _handle_research_query(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Handle research query"""
        from nebula_writer.research import ResearchEngine

        # Extract topic from message
        topic = message.replace("research", "").replace("look up", "").replace("search", "").strip()

        engine = ResearchEngine()
        results = engine.search(topic, num_results=3)

        if results:
            summary = "\n".join([f"- {r.title}: {r.snippet[:200]}" for r in results[:2]])
            return {
                "message": f"I found some information:\n\n{summary}\n\nWould you like me to add any of this to the research citations?",
                "actions": [{"type": "research_completed", "results_count": len(results)}],
                "ui_update": {"refresh_research": True},
            }
        else:
            return {
                "message": "I couldn't find much on that topic. Would you like me to try different search terms?",
                "actions": [],
            }

    def _handle_approve(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Approve current chapter"""
        return {
            "message": "Chapter approved! I'll generate the next lookahead and continue writing.",
            "actions": [{"type": "chapter_approved"}],
            "ui_update": {"refresh_chapters": True, "regenerate_lookahead": True},
        }

    def _handle_plot_direction(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Handle story direction change"""
        from nebula_writer.outline_engine import create_evolution_engine

        engine = create_evolution_engine()

        # Trigger redirect
        result = engine.redirect_story("user_redirect", message)

        return {
            "message": f"I understand you want to change direction. {result.get('narrative_debt', ['No issues'])[0] if result.get('narrative_debt') else 'I&apos;ll recalculate the lookahead.'} The rolling lookahead has been updated.",
            "actions": [{"type": "story_redirect", "details": result}],
            "ui_update": {"refresh_lookahead": True},
        }

    def _handle_comment(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Handle inline comment-style feedback"""
        return {
            "message": "I've noted your feedback. Let me incorporate that into the current chapter.",
            "actions": [{"type": "comment_received", "comment": message}],
            "ui_update": {"needs_revision": True},
        }

    async def _handle_consistency_check(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Audit the story for consistency issues using AI and structural audit"""
        from nebula_writer.ripple_checker import create_ripple_checker

        checker = create_ripple_checker(self.db, self.ai)

        # Get last chapter
        chapters = self.db.get_chapters()
        last_chapter_content = chapters[-1]["content"] if chapters else ""

        # Perform deeper analysis
        # We'll ask the ripple checker to analyze the "consistency of the latest manuscript"
        report = await checker.analyze_change(
            "Verify consistency of current manuscript against the Codex facts.",
            context={"manuscript": last_chapter_content[:2000]},
        )

        issues = report.get("structural_contradictions", [])
        ripples = report.get("predicted_ripples", [])

        if not issues and not ripples:
            return {
                "message": "I've analyzed the story elements. Everything aligns with the Codex facts! No contradictions or logic gaps detected.",
                "actions": [{"type": "consistency_audit_completed", "status": "clear"}],
            }

        # Combine issues and ripples into a helpful response
        message_out = "I've performed a Narrative Ripple Analysis. Here's what I found:\n\n"

        if issues:
            message_out += "**Contradictions Found:**\n"
            for issue in issues[:3]:
                # Format from StoryAuditor result
                msg = issue.get("message") or issue.get("description") or "General conflict"
                message_out += f"- {msg}\n"

        if ripples:
            message_out += "\n**Potential Narrative Gaps:**\n"
            for ripple in ripples[:3]:
                message_out += f"- {ripple['target']}: {ripple['effect']} (Severity: {ripple['severity']})\n"

        return {
            "message": message_out + "\nWould you like me to help you resolve these conflicts?",
            "actions": [{"type": "consistency_audit_completed", "status": "issues_found", "report": report}],
            "ui_update": {"show_consistency_modal": True},
        }

    async def _handle_general_chat(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """General conversation"""
        prompt = f"You are AutoNovelist AI assistant. User says: '{message}'. Provide helpful, conversational response about their novel project."

        try:
            # Use 'writer' agent for general chat
            response = await self.ai.generate(prompt, role="writer", temperature=0.7)
            return {"message": response, "actions": []}
        except:
            return {
                "message": "I'm your creative co-pilot for this novel. I can help with character profiles, plot brainstorming, and identifying consistency issues. What's on your mind?",
                "actions": [],
            }

    def _handle_unknown(self, message: str, intent: ClassifiedIntent, state: Dict) -> Dict:
        """Handle unclear intent"""
        return {
            "message": "I'm not sure what you mean. You can say things like:\n- 'Add a character named Ravi'\n- 'Write Chapter 1'\n- 'What do we know about Mumbai?'\n- 'Make it darker'\n\nOr just tell me what you're thinking.",
            "actions": [],
        }

    def get_conversation_history(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation"""
        return self.conversation_history[-limit:]

    def clear_history(self):
        """Clear conversation"""
        self.conversation_history = []


# Global conversation engine (initialized on app start)
_conversation_engine: Optional[ConversationEngine] = None


def get_conversation_engine() -> ConversationEngine:
    """Get or create conversation engine"""
    global _conversation_engine
    if _conversation_engine is None:
        from main import db  # Import from main

        _conversation_engine = ConversationEngine(db)
    return _conversation_engine


if __name__ == "__main__":
    print("Conversation Engine Ready")
    print("\nTest scenarios:")
    print("  'A detective in 1920s Shanghai' -> new_project")
    print("  'Add a character named Chen Wei' -> create_entity")
    print("  'Write Chapter 1' -> write_chapter")
    print("  'What do we know about the detective?' -> answer_question")
