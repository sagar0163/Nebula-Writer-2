from typing import Dict

from nebula_writer.ai_writer import AIWriter
from nebula_writer.codex import CodexDatabase
from nebula_writer.conversation import ConversationEngine
from nebula_writer.core.character_agent import CharacterAgent
from nebula_writer.core.memory_manager import MemoryManager
from nebula_writer.core.narrative_state_engine import NarrativeStateEngine
from nebula_writer.core.narrative_intent_engine import NarrativeIntentEngine
from nebula_writer.core.feedback_engine import FeedbackEngine
from nebula_writer.core.generation_constraints import GenerationConstraints
from nebula_writer.core.performance import NarrativeCache, run_parallel_checks
from nebula_writer.core.versioning import VersioningService
from nebula_writer.plot_manager import create_plot_manager
from nebula_writer.ripple_checker import create_ripple_checker


class NarrativeOrchestrator:
    """
    Main Orchestrator (Step 7): Decouples main.py from business logic.
    Coordinates all engines and services.
    """

    def __init__(self):
        # 1. Initialize core data layers
        self.db = CodexDatabase()
        self.pm = create_plot_manager()
        self.ai = AIWriter()

        # 2. Initialize Control Layers
        self.nse = NarrativeStateEngine(self.db, self.pm)
        self.nie = NarrativeIntentEngine()
        self.memory = MemoryManager(token_limit=100000)
        self.versioning = VersioningService()
        self.ripple = create_ripple_checker(self.db, self.ai)
        self.feedback = FeedbackEngine(self.db)

        # 3. Initialize Conversation Logic
        self.conv = ConversationEngine(self.db, self.ai)

    async def handle_chat(self, message: str) -> Dict:
        """
        Refactored Generation Flow (Step 3):
        user input -> intent -> snapshot -> context -> generate
        """
        # 1. Intent Classification
        classification = self.conv.classify_intent(message)

        # 2. Get Narrative Snapshot
        snapshot = self.nse.get_snapshot()

        # 3. Build Context using MemoryManager
        context = self.memory.build_context(snapshot, user_input=message)

        # 4. Handle Specific Intent
        if classification.intent.value == "write_chapter":
            return await self._execute_write_chapter(message, context)

        # Default: General Chat
        system_prompt = f"You are AutoNovelist in {snapshot.phase.value} phase. Context: {context}"
        response = self.ai._generate(system_prompt, message)

        return {
            "response": response,
            "intent": classification.intent.value,
            "phase": snapshot.phase.value,
            "momentum": snapshot.momentum_score,
        }

    async def _execute_write_chapter(self, beat: str, context: str) -> Dict:
        """
        Decision-Driven Generation (Phase 2 Upgrade):
        intent -> simulation -> constraints -> generate
        """
        # 1. Decision Layer: Get Narrative Intent
        snapshot = self.nse.get_snapshot()
        intent = self.nie.derive_intent(snapshot)

        # 2. Character Simulation
        simulations = []
        for char_id in intent.character_focus:
            agent = CharacterAgent(char_id, self.db)
            simulations.append(agent.simulate_behavior(beat))

        # 3. Aggregate Constraints
        constraints = GenerationConstraints(
            intent=intent,
            character_simulations=simulations,
            narrative_bias=self.feedback.get_narrative_bias(),
            context_string=context,
            active_anchors=[a['description'] for a in getattr(snapshot, 'anchors', [])]
        )

        # Check cache
        cache_key = f"constraints_{hash(str(constraints))}"
        cached_context = NarrativeCache.get(cache_key)
        if not cached_context:
            NarrativeCache.set(cache_key, constraints.to_system_prompt())

        # Save pre-change snapshot
        self.versioning.create_snapshot(self.db, snapshot_type="pre_chapter_write")

        # Generate prose with high-density constraints
        system_prompt = constraints.to_system_prompt()
        prose = self.ai._generate(system_prompt, f"Scene beat: {beat}", max_tokens=3000)

        # Run Ripple Check in Parallel
        performance_results = await run_parallel_checks(self.ripple, f"Wrote chapter based on: {beat}")

        return {"prose": prose, "ripples": performance_results["ripples"], "version_saved": True, "intent": intent.scene_purpose.value}

    def get_character_insights(self, entity_id: int) -> Dict:
        """Uses CharacterAgent wrapper to get derived insights."""
        agent = CharacterAgent(entity_id, self.db)
        return {"persona": agent.derive_persona(), "arc": self.nse.get_character_arc_progression(entity_id)}
