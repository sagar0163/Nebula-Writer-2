"""
Nebula-Writer Style Learning System
Captures and learns from user's writing style to improve AI-generated content
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from nebula_writer.codex import CodexDatabase


class StyleProfile:
    """Represents a learned writing style profile"""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.vocabulary_preferences = {}  # word frequency preferences
        self.sentence_structure = {}  # average length, complexity
        self.tone_indicators = {}  # emotional word usage
        self.punctuation_style = {}  # comma, semicolon, dash usage
        self.dialogue_patterns = {}  # how dialogue is written
        self.descriptive_phrases = []  # common descriptive patterns
        self.last_updated = datetime.now().isoformat()
        self.confidence_score = 0.0  # how confident we are in this profile

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "vocabulary_preferences": self.vocabulary_preferences,
            "sentence_structure": self.sentence_structure,
            "tone_indicators": self.tone_indicators,
            "punctuation_style": self.punctuation_style,
            "dialogue_patterns": self.dialogue_patterns,
            "descriptive_phrases": self.descriptive_phrases,
            "last_updated": self.last_updated,
            "confidence_score": self.confidence_score,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StyleProfile":
        profile = cls(data.get("user_id", "default"))
        profile.vocabulary_preferences = data.get("vocabulary_preferences", {})
        profile.sentence_structure = data.get("sentence_structure", {})
        profile.tone_indicators = data.get("tone_indicators", {})
        profile.punctuation_style = data.get("punctuation_style", {})
        profile.dialogue_patterns = data.get("dialogue_patterns", {})
        profile.descriptive_phrases = data.get("descriptive_phrases", [])
        profile.last_updated = data.get("last_updated", datetime.now().isoformat())
        profile.confidence_score = data.get("confidence_score", 0.0)
        return profile


class StyleLearner:
    """Learns and applies user writing style"""

    def __init__(self, db: CodexDatabase, profile_path: str = "data/style_profiles.json"):
        self.db = db
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(exist_ok=True)
        self.current_profile = self._load_profile()

    def _load_profile(self) -> StyleProfile:
        """Load existing style profile or create new one"""
        if self.profile_path.exists():
            try:
                with open(self.profile_path, "r") as f:
                    data = json.load(f)
                    return StyleProfile.from_dict(data)
            except Exception as e:
                print(f"Error loading style profile: {e}")

        # Return default profile
        return StyleProfile()

    def _save_profile(self):
        """Save current style profile to disk"""
        try:
            with open(self.profile_path, "w") as f:
                json.dump(self.current_profile.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving style profile: {e}")

    def analyze_text(self, text: str) -> Dict:
        """Analyze text to extract style characteristics"""
        if not text or len(text.strip()) < 50:
            return {}

        # Basic text statistics
        words = text.split()
        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]

        analysis = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "vocabulary_diversity": len(set(w.lower() for w in words)) / len(words) if words else 0,
        }

        # Sentence structure analysis
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            analysis["sentence_length_variance"] = sum(
                (length - analysis["avg_sentence_length"]) ** 2 for length in sentence_lengths
            ) / len(sentence_lengths)

        # Punctuation analysis
        analysis["comma_count"] = text.count(",")
        analysis["semicolon_count"] = text.count(";")
        analysis["colon_count"] = text.count(":")
        analysis["dash_count"] = text.count("—") + text.count("--")
        analysis["quotation_count"] = text.count('"') + text.count("'")
        analysis["exclamation_count"] = text.count("!")
        analysis["question_count"] = text.count("?")

        # Dialogue detection (simple)
        dialogue_markers = ['"', "'"]
        dialogue_count = sum(text.count(marker) for marker in dialogue_markers) // 2  # Approximate pairs
        analysis["dialogue_ratio"] = dialogue_count / len(sentences) if sentences else 0

        # Common words (excluding stop words)
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
        }
        content_words = [
            w.lower().strip('.,!?;:"') for w in words if w.lower().strip('.,!?;:"') not in stop_words and len(w) > 2
        ]
        if content_words:
            from collections import Counter

            word_freq = Counter(content_words)
            analysis["top_words"] = dict(word_freq.most_common(20))

        return analysis

    def learn_from_text(self, text: str, weight: float = 0.1):
        """Learn style characteristics from a text sample"""
        if not text or len(text.strip()) < 30:
            return

        analysis = self.analyze_text(text)
        if not analysis:
            return

        # Update vocabulary preferences
        if "top_words" in analysis:
            for word, freq in analysis["top_words"].items():
                current = self.current_profile.vocabulary_preferences.get(word, 0)
                # Exponential moving average
                self.current_profile.vocabulary_preferences[word] = current * (1 - weight) + freq * weight

        # Update sentence structure
        if "avg_sentence_length" in analysis:
            current = self.current_profile.sentence_structure.get("avg_length", 0)
            self.current_profile.sentence_structure["avg_length"] = (
                current * (1 - weight) + analysis["avg_sentence_length"] * weight
            )

        if "sentence_length_variance" in analysis:
            current = self.current_profile.sentence_structure.get("variance", 0)
            self.current_profile.sentence_structure["variance"] = (
                current * (1 - weight) + analysis["sentence_length_variance"] * weight
            )

        # Update punctuation style
        punctuation_fields = [
            "comma_count",
            "semicolon_count",
            "colon_count",
            "dash_count",
            "quotation_count",
            "exclamation_count",
            "question_count",
        ]
        for field in punctuation_fields:
            if field in analysis:
                current = self.current_profile.punctuation_style.get(field, 0)
                # Normalize by text length
                normalized_value = analysis[field] / max(len(text), 1)
                self.current_profile.punctuation_style[field] = current * (1 - weight) + normalized_value * weight

        # Update dialogue patterns
        if "dialogue_ratio" in analysis:
            current = self.current_profile.dialogue_patterns.get("ratio", 0)
            self.current_profile.dialogue_patterns["ratio"] = (
                current * (1 - weight) + analysis["dialogue_ratio"] * weight
            )

        # Extract descriptive phrases (adjective-noun combinations)
        import re

        # Simple pattern for adjective-noun pairs
        adj_noun_pattern = r"\b([a-zA-Z]+(?:ous|ful|ive|ic|ish|less|ly))\s+([a-zA-Z]+)\b"
        matches = re.findall(adj_noun_pattern, text.lower())
        for adj, noun in matches[:10]:  # Limit to top 10
            phrase = f"{adj} {noun}"
            if phrase not in self.current_profile.descriptive_phrases:
                self.current_profile.descriptive_phrases.append(phrase)
                # Keep only top 50 phrases
                if len(self.current_profile.descriptive_phrases) > 50:
                    self.current_profile.descriptive_phrases = self.current_profile.descriptive_phrases[-50:]

        # Update metadata
        self.current_profile.last_updated = datetime.now().isoformat()
        # Increase confidence based on amount of text learned
        text_weight = min(len(text) / 1000, 0.5)  # Cap at 0.5 for single text
        self.current_profile.confidence_score = min(self.current_profile.confidence_score + text_weight, 1.0)

        # Save profile
        self._save_profile()

    def learn_from_chapter_edits(self, chapter_id: int):
        """Learn from a chapter's content (user's writing)"""
        chapter = self.db.get_chapter(chapter_id)
        if chapter and chapter.get("content"):
            self.learn_from_text(chapter["content"], weight=0.2)

    def learn_from_recent_edits(self, limit: int = 5):
        """Learn from recently edited chapters"""
        chapters = self.db.get_chapters()
        # Sort by update time if available, otherwise just take recent ones
        sorted_chapters = sorted(chapters, key=lambda x: x.get("updated_at", ""), reverse=True)
        for chapter in sorted_chapters[:limit]:
            if chapter.get("content"):
                self.learn_from_text(chapter["content"], weight=0.15)

    def get_style_prompt_addition(self) -> str:
        """Generate a prompt addition that encapsulates the learned style"""
        if self.current_profile.confidence_score < 0.1:
            return ""  # Not enough data yet

        additions = []

        # Vocabulary guidance
        top_words = sorted(self.current_profile.vocabulary_preferences.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_words:
            words = [word for word, _ in top_words]
            additions.append(f"Prefer using words like: {', '.join(words)}")

        # Sentence length guidance
        avg_length = self.current_profile.sentence_structure.get("avg_length", 0)
        if avg_length > 0:
            if avg_length < 10:
                additions.append("Use short, punchy sentences")
            elif avg_length > 25:
                additions.append("Use longer, flowing sentences with complex structures")
            else:
                additions.append("Use medium-length sentences with varied structure")

        # Punctuation guidance
        comma_usage = self.current_profile.punctuation_style.get("comma_count", 0)
        if comma_usage > 0.1:  # More than 1 comma per 10 chars
            additions.append("Use commas frequently for rhythm and pauses")
        elif comma_usage < 0.03:
            additions.append("Use commas sparingly for direct, impactful phrasing")

        semicolon_usage = self.current_profile.punctuation_style.get("semicolon_count", 0)
        if semicolon_usage > 0.01:
            additions.append("Use semicolons to connect related complex ideas")

        # Dialogue guidance
        dialogue_ratio = self.current_profile.dialogue_patterns.get("ratio", 0)
        if dialogue_ratio > 0.3:
            additions.append("Include frequent dialogue with natural speech patterns")
        elif dialogue_ratio > 0.1:
            additions.append("Include some dialogue to break up narration")

        # Descriptive style
        if self.current_profile.descriptive_phrases:
            phrases = self.current_profile.descriptive_phrases[:5]
            additions.append(f"Use descriptive phrases like: {', '.join(phrases)}")

        if additions:
            return "WRITING STYLE GUIDANCE: " + " | ".join(additions)

        return ""

    def apply_style_to_prompt(self, base_prompt: str) -> str:
        """Apply learned style to a base prompt"""
        style_addition = self.get_style_prompt_addition()
        if style_addition:
            return f"{base_prompt}\n\n{style_addition}"
        return base_prompt

    def get_profile_stats(self) -> Dict:
        """Get statistics about the current style profile"""
        return {
            "confidence": self.current_profile.confidence_score,
            "vocabulary_words": len(self.current_profile.vocabulary_preferences),
            "last_updated": self.current_profile.last_updated,
            "has_sufficient_data": self.current_profile.confidence_score > 0.3,
        }


def create_style_learner(db: CodexDatabase) -> StyleLearner:
    """Factory function to create a style learner"""
    return StyleLearner(db)
