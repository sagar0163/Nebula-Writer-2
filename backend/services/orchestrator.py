import os
from typing import List, Dict, Optional
from core.narrative_state_engine import NarrativeStateEngine
from core.memory_manager import MemoryManager
from core.versioning import VersioningService
from core.character_agent import CharacterAgent
from core.performance import NarrativeCache, run_parallel_checks
from codex import CodexDatabase
from plot_manager import create_plot_manager
from ai_writer import AIWriter
from conversation import ConversationEngine
from ripple_checker import create_ripple_checker

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
        self.memory = MemoryManager(token_limit=100000)
        self.versioning = VersioningService()
        self.ripple = create_ripple_checker(self.db, self.ai)
        
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
            "momentum": snapshot.momentum_score
        }

    async def _execute_write_chapter(self, beat: str, context: str) -> Dict:
        """Surgical chapter writing with versioning and ripple checks."""
        # Check cache
        cache_key = f"context_{hash(context)}"
        cached_context = NarrativeCache.get(cache_key)
        if not cached_context:
            NarrativeCache.set(cache_key, context)
            
        # Save pre-change snapshot
        self.versioning.create_snapshot(self.db, snapshot_type="pre_chapter_write")
        
        # Generate prose
        system_prompt = f"Write the next scene. Context: {context}"
        prose = self.ai._generate(system_prompt, f"Scene beat: {beat}", max_tokens=3000)
        
        # Run Ripple Check in Parallel (Step 8)
        performance_results = await run_parallel_checks(self.ripple, f"Wrote chapter based on: {beat}")
        
        return {
            "prose": prose,
            "ripples": performance_results["ripples"],
            "version_saved": True
        }

    def get_character_insights(self, entity_id: int) -> Dict:
        """Uses CharacterAgent wrapper to get derived insights."""
        agent = CharacterAgent(entity_id, self.db)
        return {
            "persona": agent.derive_persona(),
            "arc": self.nse.get_character_arc_progression(entity_id)
        }
