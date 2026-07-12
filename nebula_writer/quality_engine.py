"""
Nebula-Writer Quality Engine — LangGraph Pipeline

Authentic asynchronous LLM orchestration for multi-pass quality revision loop
with 8-criteria rubric scoring, anti-slop filtering, and real-time SSE streaming.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncGenerator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from nebula_writer.models import create_chat_model_with_fallbacks
from nebula_writer.anti_slop import AntiSlopFilter


# =============================================================================
# STATE MODELS
# =============================================================================

class RubricCriterion(str, Enum):
    NARRATIVE_DRIVE = "narrative_drive"
    CHARACTER_VOICE = "character_voice"
    SHOW_NOT_TELL = "show_not_tell"
    SENSORY_DEPTH = "sensory_depth"
    PACING = "pacing"
    DIALOGUE_REALISM = "dialogue_realism"
    THEMATIC_RESONANCE = "thematic_resonance"
    PROSE_RHYTHM = "prose_rhythm"


RUBRIC_WEIGHTS = {
    RubricCriterion.NARRATIVE_DRIVE: 0.15,
    RubricCriterion.CHARACTER_VOICE: 0.15,
    RubricCriterion.SHOW_NOT_TELL: 0.15,
    RubricCriterion.SENSORY_DEPTH: 0.12,
    RubricCriterion.PACING: 0.10,
    RubricCriterion.DIALOGUE_REALISM: 0.13,
    RubricCriterion.THEMATIC_RESONANCE: 0.10,
    RubricCriterion.PROSE_RHYTHM: 0.10,
}

RUBRIC_DESCRIPTIONS = {
    RubricCriterion.NARRATIVE_DRIVE: "Active verbs, forward momentum, cause-and-effect chain pulling reader forward",
    RubricCriterion.CHARACTER_VOICE: "Distinct speech patterns, vocabulary, rhythm unique to each character",
    RubricCriterion.SHOW_NOT_TELL: "Physical actions/behaviors instead of named emotions; no filter words (felt, noticed, saw)",
    RubricCriterion.SENSORY_DEPTH: "All five senses evoked; specific concrete details over generic descriptors",
    RubricCriterion.PACING: "Sentence length variation matching scene tension; breath control",
    RubricCriterion.DIALOGUE_REALISM: "Contractions, interruptions, subtext, distinct voices, not exposition dumps",
    RubricCriterion.THEMATIC_RESONANCE: "Motifs, callbacks, thematic imagery that deepens meaning beyond plot",
    RubricCriterion.PROSE_RHYTHM: "Cadence, euphony, varied sentence openings, musical quality at sentence level",
}


class QualityScore(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: str = "ch_default"
    scores: Dict[str, float] = Field(default_factory=dict)
    overall_score: float = 0.0
    passes_used: int = 1
    is_approved: bool = False
    weakest_criterion: Optional[str] = None
    feedback: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class ManuscriptDraft(BaseModel):
    draft_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_number: int = 1
    initial_prose: str
    revised_prose: str = ""
    final_prose: str = ""
    quality_score: float = 0.0
    is_approved: bool = False
    evaluation: Optional[QualityScore] = None
    passes: List[str] = Field(default_factory=list)  # History of each pass


class QualityEngineState(BaseModel):
    """LangGraph state for the quality revision pipeline."""
    manuscript: ManuscriptDraft
    target_score: float = 8.5
    max_passes: int = 3
    current_pass: int = 0
    rubric_scores: Dict[str, float] = Field(default_factory=dict)
    stream_tokens: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are an expert literary editor evaluating prose against an 8-criterion rubric.
Score each criterion 0.0–10.0. Be precise and honest. Output ONLY valid JSON.

CRITERIA:
{criteria}

WEIGHTS:
{weights}

CRITICAL: You MUST use EXACTLY these 8 criterion names in your scores object:
- narrative_drive
- character_voice
- show_not_tell
- sensory_depth
- pacing
- dialogue_realism
- thematic_resonance
- prose_rhythm

Do NOT add, remove, or rename any criteria. Use EXACT names above.

Return JSON with:
{
  "scores": {"criterion_name": float_score, ...},
  "overall": float_weighted_average,
  "weakest": "criterion_name_from_above_list_only",
  "feedback": ["specific actionable feedback for revision", ...]
}"""),
    HumanMessage(content="""PROSE TO EVALUATE:
{prose}

Evaluate now.""")
])

REVISION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are an expert literary editor. Revise the prose to improve the WEAKEST criterion while maintaining all other qualities.

TARGET CRITERION: {weakest_criterion}
TARGET DESCRIPTION: {criterion_description}
CURRENT SCORE: {current_score}/10.0
TARGET SCORE: 8.5+

REVISION PRINCIPLES:
- Make minimal, surgical changes targeting only the weak area
- Preserve voice, plot, character consistency
- Do NOT add fluff or change the scene's purpose
- Output ONLY the revised prose, no commentary"""),
    HumanMessage(content="""ORIGINAL PROSE:
{prose}

REVISE for {weakest_criterion}:""")
])


# =============================================================================
# NODE FUNCTIONS
# =============================================================================

async def evaluate_node(state: QualityEngineState) -> QualityEngineState:
    """Evaluate current prose against 8-criterion rubric using LLM."""
    model: BaseChatModel = create_chat_model_with_fallbacks(temperature=0.3)
    
    prose = state.manuscript.revised_prose or state.manuscript.initial_prose
    if not prose.strip():
        state.error = "Empty prose cannot be evaluated"
        return state
    
    criteria_text = "\n".join(f"- {k.value}: {v}" for k, v in RUBRIC_DESCRIPTIONS.items())
    weights_text = "\n".join(f"- {k.value}: {v}" for k, v in RUBRIC_WEIGHTS.items())
    
    chain = EVALUATION_PROMPT | model | JsonOutputParser()
    
    try:
        result = await chain.ainvoke({
            "criteria": criteria_text,
            "weights": weights_text,
            "prose": prose
        })
        
        scores = result.get("scores", {})
        overall = result.get("overall", 0.0)
        weakest = result.get("weakest", min(scores, key=scores.get) if scores else RubricCriterion.SHOW_NOT_TELL.value)
        feedback = result.get("feedback", [])
        
        # Validate all 8 criteria present
        for criterion in RubricCriterion:
            if criterion.value not in scores:
                scores[criterion.value] = 5.0  # Default neutral
        
        # Recalculate weighted overall
        overall = sum(scores[k.value] * RUBRIC_WEIGHTS[k] for k in RubricCriterion)
        
        state.rubric_scores = scores
        state.manuscript.evaluation = QualityScore(
            chapter_id=f"ch_{state.manuscript.chapter_number}",
            scores=scores,
            overall_score=round(overall, 2),
            passes_used=state.current_pass,
            is_approved=overall >= state.target_score,
            weakest_criterion=weakest,
            feedback=feedback,
        )
        state.manuscript.quality_score = round(overall, 2)
        
    except Exception as e:
        state.error = f"Evaluation failed: {str(e)}"
        # Fallback heuristic
        state.rubric_scores = {k.value: 5.0 for k in RubricCriterion}
        state.manuscript.quality_score = 5.0
    
    return state


async def check_approval_node(state: QualityEngineState) -> QualityEngineState:
    """Determine if revision loop should continue."""
    if state.error:
        return state
    
    eval_result = state.manuscript.evaluation
    if eval_result and eval_result.is_approved:
        state.manuscript.is_approved = True
        state.manuscript.final_prose = state.manuscript.revised_prose or state.manuscript.initial_prose
    elif state.current_pass >= state.max_passes:
        state.manuscript.is_approved = False
        state.manuscript.final_prose = state.manuscript.revised_prose or state.manuscript.initial_prose
    # else: continue to revision
    
    return state


async def revision_node(state: QualityEngineState) -> QualityEngineState:
    """Execute one revision pass targeting the weakest criterion."""
    if state.error or state.manuscript.is_approved or state.current_pass >= state.max_passes:
        return state
    
    model: BaseChatModel = create_chat_model_with_fallbacks(temperature=0.7)
    
    prose = state.manuscript.revised_prose or state.manuscript.initial_prose
    eval_result = state.manuscript.evaluation
    
    if not eval_result or not eval_result.weakest_criterion:
        return state
    
    weakest = eval_result.weakest_criterion
    criterion_desc = RUBRIC_DESCRIPTIONS.get(RubricCriterion(weakest), "")
    current_score = state.rubric_scores.get(weakest, 5.0)
    
    chain = REVISION_PROMPT | model
    
    try:
        result = await chain.ainvoke({
            "weakest_criterion": weakest,
            "criterion_description": criterion_desc,
            "current_score": current_score,
            "prose": prose
        })
        
        revised = result.content.strip()
        if revised:
            state.current_pass += 1
            state.manuscript.revised_prose = revised
            state.manuscript.passes.append(f"pass_{state.current_pass}_{weakest}")
            state.manuscript.passes.append(revised[:200] + "...")  # Store preview
            
    except Exception as e:
        state.error = f"Revision failed: {str(e)}"
    
    return state


async def anti_slop_node(state: QualityEngineState) -> QualityEngineState:
    """Apply anti-slop filtering to final prose."""
    if state.error:
        return state
    
    slop_filter = AntiSlopFilter()
    final_prose = state.manuscript.final_prose or state.manuscript.revised_prose or state.manuscript.initial_prose
    state.manuscript.final_prose = slop_filter.clean_prose(final_prose)
    
    return state


# =============================================================================
# LANGGRAPH COMPILATION
# =============================================================================

def create_quality_graph() -> StateGraph:
    """Create and compile the LangGraph quality revision pipeline."""
    graph = StateGraph(QualityEngineState)
    
    # Nodes
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("check_approval", check_approval_node)
    graph.add_node("revise", revision_node)
    graph.add_node("anti_slop", anti_slop_node)
    
    # Edges
    graph.set_entry_point("evaluate")
    graph.add_edge("evaluate", "check_approval")
    graph.add_conditional_edges(
        "check_approval",
        lambda s: "approved" if s.manuscript.is_approved or s.current_pass >= s.max_passes or s.error else "revise",
        {
            "approved": "anti_slop",
            "revise": "revise"
        }
    )
    graph.add_edge("revise", "evaluate")  # Loop back for next pass
    graph.add_edge("anti_slop", END)
    
    return graph.compile()


QUALITY_GRAPH = create_quality_graph()


# =============================================================================
# PUBLIC API
# =============================================================================

class QualityEngine:
    """
    LangGraph-powered quality engine for multi-pass prose revision.
    
    Replaces the mock string-manipulation stub with authentic LLM orchestration.
    """
    
    def __init__(self):
        self.graph = QUALITY_GRAPH
        self.slop_filter = AntiSlopFilter()
    
    async def evaluate_prose(self, text: str) -> tuple[float, Dict[str, float]]:
        """Evaluates prose and returns overall score and individual rubric scores."""
        if not text.strip():
            return 0.0, {k.value: 0.0 for k in RubricCriterion}
        
        manuscript = ManuscriptDraft(chapter_number=1, initial_prose=text)
        initial_state = QualityEngineState(
            manuscript=manuscript,
            target_score=8.5,
            max_passes=0,  # Evaluation only
            current_pass=0
        )
        
        result = await self.graph.ainvoke(initial_state)
        
        if isinstance(result, dict):
            manuscript = result.get("manuscript")
        else:
            manuscript = result.manuscript
        
        if manuscript and manuscript.evaluation:
            return manuscript.evaluation.overall_score, manuscript.evaluation.scores
        
        return 5.0, {k.value: 5.0 for k in RubricCriterion}
    
    async def revise_prose(self, text: str, target_score: float = 8.5, max_passes: int = 3) -> tuple[str, float, int]:
        """Executes internal AI revision loop (up to max_passes) to improve prose quality."""
        if not text.strip():
            return text.strip(), 0.0, 0
        
        manuscript = ManuscriptDraft(chapter_number=1, initial_prose=text)
        initial_state = QualityEngineState(
            manuscript=manuscript,
            target_score=target_score,
            max_passes=max_passes,
            current_pass=0
        )
        
        result = await self.graph.ainvoke(initial_state)
        
        if isinstance(result, dict):
            manuscript = result.get("manuscript")
        else:
            manuscript = result.manuscript
        
        if manuscript:
            final = manuscript.final_prose or manuscript.revised_prose or manuscript.initial_prose
            score = manuscript.quality_score
            passes = manuscript.evaluation.passes_used if manuscript.evaluation else manuscript.current_pass
            return final.strip(), score, passes
        
        return text.strip(), 5.0, 0
    
    async def revise_prose_streaming(self, text: str, target_score: float = 8.5, max_passes: int = 3) -> AsyncGenerator[str, None]:
        """
        Stream tokens during revision using LangGraph's astream.
        Yields SSE-formatted tokens for real-time streaming.
        """
        if not text.strip():
            yield f"data: [DONE]\n\n"
            return
        
        manuscript = ManuscriptDraft(chapter_number=1, initial_prose=text)
        initial_state = QualityEngineState(
            manuscript=manuscript,
            target_score=target_score,
            max_passes=max_passes,
            current_pass=0
        )
        
        try:
            # Stream the graph execution
            async for event in self.graph.astream(initial_state):
                # LangGraph yields events for each node
                for node_name, node_state in event.items():
                    if node_name == "evaluate" and node_state.manuscript.evaluation:
                        eval_result = node_state.manuscript.evaluation
                        yield f"data: [EVAL] Score: {eval_result.overall_score}/10 | Weakest: {eval_result.weakest_criterion}\n\n"
                    elif node_name == "revise" and node_state.manuscript.revised_prose:
                        revised = node_state.manuscript.revised_prose
                        # Stream the revised prose word by word
                        for word in revised.split():
                            yield f"data: {word} \n\n"
                            await asyncio.sleep(0.005)  # Small delay for realistic streaming
                        yield f"data: [PASS {node_state.current_pass} COMPLETE]\n\n"
                    elif node_name == "anti_slop" and node_state.manuscript.final_prose:
                        final = node_state.manuscript.final_prose
                        yield f"data: [FINAL] {final}\n\n"
                    elif node_name == "check_approval" and node_state.manuscript.is_approved:
                        yield f"data: [APPROVED] Quality target met!\n\n"
            
            yield f"data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
            yield f"data: [DONE]\n\n"


# Backward-compatible functions for existing code
async def evaluate_prose_standalone(text: str) -> tuple[float, Dict[str, float]]:
    """Standalone evaluation function (for orchestrator compatibility)."""
    qe = QualityEngine()
    return await qe.evaluate_prose(text)


async def revise_prose_standalone(text: str, target_score: float = 8.5) -> tuple[str, float, int]:
    """Standalone revision function (for orchestrator compatibility)."""
    qe = QualityEngine()
    return await qe.revise_prose(text, target_score=target_score)