"""
Nebula-Writer AI Module
AI-powered writing using Gemini API with context from Codex
"""

import os
from pathlib import Path
from typing import Dict, List

# Try to import google.genai and huggingface_hub, install if not available
try:
    from google import genai
except ImportError:
    import subprocess

    subprocess.run(["pip", "install", "google-genai"], check=True)
    from google import genai

try:
    from huggingface_hub import AsyncInferenceClient
except ImportError:
    import subprocess

    subprocess.run(["pip", "install", "huggingface-hub"], check=True)
    from huggingface_hub import AsyncInferenceClient


class AIWriter:
    """AI Writer that uses Codex context for accurate fiction writing"""

    def __init__(self, gemini_key: str = None, hf_token: str = None):
        """
        Initializes the AI client with a dynamic Load Balancer for Space clones.
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

        # Initialize Hugging Face worker pool
        self.worker_pool = []
        self.current_worker_index = 0
        
        # Collect all available Space URLs from ENV
        self.worker_metadata = []
        space_configs = [
            ("Writer-Brain", os.environ.get("HF_WRITER_URL")),
            ("Ripple-Check", os.environ.get("HF_RIPPLE_URL")),
            ("Architect-Bot", os.environ.get("HF_ARCHITECT_URL"))
        ]

        for name, url in space_configs:
            if url and self.hf_token:
                try:
                    client = AsyncInferenceClient(model=url, token=self.hf_token)
                    self.worker_pool.append(client)
                    self.worker_metadata.append({
                        "name": name,
                        "url": url,
                        "status": "ready",
                        "usage_count": 0
                    })
                    print(f"[LOAD BALANCER] Added worker: {name} ({url})")
                except Exception as e:
                    print(f"FAILED to add worker {url}: {e}")

        # Fallback to public model if pool is empty
        if not self.worker_pool and self.hf_token:
            public_model = "meta-llama/Llama-3.2-1B-Instruct"
            self.worker_pool.append(AsyncInferenceClient(model=public_model, token=self.hf_token))
            self.worker_metadata.append({
                "name": "Llama-Fallback",
                "url": public_model,
                "status": "ready",
                "usage_count": 0
            })
            print(f"[LOAD BALANCER] Using public model fallback: {public_model}")

    def _get_next_worker(self):
        """Dynamic selection: Find first 'ready' worker, otherwise fallback to round-robin"""
        if not self.worker_pool:
            return None, -1
        
        # 1. Try to find a worker that is currently READY
        for i in range(len(self.worker_pool)):
            idx = (self.current_worker_index + i) % len(self.worker_pool)
            if self.worker_metadata[idx]["status"] == "ready":
                # Advance round-robin pointer to next
                self.current_worker_index = (idx + 1) % len(self.worker_pool)
                
                # Update metadata
                self.worker_metadata[idx]["status"] = "active"
                self.worker_metadata[idx]["usage_count"] += 1
                return self.worker_pool[idx], idx
        
        # 2. If all workers are busy, fallback to standard round-robin
        idx = self.current_worker_index
        self.current_worker_index = (idx + 1) % len(self.worker_pool)
        
        self.worker_metadata[idx]["status"] = "active"
        self.worker_metadata[idx]["usage_count"] += 1
        return self.worker_pool[idx], idx

    def get_worker_status(self):
        """Returns the current status of all workers in the pool"""
        return self.worker_metadata

    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Public async wrapper for the internal generation engine"""
        return await self._generate(system_prompt or "You are a helpful assistant.", prompt, temperature, max_tokens)

    async def _generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.8, max_tokens: int = 2000) -> str:
        """
        Internal generation engine with Dynamic Load Balancing and Fallback.
        """
        # 1. Pick the next worker from the pool
        worker, worker_idx = self._get_next_worker()

        if worker:
            try:
                print(f"Routing request to Worker #{worker_idx} ({self.worker_metadata[worker_idx]['name']})...")
                messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                response = await worker.chat_completion(
                    messages=messages, max_tokens=max_tokens, temperature=temperature
                )
                
                # Reset status back to ready
                self.worker_metadata[worker_idx]["status"] = "ready"
                
                return response.choices[0].message.content
            except Exception as e:
                print(f"Worker failed: {e}. Trying fallback...")
                if worker_idx != -1:
                    self.worker_metadata[worker_idx]["status"] = "error"

                
        # 2. Fallback to Gemini if workers fail
        if self.gemini_client:
            try:
                print("Generating with Gemini (gemini-2.0-flash)...")
                async with self.gemini_client.aio as aclient:
                    response = await aclient.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=user_prompt,
                        config={
                            "system_instruction": system_prompt,
                            "temperature": temperature,
                            "max_output_tokens": max_tokens,
                        },
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
                ch = f" (Ch. {ev['chapter']})" if ev.get("chapter") else ""
                prompt += f"- {ev['title']}{ch}: {ev.get('description', '')}\n"

        prompt += """
Write in third person, past tense. Immerse readers with sensory details.
Never contradict established facts from the Codex.
"""
        return prompt

    def get_context(
        self, db, entity_ids: List[int] = None, chapter: int = None, max_entities: int = 5, max_events: int = 3
    ) -> Dict:
        """
        Retrieve context from Codex with AGGRESSIVE limits to prevent token overflow.
        Target: < 15,000 tokens total
        """
        context = {"entities": [], "relationships": [], "recent_events": [], "chapters": []}

        # Entities: max 5, max 3 attributes each
        all_entities = db.get_entities()
        if entity_ids:
            entities = [e for e in all_entities if e["id"] in entity_ids][:max_entities]
        else:
            entities = all_entities[:max_entities]

        for e in entities:
            e["attributes"] = db.get_attributes(e["id"])[:3]  # Max 3 attrs
            # Remove large fields
            if "description" in e and len(e["description"]) > 200:
                e["description"] = e["description"][:200] + "..."
            context["entities"].append(e)

        # Relationships: only those involving selected entities, max 10
        all_rels = db.get_relationships()
        if entity_ids:
            rels = [r for r in all_rels if r["from_entity_id"] in entity_ids or r["to_entity_id"] in entity_ids][:10]
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
                    "summary": chap.get("summary", "")[:300] if chap.get("summary") else "",
                }
                context["chapters"].append(chap_summ)

        return context

    async def write_scene(
        self, db, beat: str, word_count: int = 500, entity_ids: List[int] = None, chapter: int = None
    ) -> str:
        """Write a scene based on a beat"""
        context = self.get_context(db, entity_ids, chapter)
        system_prompt = self._build_system_prompt(context)

        user_prompt = f"""Write a scene based on this beat:
"{beat}"

Target length: ~{word_count} words.

Write the scene now:"""

        return await self._generate(system_prompt, user_prompt, temperature=0.8, max_tokens=2000)

    async def rewrite_style(self, text: str, style: str) -> str:
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

        return await self._generate(system_prompt, f"{style_prompt}\n\nRewrite:\n{text}", temperature=0.8)

    async def generate_description(self, entity_name: str, db) -> str:
        """Generate sensory description for an entity"""
        entity = None
        for e in db.get_entities():
            if e["name"].lower() == entity_name.lower():
                entity = e
                break

        if not entity:
            return f"Entity '{entity_name}' not found in Codex."

        attrs = db.get_attributes(entity["id"])

        system_prompt = "You are a descriptive writer focusing on sensory details."
        user_prompt = f"""Generate a vivid sensory description for **{entity["name"]}** ({entity["type"]}).

Details: {entity.get("description", "N/A")}
Attributes: {", ".join([f"{a['key']}: {a['value']}" for a in attrs])}

Include smell, touch, sound, and sight. Make it immersive:"""

        return await self._generate(system_prompt, user_prompt, temperature=0.7)

    async def show_not_tell(self, text: str) -> str:
        """Convert telling to showing"""
        system_prompt = "You are a writing coach specializing in the 'Show, Don't Tell' technique."
        user_prompt = f"""Convert this telling prose to showing (physical actions/behaviors instead of emotions):

{text}

Rewrite with physical actions that convey the same emotions:"""

        return await self._generate(system_prompt, user_prompt, temperature=0.7)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "backend"))

    # Quick test
    print("Testing AI Writer...")
    # Will work once GEMINI_API_KEY or HUGGINGFACE_API_KEY is set
