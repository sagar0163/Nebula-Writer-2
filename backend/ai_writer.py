"""
Nebula-Writer AI Module
AI-powered writing using Gemini API with context from Codex
"""
import os
import json
from typing import List, Dict, Optional
from pathlib import Path

# Try to import google.genai and huggingface_hub, install if not available
try:
    from google import genai
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "google-genai"], check=True)
    from google import genai

try:
    from huggingface_hub import InferenceClient
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "huggingface-hub"], check=True)
    from huggingface_hub import InferenceClient


class AIWriter:
    """AI Writer that uses Codex context for accurate fiction writing"""
    
    def __init__(self, gemini_key: str = None, hf_token: str = None):
        """
        Initializes the multi-provider AI client.
        
        Nebula-Writer prioritizes Hugging Face (Llama-3) for logic and creativity,
        with a robust fallback to Google Gemini-2.0-Flash for speed and reliability.
        
        :param gemini_key: API key for Google Gemini (optional if in ENV).
        :param hf_token: API key for Hugging Face Inference API (optional if in ENV).
        """
        self.gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY")
        self.hf_token = hf_token or os.environ.get("HUGGINGFACE_API_KEY")
        
        if not self.gemini_key and not self.hf_token:
            raise ValueError("Neither GEMINI_API_KEY nor HUGGINGFACE_API_KEY set")
        
        # Initialize Gemini client
        self.gemini_client = None
        if self.gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                print(f"FAILED to initialize Gemini: {e}")
        
        # Initialize Hugging Face client
        self.hf_client = None
        # Using Llama-3.2-1B-Instruct as the primary lightweight model
        self.hf_model = "meta-llama/Llama-3.2-1B-Instruct"
        if self.hf_token:
            try:
                self.hf_client = InferenceClient(model=self.hf_model, token=self.hf_token)
            except Exception as e:
                print(f"FAILED to initialize Hugging Face: {e}")
    
    def _generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.8, max_tokens: int = 2000) -> str:
        """
        Internal generation engine with fallback logic.
        
        Attempts to generate content using Hugging Face (Llama-3). 
        If the inference API fails or times out, it seamlessly falls back to Google Gemini.
        
        :param system_prompt: Instructions defining the AI's persona and constraints.
        :param user_prompt: The specific request or context from the user.
        :param temperature: Sampling temperature (0.0 for deterministic, 1.0 for creative).
        :param max_tokens: Maximum length of the generated response.
        :return: The generated text response.
        """
        
        # Attempt generation with Hugging Face first
        if self.hf_client:
            try:
                print(f"Generating with Hugging Face ({self.hf_model})...")
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                response = self.hf_client.chat_completion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Hugging Face failed: {e}")
                if not self.gemini_client:
                    raise e
                print("Falling back to Gemini...")
        
        # Fallback to Gemini
        if self.gemini_client:
            try:
                print("Generating with Gemini (gemini-2.0-flash)...")
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_prompt,
                    config={
                        "system_instruction": system_prompt,
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )
                return response.text
            except Exception as e:
                print(f"Gemini failed: {e}")
                raise e
        
        raise ValueError("No LLM providers available or both failed.")

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
    
    def get_context(self, db, entity_ids: List[int] = None, chapter: int = None, max_entities: int = 5, max_events: int = 3) -> Dict:
        """
        Retrieve context from Codex with AGGRESSIVE limits to prevent token overflow.
        Target: < 15,000 tokens total
        """
        context = {"entities": [], "relationships": [], "recent_events": [], "chapters": []}
        
        # Entities: max 5, max 3 attributes each
        all_entities = db.get_entities()
        if entity_ids:
            entities = [e for e in all_entities if e['id'] in entity_ids][:max_entities]
        else:
            entities = all_entities[:max_entities]
        
        for e in entities:
            e['attributes'] = db.get_attributes(e['id'])[:3]  # Max 3 attrs
            # Remove large fields
            if 'description' in e and len(e['description']) > 200:
                e['description'] = e['description'][:200] + "..."
            context["entities"].append(e)
        
        # Relationships: only those involving selected entities, max 10
        all_rels = db.get_relationships()
        if entity_ids:
            rels = [r for r in all_rels if r['from_entity_id'] in entity_ids or r['to_entity_id'] in entity_ids][:10]
        else:
            rels = all_rels[:10]
        context["relationships"] = rels
        
        # Events: only for specific chapter, max 3
        if chapter:
            events = db.get_events(chapter)[:max_events]
        else:
            events = []
        context["recent_events"] = events
        
        # Chapters: only current chapter summary, MAX word count 500
        if chapter:
            chap = db.get_chapter(chapter)
            if chap:
                chap_summ = {
                    "number": chap.get("number"),
                    "title": chap.get("title", ""),
                    "summary": chap.get("summary", "")[:300] if chap.get("summary") else ""
                }
                context["chapters"].append(chap_summ)
        
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
        
        return self._generate(system_prompt, user_prompt, temperature=0.8, max_tokens=2000)
    
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
        system_prompt = "You are a versatile editor and writer. Rewrite the user's text exactly as requested."
        
        return self._generate(system_prompt, f"{style_prompt}\n\nRewrite:\n{text}", temperature=0.8)
    
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
        
        system_prompt = "You are a descriptive writer focusing on sensory details."
        user_prompt = f"""Generate a vivid sensory description for **{entity['name']}** ({entity['type']}).

Details: {entity.get('description', 'N/A')}
Attributes: {', '.join([f"{a['key']}: {a['value']}" for a in attrs])}

Include smell, touch, sound, and sight. Make it immersive:"""
        
        return self._generate(system_prompt, user_prompt, temperature=0.7)
    
    def show_not_tell(self, text: str) -> str:
        """Convert telling to showing"""
        system_prompt = "You are a writing coach specializing in the 'Show, Don't Tell' technique."
        user_prompt = f"""Convert this telling prose to showing (physical actions/behaviors instead of emotions):

{text}

Rewrite with physical actions that convey the same emotions:"""
        
        return self._generate(system_prompt, user_prompt, temperature=0.7)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "backend"))
    from codex import CodexDatabase
    
    # Quick test
    print("Testing AI Writer...")
    # Will work once GEMINI_API_KEY or HUGGINGFACE_API_KEY is set
