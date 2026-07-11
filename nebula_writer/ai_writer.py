"""Nebula-Writer AI Module — LangChain-powered writing engine.

Replaces the raw provider SDK calls with LangChain ChatModel instances
that support automatic fallbacks, structured output, and LangSmith tracing.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from nebula_writer.models import create_chat_model_with_fallbacks


class AIWriter:
    """AI Writer powered by LangChain ChatModel with automatic fallback chain.

    Preserves the same public API as the original for backwards compatibility.
    """

    def __init__(self, gemini_key: Optional[str] = None, hf_token: Optional[str] = None):
        # Ensure .env is loaded so env vars are available
        from dotenv import load_dotenv
        load_dotenv()

        self.gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY")
        self.hf_token = hf_token or os.environ.get("HUGGINGFACE_API_KEY")

        from nebula_writer.models import _detect_provider

        primary = _detect_provider()

        self.model: BaseChatModel = create_chat_model_with_fallbacks(
            primary_provider=primary,
            temperature=0.7,
            max_tokens=4096,
        )

        # Style learner (set externally for backwards compat)
        self.style_learner = None
        self.style_learner_db = None

        # Worker metadata (kept for backwards compat with /api/system/workers)
        self.worker_metadata = [
            {"name": "LangChain-Gemini", "url": "gemini-2.0-flash", "status": "ready", "usage_count": 0},
        ]

    def get_worker_status(self) -> List[Dict[str, Any]]:
        return self.worker_metadata

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        return await self._generate(system_prompt or "You are a helpful assistant.", prompt, temperature, max_tokens)

    async def _generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.8,
        max_tokens: int = 2000,
    ) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = await self.model.ainvoke(messages, {"temperature": temperature, "max_tokens": max_tokens})
        return response.content

    # ── Prompt templates ──────────────────────────────────────────

    _WRITE_SCENE_TEMPLATE = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("{context}"),
        HumanMessagePromptTemplate.from_template(
            "Write a scene based on this beat:\n\"{beat}\"\n\nTarget length: ~{word_count} words.\n\n"
            "STYLE AND PACING GUIDANCE:\n{style_guidance}\n\nWrite the scene now:"
        ),
    ])

    _REWRITE_TEMPLATE = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("You are a versatile editor and writer. Rewrite the user's text exactly as requested."),
        HumanMessagePromptTemplate.from_template("{style_prompt}\n\nRewrite:\n{text}"),
    ])

    _DESCRIBE_TEMPLATE = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("You are a descriptive writer focusing on sensory details."),
        HumanMessagePromptTemplate.from_template(
            "Generate a vivid sensory description for **{name}** ({type}).\n\n"
            "Details: {description}\n"
            "Attributes: {attributes}\n\n"
            "Include smell, touch, sound, and sight. Make it immersive:"
        ),
    ])

    _SHOW_NOT_TELL_TEMPLATE = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a writing coach specializing in the 'Show, Don't Tell' technique."
        ),
        HumanMessagePromptTemplate.from_template(
            "Convert this telling prose to showing (physical actions/behaviors instead of emotions):\n\n"
            "{text}\n\nRewrite with physical actions that convey the same emotions:"
        ),
    ])

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with Codex context.
        
        Preserves the same format as the original for backwards compatibility.
        """
        prompt_parts = [
            "You are Nebula-Writer, an AI fiction writing assistant. You write immersive, engaging prose.",
            "",
            "IMPORTANT: You have access to the story's Codex (database). Use these facts accurately:",
            "",
        ]

        if context.get("entities"):
            prompt_parts.append("## ENTITIES")
            for e in context["entities"]:
                attrs = ", ".join([f"{a['key']}: {a['value']}" for a in e.get("attributes", [])])
                line = f"- **{e['name']}** ({e['type']}): {e.get('description', 'N/A')}"
                if attrs:
                    line += f" | {attrs}"
                prompt_parts.append(line)

        if context.get("relationships"):
            prompt_parts.append("")
            prompt_parts.append("## RELATIONSHIPS")
            for r in context["relationships"]:
                prompt_parts.append(f"- {r['from_name']} → {r['relationship_type']} → {r['to_name']}")

        if context.get("recent_events"):
            prompt_parts.append("")
            prompt_parts.append("## RECENT EVENTS")
            for ev in context["recent_events"][-5:]:
                ch = f" (Ch. {ev['chapter']})" if ev.get("chapter") else ""
                prompt_parts.append(f"- {ev['title']}{ch}: {ev.get('description', '')}")

        prompt_parts.append("")
        prompt_parts.append("Write in third person, past tense. Immerse readers with sensory details.")
        prompt_parts.append("Never contradict established facts from the Codex.")

        if self.style_learner and self.style_learner_db:
            try:
                style_addition = self.style_learner.get_style_prompt_addition()
                if style_addition:
                    prompt_parts.append("")
                    prompt_parts.append(style_addition)
            except Exception:
                pass

        return "\n".join(prompt_parts)

    def get_context(
        self,
        db,
        entity_ids: Optional[List[int]] = None,
        chapter: Optional[int] = None,
        max_entities: int = 5,
        max_events: int = 3,
    ) -> Dict[str, Any]:
        """Retrieve context from Codex with limits to prevent token overflow.
        
        Preserves the exact same behavior as the original.
        """
        context: Dict[str, Any] = {"entities": [], "relationships": [], "recent_events": [], "chapters": []}

        all_entities = db.get_entities()
        if entity_ids:
            entities = [e for e in all_entities if e["id"] in entity_ids][:max_entities]
        else:
            entities = all_entities[:max_entities]

        for e in entities:
            e["attributes"] = db.get_attributes(e["id"])[:3]
            if "description" in e and len(e["description"]) > 200:
                e["description"] = e["description"][:200] + "..."
            context["entities"].append(e)

        all_rels = db.get_relationships()
        if entity_ids:
            rels = [r for r in all_rels if r["from_entity_id"] in entity_ids or r["to_entity_id"] in entity_ids][:10]
        else:
            rels = all_rels[:10]
        context["relationships"] = rels

        if chapter:
            # Pass both chapter (number) and chapter_id (UUID) to get_events
            # This handles both old calls (integer chapter number) and new calls (UUID)
            if isinstance(chapter, str) and len(chapter) > 10 and '-' in chapter:
                # It's a UUID, pass as chapter_id
                events = db.get_events(chapter_id=chapter)[:max_events]
            else:
                # It's an integer chapter number
                events = db.get_events(chapter=chapter)[:max_events]
        else:
            events = []
        context["recent_events"] = events

        if chapter:
            # Handle both UUID and integer chapter references
            if isinstance(chapter, str) and len(chapter) > 10 and '-' in chapter:
                chap = db.get_chapter(chapter_id=chapter)
            else:
                chap = db.get_chapter(number=chapter)
            if chap:
                chap_summ = {
                    "number": chap.get("number"),
                    "title": chap.get("title", ""),
                    "summary": chap.get("summary", "")[:300] if chap.get("summary") else "",
                }
                context["chapters"].append(chap_summ)

        return context

    async def write_scene(
        self,
        db,
        beat: str,
        word_count: int = 500,
        entity_ids: Optional[List[int]] = None,
        chapter: Optional[int] = None,
        pacing: Optional[str] = None,
        pov: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> str:
        context = self.get_context(db, entity_ids, chapter)
        system_prompt = self._build_system_prompt(context)

        style_guidance = self._build_style_guidance(pacing, pov, tone)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"Write a scene based on this beat:\n\"{beat}\"\n\n"
                f"Target length: ~{word_count} words.\n\n"
                f"STYLE AND PACING GUIDANCE:\n{style_guidance}\n\n"
                f"Write the scene now:"
            ),
        ]
        response = await self.model.ainvoke(messages, {"temperature": 0.8, "max_tokens": 2000})
        return response.content

    async def rewrite_style(self, text: str, style: str) -> str:
        style_prompts = {
            "noir": "Write in a dark, gritty noir style. Short sentences, cynical tone, shadowy atmosphere.",
            "romantic": "Write with passionate, poetic language. Emotionally rich, sensory descriptions of love.",
            "horror": "Write with dread and tension. Psychological horror, unsettling atmosphere.",
            "humor": "Write with comedic timing. Witty, playful, humorous.",
            "thriller": "Write with fast pacing. Suspenseful, high stakes, quick cuts.",
        }
        style_prompt = style_prompts.get(style.lower(), f"Rewrite in {style} style.")

        messages = [
            SystemMessage(content="You are a versatile editor and writer. Rewrite the user's text exactly as requested."),
            HumanMessage(content=f"{style_prompt}\n\nRewrite:\n{text}"),
        ]
        response = await self.model.ainvoke(messages, {"temperature": 0.8})
        return response.content

    async def generate_description(self, entity_name: str, db) -> str:
        entity = None
        for e in db.get_entities():
            if e["name"].lower() == entity_name.lower():
                entity = e
                break

        if not entity:
            return f"Entity '{entity_name}' not found in Codex."

        attrs = db.get_attributes(entity["id"])
        attr_str = ", ".join([f"{a['key']}: {a['value']}" for a in attrs])

        messages = [
            SystemMessage(content="You are a descriptive writer focusing on sensory details."),
            HumanMessage(
                content=f"Generate a vivid sensory description for **{entity['name']}** ({entity['type']}).\n\n"
                f"Details: {entity.get('description', 'N/A')}\n"
                f"Attributes: {attr_str}\n\n"
                f"Include smell, touch, sound, and sight. Make it immersive:"
            ),
        ]
        response = await self.model.ainvoke(messages, {"temperature": 0.7})
        return response.content

    async def show_not_tell(self, text: str) -> str:
        messages = [
            SystemMessage(
                content="You are a writing coach specializing in the 'Show, Don't Tell' technique."
            ),
            HumanMessage(
                content=f"Convert this telling prose to showing (physical actions/behaviors instead of emotions):\n\n"
                f"{text}\n\nRewrite with physical actions that convey the same emotions:"
            ),
        ]
        response = await self.model.ainvoke(messages, {"temperature": 0.7})
        return response.content

    # ── Internal helpers ──────────────────────────────────────────

    @staticmethod
    def _build_style_guidance(
        pacing: Optional[str] = None,
        pov: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> str:
        guidance = []

        pacing_map = {
            "slow": "Use a slow, deliberate pace with rich descriptive details and introspective moments.",
            "steady": "Maintain a steady, balanced pace that advances the story consistently.",
            "fast": "Use a fast pace with short sentences, quick action, and minimal exposition.",
            "breakneck": "Use a breakneck pace with rapid-fire action, minimal description, and high tension.",
        }
        if pacing in pacing_map:
            guidance.append(f"- {pacing_map[pacing]}")

        pov_map = {
            "first_person": "Write in first person perspective (I/me/my) for intimate, immediate narration.",
            "third_person_limited": "Write in third person limited perspective, following one character's thoughts and experiences closely.",
            "third_person_omniscient": "Write in third person omniscient perspective, with access to multiple characters' thoughts and a broader narrative view.",
            "second_person": "Write in second person perspective (you/your) for an immersive, choose-your-own-adventure feel.",
        }
        if pov in pov_map:
            guidance.append(f"- {pov_map[pov]}")

        tone_map = {
            "dark": "Use a dark, gloomy tone with ominous foreboding and morbid themes.",
            "hopeful": "Use a hopeful, uplifting tone with optimism and positive outlook.",
            "suspenseful": "Use a suspenseful, tense tone that keeps readers on edge.",
            "melancholic": "Use a melancholic, wistful tone with sadness and reflection.",
            "mysterious": "Use a mysterious, enigmatic tone with secrets and unanswered questions.",
            "violent": "Use a violent, aggressive tone with conflict and physical confrontation.",
            "romantic": "Use a romantic, affectionate tone with focus on relationships and emotions.",
            "humorous": "Use a humorous, light-hearted tone with wit and comedy.",
        }
        if tone in tone_map:
            guidance.append(f"- {tone_map[tone]}")

        return "\n".join(guidance) if guidance else "Write naturally with appropriate pacing and tone for the scene."


if __name__ == "__main__":
    print("Testing AI Writer (LangChain)...")
