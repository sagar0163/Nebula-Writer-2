"""
Nebula-Writer Idea Processor v2.1
Handles conversational onboarding and anchor generation
"""

import json
from typing import Dict, List


class StoryArchitect:
    """
    Conversational Story Architect - BRD Section 5.

    This class serves as the primary intelligence layer for the "Story Architect" view.
    It handles free-form brainstorming sessions with the user and uses an LLM to:
    1. Provide narrative feedback and encouragement.
    2. Extract structured story metadata (Entities, Anchors, Tensions, Plot Threads).
    """

    def __init__(self, ai_writer):
        """
        Initializes the StoryArchitect with an AIWriter instance.
        :param ai_writer: The AI client used for generation and extraction.
        """
        self.ai = ai_writer

    def process_chat(self, history: List[Dict], current_state: Dict) -> Dict:
        """
        Process the ongoing conversation history and identify new story elements.

        This method sends the chat history and the current known state of the story
        to the LLM. The LLM is instructed to respond as a 'Story Architect' and
        output a JSON object containing both its verbal response and any
        extracted story elements.

        :param history: List of chat messages (role and content).
        :param current_state: The current database state (entities, plot threads, etc.)
                              to provide context for the LLM.
        :return: A dictionary containing 'response' (str) and 'extractions' (dict).
        """

        # Define the personality and rules for the AI Architect
        system_prompt = f"""You are the Nebula Story Architect. Your goal is to help the writer brainstorm their novel.
        Be encouraging, inquisitive, and insightful. Focus on deep character motivations and narrative stakes.

        CURRENT STORY STATE (Context for your understanding):
        {json.dumps(current_state)}

        TASK:
        1. Respond to the user's latest message naturally.
        2. Extract any NEW or UPDATED story elements mentioned in the conversation.

        OUTPUT FORMAT (Strict JSON):
        Return ONLY JSON with:
        - "response": Your verbal response to the writer.
        - "extractions": {{
            "entities": [{{ "name": "...", "type": "character|location|item", "description": "..." }}],
            "anchors": [{{ "type": "beginning|midpoint|end", "description": "..." }}],
            "tensions": ["..."],
            "plot_threads": [{{ "title": "...", "description": "...", "importance": "minor|normal|major|central" }}]
          }}

        GUIDELINES:
        - Only include extractions if they were explicitly mentioned or strongly implied in the latest part of the chat.
        - Do not repeat elements already present in the CURRENT STORY STATE unless they are being updated.
        """

        # Get the latest user message or default to a greeting
        user_message = history[-1]["content"] if history else "Hello"

        try:
            # Generate the response and extractions
            # Temperature is set to 0.5 for a balance between creativity and structural consistency.
            response_text = self.ai._generate(system_prompt, user_message, temperature=0.5)

            # Clean and parse the JSON from the AI output
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            data = json.loads(response_text[start:end])
            return data
        except Exception as e:
            # Graceful error handling for LLM timeouts or parsing errors
            print(f"Architect Processing Error: {e}")
            return {
                "response": "I'm having a bit of trouble processing that. Can we try again?",
                "extractions": {"entities": [], "anchors": [], "tensions": [], "plot_threads": []},
            }


class IdeaProcessor:
    """
    Q&A Engine for Idea Clarification.
    Based on v2.1 specifications for onboarding.
    """

    def __init__(self):
        self.questions = []
        self.answers = {}
        self.idea = ""

    def process_idea(self, idea: str) -> Dict:
        self.idea = idea
        # Mock logic for onboarding flow
        self.questions = [
            {"id": "q1", "question": "What is the primary emotional tone of this story?", "user_answer": None},
            {
                "id": "q2",
                "question": "Who is the main antagonist or what is the primary opposing force?",
                "user_answer": None,
            },
            {
                "id": "q3",
                "question": "What is the unique 'twist' or hook that sets this world apart?",
                "user_answer": None,
            },
        ]
        return {
            "detected": {"genre": "unknown", "tone": "developing"},
            "questions": self.questions,
            "questions_remaining": len(self.questions),
        }

    def answer_question(self, q_id: str, answer: str) -> str:
        self.answers[q_id] = answer
        for q in self.questions:
            if q["id"] == q_id:
                q["user_answer"] = answer
                return f"Got it: {answer}"
        return "Question not found"

    def is_ready(self) -> bool:
        return all(q["user_answer"] is not None for q in self.questions)

    def generate_world_proposal(self) -> Dict:
        return {
            "name": "Developing World",
            "description": f"A world born from the idea: {self.idea}",
            "rules": ["Magic exists but is rare", "High political tension"],
        }

    def generate_character_proposals(self) -> List[Dict]:
        return [
            {"name": "Protagonist", "type": "character", "description": "The center of the journey."},
            {"name": "Antagonist", "type": "character", "description": "The opposing force."},
        ]


def create_story_architect(ai_writer):
    """Factory function to instantiate the StoryArchitect."""
    return StoryArchitect(ai_writer)
