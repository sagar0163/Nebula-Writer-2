import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from nebula_writer.ai_writer import AIWriter
from nebula_writer.codex import CodexDatabase
from nebula_writer.conversation import ConversationEngine
from nebula_writer.core.character_agent import CharacterAgent
from nebula_writer.core.memory_manager import MemoryManager
from nebula_writer.core.narrative_state_engine import NarrativeStateEngine
from nebula_writer.core.narrative_intent_engine import NarrativeIntentEngine
from nebula_writer.core.narrative_director import NarrativeDirector, NarrativeDirective
from nebula_writer.core.narrative_planner import NarrativePlanner
from nebula_writer.core.feedback_engine import FeedbackEngine
from nebula_writer.core.generation_constraints import GenerationConstraints
from nebula_writer.core.performance import NarrativeCache, run_parallel_checks
from nebula_writer.core.versioning import VersioningService
from nebula_writer.plot_manager import create_plot_manager
from nebula_writer.ripple_checker import create_ripple_checker


class NarrativeOrchestrator:
    """
    Directive Narrative Orchestrator (Phase 3).
    Coordinates the proactive planning, simulation, and validation pipeline.
    """

    def __init__(self):
        # 1. Initialize core data layers
        self.db = CodexDatabase()
        self.pm = create_plot_manager()
        self.ai = AIWriter()

        # 2. Initialize Control Layers
        self.nse = NarrativeStateEngine(self.db, self.pm)
        self.nie = NarrativeIntentEngine()
        self.director = NarrativeDirector(self.db)
        self.planner = NarrativePlanner(self.db)
        
        # 3. Initialize Support Modules
        self.memory = MemoryManager(token_limit=120000)
        self.versioning = VersioningService()
        self.ripple = create_ripple_checker(self.db, self.ai)
        self.feedback = FeedbackEngine(self.db)
        self.conv = ConversationEngine(self.db, self.ai)

    async def handle_chat(self, message: str) -> Dict:
        """Standard chat flow routed through ConversationEngine."""
        snapshot = self.nse.get_snapshot()
        project_state = {
            "phase": snapshot.phase.value,
            "momentum": snapshot.momentum_score,
            "chapters_count": len(self.db.get_chapters())
        }
        
        # Use the conversation engine to process the message
        result = await self.conv.process_message(message, project_state=project_state)
        
        # Add phase/context info for the UI
        result["phase"] = snapshot.phase.value
        
        # Note: If intent was write_chapter, result will contain message about starting generation
        # The frontend handles triggering the actual generation if needed, or we could handle it here.
        
        return result

    async def handle_write_scene(self, beat: str) -> Dict:
        """
        The 10-Step Directive Writing Pipeline.
        Enforces narrative logic and performs active integrity checks.
        """
        # 1. Snapshot & Planning
        cache_key = f"snapshot_{datetime.now().strftime('%Y%m%d_%H')}"
        snapshot = NarrativeCache.get(cache_key)
        if not snapshot:
            snapshot = self.nse.get_snapshot()
            NarrativeCache.set(cache_key, snapshot)
            
        lt_plan = self.planner.get_plan()

        # 2. Director -> Generate Narrative Directive
        directive = self.director.derive_directive(snapshot, long_term_plan=lt_plan)
        
        # 3. Planner -> Verify Arc Alignment
        alignment = self.planner.check_alignment(beat, lt_plan)

        # 4. Memory Manager -> Guaranteed Context
        context = self.memory.build_context(snapshot, user_input=beat)

        # 5. Character Agent -> Action Prediction
        character_predictions = []
        # Focus on characters mentioned in the beat or intent
        for entity in snapshot.entities:
            if entity['type'] == 'character' and entity['name'].lower() in beat.lower():
                agent = CharacterAgent(entity['id'], self.db)
                character_predictions.append(agent.predict_actions(beat))

        # 6. Assemble Generation Constraints
        constraints = GenerationConstraints(
            directive=directive,
            character_predictions=character_predictions,
            context_string=context
        )

        # 7. Pre-Generation Snapshot (Versioning)
        self.versioning.create_snapshot(self.db, snapshot_type="pre_scene_write")

        # 8. AI Generation
        system_prompt = constraints.to_system_prompt()
        prose = await self.ai._generate(system_prompt, f"Write the scene for this beat: {beat}", role='writer', max_tokens=4000)

        # 9. Active Integrity Check (Ripple Checker)
        validation = self.ripple.validate_scene_integrity(prose, directive)
        
        # 10. Auto-Correction Loop (One Retry)
        if not validation["is_valid"]:
            prose = await self.ai._generate(
                f"{system_prompt}\n\nCRITICAL CORRECTION: {validation['correction_prompt']}", 
                f"Rewrite the scene: {beat}", 
                role='writer',
                max_tokens=4000
            )
            # Final validation after retry
            validation = self.ripple.validate_scene_integrity(prose, directive)

        return {
            "prose": prose,
            "directive": {
                "outcome": directive.required_outcome,
                "pacing": directive.pacing_target
            },
            "alignment": alignment,
            "integrity": {
                "is_valid": validation["is_valid"],
                "violations": validation["violations"]
            }
        }

    def get_character_insights(self, entity_id: int) -> Dict:
        """Uses CharacterAgent wrapper to get derived insights."""
        agent = CharacterAgent(entity_id, self.db)
        return {
            "persona": agent.derive_persona(),
            "arc": self.nse.get_character_arc_progression(entity_id)
        }

    def clear_cache(self):
        """Invalidate the narrative cache."""
        NarrativeCache.clear()
        return {"status": "cache_cleared"}
