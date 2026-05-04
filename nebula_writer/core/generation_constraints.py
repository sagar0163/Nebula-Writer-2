from typing import Any, Dict, List


class GenerationConstraints:
    """
    Structured input layer for the AIWriter.
    Combines directive, character predictions, and context.
    """

    def __init__(self, directive: Any, character_predictions: List[Dict], context_string: str):
        self.directive = directive
        self.character_predictions = character_predictions
        self.context_string = context_string

    def to_system_prompt(self) -> str:
        """Converts constraints into a high-density directive prompt."""
        prompt = "### NARRATIVE DIRECTIVE\n"
        prompt += f"REQUIRED OUTCOME: {self.directive.required_outcome}\n"
        prompt += f"TENSION PROGRESSION: {self.directive.tension_progression}\n"
        prompt += f"PACING TARGET: {self.directive.pacing_target}/10\n"

        prompt += "\n### CHARACTER BEHAVIOR\n"
        for pred in self.character_predictions:
            prompt += f"- {pred['name']}: {pred['conflict_stance']} stance (Resistance: {pred['resistance_level']}). Intent: {pred['intended_actions'][0]}\n"

        prompt += "\n### CONSTRAINTS\n"
        for constraint in self.directive.constraints:
            prompt += f"- {constraint}\n"

        prompt += f"\n### STORY CONTEXT\n{self.context_string}"
        return prompt
