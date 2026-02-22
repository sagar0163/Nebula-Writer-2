"""
Nebula-Writer AI Module
AI-powered writing using Gemini API with context from Codex
"""
import os
import json
from typing import List, Dict, Optional
from pathlib import Path

# Try to import google.genai, install if not available
try:
    from google import genai
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "google-genai"], check=True)
    from google import genai


class AIWriter:
    """AI Writer that uses Codex context for accurate fiction writing"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"
    
    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with Codex context"""
        prompt = """You are Nebula-Writer, an AI fiction writing assistant. You write immersive, engaging prose.

IMPORTANT: You have access to the story's Codex (database). Use these facts accurately:

"""
        # Add entities
        if context.get("entities"):
            prompt += "## ENTITIES\n"
            for e in context["entities"]:
                attrs = ", ".join([f"{a['key']}: {a['value']}" for a in e.get("attributes", [])])
                prompt += f"- **{e['name']}** ({e['type']}): {e.get('description', 'N/A')}"
                if attrs:
                    prompt += f" | {attrs}"
                prompt += "\n"
        
        # Add relationships
        if context.get("relationships"):
            prompt += "\n## RELATIONSHIPS\n"
            for r in context["relationships"]:
                prompt += f"- {r['from_name']} → {r['relationship_type']} → {r['to_name']}\n"
        
        # Add recent events
        if context.get("recent_events"):
            prompt += "\n## RECENT EVENTS\n"
            for ev in context["recent_events"][-5:]:
                ch = f" (Ch. {ev['chapter']})" if ev.get('chapter') else ""
                prompt += f"- {ev['title']}{ch}: {ev.get('description', '')}\n"
        
        prompt += """
Write in third person, past tense. Immerse readers with sensory details.
Never contradict established facts from the Codex.
"""
        return prompt
    
    def get_context(self, db, entity_ids: List[int] = None, chapter: int = None) -> Dict:
        """Retrieve context from Codex"""
        context = {"entities": [], "relationships": [], "recent_events": []}
        
        # Get entities with attributes
        entities = db.get_entities()
        for e in entities:
            if entity_ids and e['id'] not in entity_ids:
                continue
            e['attributes'] = db.get_attributes(e['id'])
            context["entities"].append(e)
        
        # Get relationships
        context["relationships"] = db.get_relationships()
        
        # Get recent events
        context["recent_events"] = db.get_events(chapter)
        
        return context
    
    def write_scene(self, db, beat: str, word_count: int = 500, 
                    entity_ids: List[int] = None, chapter: int = None) -> str:
        """Write a scene based on a beat"""
        context = self.get_context(db, entity_ids, chapter)
        system_prompt = self._build_system_prompt(context)
        
        user_prompt = f"""Write a scene based on this beat:
"{beat}"

Target length: ~{word_count} words.

Write the scene now:"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
                "temperature": 0.8,
                "max_output_tokens": 2000,
            }
        )
        
        return response.text
    
    def rewrite_style(self, text: str, style: str) -> str:
        """Rewrite text in a different style"""
        style_prompts = {
            "noir": "Write in a dark, gritty noir style. Short sentences, cynical tone, shadowy atmosphere.",
            "romantic": "Write with passionate, poetic language. Emotionally rich, sensory descriptions of love.",
            "horror": "Write with dread and tension. Psychological horror, unsettling atmosphere.",
            "humor": "Write with comedic timing. Witty, playful, humorous.",
            "thriller": "Write with fast pacing. Suspenseful, high stakes, quick cuts.",
        }
        
        style_prompt = style_prompts.get(style.lower(), f"Rewrite in {style} style.")
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{style_prompt}\n\nRewrite:\n{text}",
            config={"temperature": 0.8}
        )
        
        return response.text
    
    def generate_description(self, entity_name: str, db) -> str:
        """Generate sensory description for an entity"""
        entity = None
        for e in db.get_entities():
            if e['name'].lower() == entity_name.lower():
                entity = e
                break
        
        if not entity:
            return f"Entity '{entity_name}' not found in Codex."
        
        attrs = db.get_attributes(entity['id'])
        
        prompt = f"""Generate a vivid sensory description for **{entity['name']}** ({entity['type']}).

Details: {entity.get('description', 'N/A')}
Attributes: {', '.join([f"{a['key']}: {a['value']}" for a in attrs])}

Include smell, touch, sound, and sight. Make it immersive:"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": 0.7}
        )
        
        return response.text
    
    def show_not_tell(self, text: str) -> str:
        """Convert telling to showing"""
        prompt = f"""Convert this telling prose to showing (physical actions/behaviors instead of emotions):

{text}

Rewrite with physical actions that convey the same emotions:"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": 0.7}
        )
        
        return response.text


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "backend"))
    from codex import CodexDatabase
    
    # Quick test
    print("Testing AI Writer...")
    # Will work once GEMINI_API_KEY is set
