"""
Nebula-Writer Prompt Templates
Pre-built prompts for common writing tasks
"""
from typing import Dict, List


PROMPTS = {
    "scene_opener": {
        "name": "Scene Opener",
        "description": "Write an engaging opening for a scene",
        "template": """Write an opening paragraph for a scene with these elements:
- Setting: {setting}
- Mood: {mood}
- Main character present: {character}

Make it immersive and engaging."""
    },
    
    "character_intro": {
        "name": "Character Introduction", 
        "description": "Introduce a character to readers",
        "template": """Write a character introduction for **{name}**.
- Role: {role}
- Key traits: {traits}
- First impression: {impression}

Include physical description and personality."""
    },
    
    "dialogue_scene": {
        "name": "Dialogue Scene",
        "description": "Write a conversation between characters",
        "template": """Write a dialogue scene between **{char1}** and **{char2}**.
- Topic: {topic}
- Subtext: {subtext}
- Tension level: {tension}

Make it natural and revealing of character."""
    },
    
    "action_sequence": {
        "name": "Action Sequence",
        "description": "Write an exciting action scene",
        "template": """Write an action sequence:
- Characters involved: {characters}
- Setting: {setting}
- Goal: {goal}
- Obstacle: {obstacle}

Make it fast-paced and visceral."""
    },
    
    "sensory_description": {
        "name": "Sensory Description",
        "description": "Describe a location or object using all senses",
        "template": """Write a sensory description of **{subject}**.
Include: sight, sound, smell, taste, and touch.
Make it immersive and atmospheric."""
    },
    
    "emotion_transition": {
        "name": "Emotion Transition",
        "description": "Show character emotional changes",
        "template": """Show **{character}** transitioning from **{from_emotion}** to **{to_emotion}**.
- Trigger: {trigger}
- Setting: {setting}

Use physical actions and internal thoughts, not direct emotion labels."""
    },
    
    "backstory_injection": {
        "name": "Backstory Injection",
        "description": "Reveal character backstory naturally",
        "template": """Reveal **{character}**'s backstory about **{topic}**.
- Current situation: {situation}
- How it surfaces: {method}

Make it feel organic, not like an info dump."""
    },
    
    "cliffhanger": {
        "name": "Chapter Cliffhanger",
        "description": "End a chapter on a cliffhanger",
        "template": """Write a cliffhanger ending for Chapter {chapter}.
- Main conflict: {conflict}
- Stakes: {stakes}
- Reveal or decision: {reveal}

Leave the reader wanting more."""
    },
    
    "romantic_scene": {
        "name": "Romantic Scene",
        "description": "Write a romantic moment",
        "template": """Write a romantic scene between **{char1}** and **{char2}**.
- Setting: {setting}
- Mood: {mood}
- Emotional stakes: {stakes}

Include sensory details and emotional vulnerability."""
    },
    
    "noir_description": {
        "name": "Noir Description",
        "description": "Write in noir style",
        "template": """Rewrite in noir style:
- Tone: cynical, gritty
- Voice: first-person detective
- Style: short sentences, metaphors

Original text:
{text}"""
    }
}


def get_prompt(template_key: str, **kwargs) -> str:
    """Get a prompt template with variables filled"""
    if template_key not in PROMPTS:
        raise ValueError(f"Unknown prompt: {template_key}")
    
    template = PROMPTS[template_key]["template"]
    
    # Replace placeholders
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    
    return template


def list_prompts() -> List[Dict]:
    """List all available prompts"""
    return [{"key": k, "name": v["name"], "description": v["description"]} 
            for k, v in PROMPTS.items()]


if __name__ == "__main__":
    # Example usage
    print("Available prompts:")
    for p in list_prompts():
        print(f"  - {p['key']}: {p['name']}")
    
    print("\nExample prompt:")
    print(get_prompt("scene_opener", setting="a rainy Mumbai street", mood="tense", character="Ravi"))
