"""
Nebula-Writer Evolving Outline Engine v2.1
Story Compass, Rolling Lookahead, Open Tensions, Character Arc States
"""

import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StoryAnchor:
    """Three story anchors - not a fixed outline"""

    emotional_start: str = "to be determined"
    midpoint_disruption: str = "to be determined"
    ending_resolution_type: str = "resolution"  # resolution, ambiguous, tragic


@dataclass
class OpenTension:
    """An unresolved conflict or mystery"""

    id: str
    description: str
    created_chapter: int
    priority: str = "normal"  # low, normal, high, critical
    related_characters: List[str] = field(default_factory=list)
    status: str = "open"  # open, deferred, resolved


@dataclass
class PlantedSeed:
    """Foreshadowing element planted but not yet paid off"""

    id: str
    content: str
    chapter_introduced: int
    payoff_deadline: Optional[int] = None  # chapter deadline
    status: str = "waiting"  # waiting, ready, paid_off, missed


@dataclass
class CharacterArcState:
    """Current state of a character's arc"""

    character_id: str
    character_name: str
    current_belief: str = ""
    current_want: str = ""
    currently_knows: List[str] = field(default_factory=list)
    emotionally_at: str = ""  # emotional state
    chapter_last_updated: int = 0


@dataclass
class LookaheadCard:
    """A single chapter lookahead card"""

    chapter_num: int
    title: str
    scene_intention: str
    character_focus: str
    story_question: str
    certainty: str = "high"  # high, medium, low
    notes: str = ""
    status: str = "draft"  # draft, approved, written


class EvolvingOutlineEngine:
    """
    Manages the Story Compass and Rolling 3-Chapter Lookahead
    Based on BRD v2.1 Section 4
    """

    def __init__(self):
        self.story_anchors = StoryAnchor()
        self.open_tensions: List[OpenTension] = []
        self.planted_seeds: List[PlantedSeed] = []
        self.character_arc_states: Dict[str, CharacterArcState] = {}
        self.narrative_momentum: float = 0.5  # 0-1 scale
        self.lookahead_cards: List[LookaheadCard] = []
        self.current_chapter: int = 0

    def initialize(self, anchors: Dict = None) -> Dict:
        """Initialize with story anchors from planning phase"""
        if anchors:
            self.story_anchors = StoryAnchor(
                emotional_start=anchors.get("emotional_start", "to be determined"),
                midpoint_disruption=anchors.get("midpoint_disruption", "to be determined"),
                ending_resolution_type=anchors.get("ending_resolution_type", "resolution"),
            )

        # Generate initial 3-chapter lookahead
        self.generate_rolling_lookahead()

        return self.get_compass()

    def get_compass(self) -> Dict:
        """Get current Story Compass state"""
        return {
            "story_anchors": {
                "emotional_start": self.story_anchors.emotional_start,
                "midpoint_disruption": self.story_anchors.midpoint_disruption,
                "ending_resolution_type": self.story_anchors.ending_resolution_type,
            },
            "open_tensions": [t.__dict__ for t in self.open_tensions],
            "narrative_momentum": self.narrative_momentum,
            "planted_seeds": [s.__dict__ for s in self.planted_seeds],
            "character_arc_states": {k: v.__dict__ for k, v in self.character_arc_states.items()},
            "current_chapter": self.current_chapter,
        }

    def generate_rolling_lookahead(self) -> List[Dict]:
        """
        Generate rolling 3-chapter lookahead cards
        Called after each chapter is approved
        """
        self.current_chapter += 1

        cards = []

        # Chapter N (next - HIGH certainty)
        next_card = LookaheadCard(
            chapter_num=self.current_chapter,
            title=f"Chapter {self.current_chapter}",
            scene_intention=self._generate_scene_intent(),
            character_focus=self._get_arc_pressure_character(),
            story_question=self._generate_story_question(),
            certainty="high",
            status="draft",
        )
        cards.append(next_card)

        # Chapter N+1 (MEDIUM certainty)
        next_plus_1 = LookaheadCard(
            chapter_num=self.current_chapter + 1,
            title=f"Chapter {self.current_chapter + 1}",
            scene_intention="Based on Chapter " + str(self.current_chapter) + " outcome",
            character_focus="To be determined",
            story_question="What tension should carry forward?",
            certainty="medium",
            status="draft",
        )
        cards.append(next_plus_1)

        # Chapter N+2 (LOW certainty - directional only)
        next_plus_2 = LookaheadCard(
            chapter_num=self.current_chapter + 2,
            title=f"Chapter {self.current_chapter + 2}",
            scene_intention="Narrative trajectory shows approaching: " + self.story_anchors.ending_resolution_type,
            character_focus="Arc trajectory",
            story_question="What's the structural beat?",
            certainty="low",
            status="draft",
        )
        cards.append(next_plus_2)

        self.lookahead_cards = cards

        return [c.__dict__ for c in cards]

    def _generate_scene_intent(self) -> str:
        """Generate scene intention for next chapter"""
        # Use highest priority open tension
        if self.open_tensions:
            highest = max(
                self.open_tensions, key=lambda t: {"critical": 4, "high": 3, "normal": 2, "low": 1}.get(t.priority, 2)
            )
            return f"Resolve or advance: {highest.description}"

        # Default scene intention
        intents = [
            "Introduce the main conflict",
            "Deepen character relationships",
            "Reveal world details through action",
            "Build tension toward midpoint",
            "Confront the antagonist",
        ]
        return intents[self.current_chapter % len(intents)]

    def _get_arc_pressure_character(self) -> str:
        """Get character with most arc pressure"""
        if not self.character_arc_states:
            return "Protagonist"

        # Character with oldest update has most pressure
        oldest = min(
            self.character_arc_states.values(), key=lambda a: a.chapter_last_updated if a.chapter_last_updated else 0
        )
        return oldest.character_name

    def _generate_story_question(self) -> str:
        """Generate the story question for this chapter"""
        if self.open_tensions:
            return f"Will the {self.open_tensions[0].description} be resolved?"

        return "What new question does this chapter introduce?"

    def add_open_tension(
        self, description: str, chapter: int = None, priority: str = "normal", characters: List[str] = None
    ) -> str:
        """Add a new open tension"""
        tension = OpenTension(
            id=str(uuid.uuid4())[:8],
            description=description,
            created_chapter=chapter or self.current_chapter,
            priority=priority,
            related_characters=characters or [],
        )
        self.open_tensions.append(tension)

        # Update narrative momentum
        self._calculate_momentum()

        return tension.id

    def close_tension(self, tension_id: str) -> bool:
        """Mark a tension as resolved"""
        for t in self.open_tensions:
            if t.id == tension_id:
                t.status = "resolved"
                self._calculate_momentum()
                return True
        return False

    def add_planted_seed(self, content: str, chapter: int = None) -> str:
        """Add foreshadowing/planted seed"""
        seed = PlantedSeed(
            id=str(uuid.uuid4())[:8],
            content=content,
            chapter_introduced=chapter or self.current_chapter,
            status="waiting",
        )
        self.planted_seeds.append(seed)
        return seed.id

    def update_character_arc(
        self,
        character_id: str,
        character_name: str,
        belief: str = None,
        want: str = None,
        knows: List[str] = None,
        emotional: str = None,
    ) -> None:
        """Update character arc state"""
        if character_id not in self.character_arc_states:
            self.character_arc_states[character_id] = CharacterArcState(
                character_id=character_id, character_name=character_name
            )

        arc = self.character_arc_states[character_id]
        if belief:
            arc.current_belief = belief
        if want:
            arc.current_want = want
        if knows:
            arc.currently_knows.extend(knows)
        if emotional:
            arc.emotionally_at = emotional

        arc.chapter_last_updated = self.current_chapter

    def _calculate_momentum(self):
        """Calculate narrative momentum score"""
        # More open tensions = higher momentum
        open_count = sum(1 for t in self.open_tensions if t.status == "open")

        self.narrative_momentum = min(1.0, open_count / 5.0)  # max at 5 tensions

    def approve_lookahead_card(self, chapter: int) -> bool:
        """User approves a lookahead card before writing"""
        for card in self.lookahead_cards:
            if card.chapter_num == chapter:
                card.status = "approved"
                return True
        return False

    def redirect_story(self, redirection_type: str, details: str) -> Dict:
        """
        User redirects story direction
        Returns what was updated and any narrative debt
        """
        debt = []

        if redirection_type == "anchor":
            # User changed a story anchor
            if "ending" in details.lower():
                self.story_anchors.ending_resolution_type = details
                debt.append("Ending type changed - lookahead recalculation needed")

            # Recalculate lookahead
            self.generate_rolling_lookahead()

        elif redirection_type == "skip_tension":
            # User wants to skip current tension
            if self.open_tensions:
                t = self.open_tensions[0]
                t.status = "deferred"
                debt.append(f"Tension '{t.description}' deferred - may need payoff later")
                self._calculate_momentum()

        elif redirection_type == "new_direction":
            # User specifies completely new direction
            self.narrative_momentum = 0.7  # Increase momentum
            self.generate_rolling_lookahead()

        return {
            "redirect_type": redirection_type,
            "updated": True,
            "narrative_debt": debt,
            "lookahead_updated": len(self.lookahead_cards) > 0,
        }

    def get_lookahead_cards(self) -> List[Dict]:
        """Get current lookahead cards"""
        return [c.__dict__ for c in self.lookahead_cards]

    def after_chapter_approved(self, chapter_content: str) -> List[Dict]:
        """
        Called after a chapter is approved
        Updates lookahead and returns new cards
        """
        # Generate new lookahead (advances chapter counter)
        new_cards = self.generate_rolling_lookahead()

        # Auto-detect new tensions from prose
        self._detect_tensions_from_prose(chapter_content)

        # Auto-detect new planted seeds
        self._detect_seeds_from_prose(chapter_content)

        return new_cards

    def _detect_tensions_from_prose(self, content: str):
        """Auto-detect open tensions from chapter prose"""
        content_lower = content.lower()

        tension_patterns = [
            ("mystery introduced", ["unknown", "discover", "secret", "hidden"], "normal"),
            ("conflict created", ["fight", "chase", "threat", "danger"], "high"),
            ("relationship tension", ["betray", "lie", "miss trust", "argument"], "normal"),
        ]

        for pattern_name, keywords, priority in tension_patterns:
            for keyword in keywords:
                if keyword in content_lower and not any(
                    pattern_name in t.description.lower() for t in self.open_tensions
                ):
                    self.add_open_tension(
                        description=f"{pattern_name}: {keyword}", chapter=self.current_chapter, priority=priority
                    )
                    break

    def _detect_seeds_from_prose(self, content: str):
        """Auto-detect foreshadowing from chapter prose"""
        seed_patterns = ["promise", "will", "later", "eventually", "when", "before"]

        content.lower()
        sentences = content.split(".")

        for sentence in sentences:
            sentence_lower = sentence.lower()
            for pattern in seed_patterns:
                if pattern in sentence_lower and len(sentence) < 100:
                    # Check if already planted
                    if not any(pattern in s.content.lower() for s in self.planted_seeds):
                        self.add_planted_seed(sentence.strip()[:100], self.current_chapter)


def create_evolution_engine() -> EvolvingOutlineEngine:
    """Create a new Evolving Outline Engine"""
    return EvolvingOutlineEngine()


if __name__ == "__main__":
    print("Testing Evolving Outline Engine...")

    engine = create_evolution_engine()

    # Initialize with story anchors
    compass = engine.initialize(
        {"emotional_start": "burdened", "midpoint_disruption": "discovers truth", "ending_resolution_type": "ambiguous"}
    )

    print(f"\nStory Compass: {json.dumps(compass, indent=2)}")

    # Add open tension
    tid = engine.add_open_tension("Who killed the crime lord?", priority="high")
    print(f"\nAdded tension: {tid}")

    # Get lookahead
    cards = engine.get_lookahead_cards()
    print("\nLookahead Cards:")
    for card in cards:
        print(f"  Ch.{card['chapter_num']} [{card['certainty']}]: {card['scene_intention']}")

    # Simulate chapter approval and lookahead update
    new_cards = engine.after_chapter_approved("A new chapter was written with tension.")
    print("\nAfter chapter approval, new cards:")
    for card in new_cards:
        print(f"  Ch.{card['chapter_num']}: {card['scene_intention']}")

    print("\nEvolving Outline Engine working!")
