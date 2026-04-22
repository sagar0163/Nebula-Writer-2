"""
Nebula-Writer Multi-AI Client
Supports Gemini, OpenAI, and Anthropic Claude
"""
import os
from typing import Dict, Optional, List


class AIClient:
    """Unified AI client supporting multiple providers"""
    
    PROVIDERS = ['gemini', 'openai', 'claude']
    
    def __init__(self, provider: str = 'gemini', api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.environ.get("API_KEY") or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"No API key provided for {provider}")
        
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate client"""
        if self.provider == 'gemini':
            self._init_gemini()
        elif self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'claude':
            self._init_claude()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-2.0-flash"
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
    
    def _init_openai(self):
        """Initialize OpenAI"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o"
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")
    
    def _init_claude(self):
        """Initialize Anthropic Claude"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-sonnet-4-20250514"
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
    
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate content using the configured provider"""
        if self.provider == 'gemini':
            return self._generate_gemini(prompt, system_prompt, **kwargs)
        elif self.provider == 'openai':
            return self._generate_openai(prompt, system_prompt, **kwargs)
        elif self.provider == 'claude':
            return self._generate_claude(prompt, system_prompt, **kwargs)
    
    def _generate_gemini(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate using Gemini"""
        config = {"temperature": kwargs.get("temperature", 0.7)}
        if system_prompt:
            config["system_instruction"] = system_prompt
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        return response.text
    
    def _generate_openai(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7)
        )
        return response.choices[0].message.content
    
    def _generate_claude(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate using Claude"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=messages
        )
        return response.content[0].text
    
    def rewrite(self, text: str, style: str, **kwargs) -> str:
        """Rewrite text in a specific style"""
        style_prompts = {
            "noir": "Write in a dark, gritty noir style. Short sentences, cynical tone, shadowy atmosphere.",
            "romantic": "Write with passionate, poetic language. Emotionally rich, sensory descriptions.",
            "horror": "Write with dread and tension. Psychological horror, unsettling atmosphere.",
            "humor": "Write with comedic timing. Witty, playful, humorous.",
            "thriller": "Write with fast pacing. Suspenseful, high stakes, quick cuts.",
        }
        
        prompt = f"{style_prompts.get(style, f'Rewrite in {style} style.')}\n\nOriginal text:\n{text}"
        return self.generate(prompt, **kwargs)
    
    def expand(self, text: str, target_words: int = 1000, **kwargs) -> str:
        """Expand text to target word count"""
        prompt = f"Expand this text to approximately {target_words} words. Keep the meaning and add sensory details:\n\n{text}"
        return self.generate(prompt, **kwargs)
    
    def summarize(self, text: str, **kwargs) -> str:
        """Summarize text"""
        prompt = f"Summarize this text concisely:\n\n{text}"
        return self.generate(prompt, **kwargs)


def get_available_providers() -> List[Dict]:
    """Check which providers have API keys configured"""
    providers = []
    
    if os.environ.get("GEMINI_API_KEY"):
        providers.append({"id": "gemini", "name": "Google Gemini", "available": True})
    if os.environ.get("OPENAI_API_KEY"):
        providers.append({"id": "openai", "name": "OpenAI GPT-4", "available": True})
    if os.environ.get("ANTHROPIC_API_KEY"):
        providers.append({"id": "claude", "name": "Anthropic Claude", "available": True})
    
    return providers


if __name__ == "__main__":
    print("Available providers:", get_available_providers())