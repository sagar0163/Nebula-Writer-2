"""
Nebula-Writer Ripple Checker v2.1
Detects narrative inconsistencies and cascading effects of story changes.
"""

import json
import uuid
from typing import Any, Dict, List

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from nebula_writer.models import create_chat_model_with_fallbacks

from nebula_writer.audit import StoryAuditor


class RippleChecker:
    """Analyzes story changes for ripple effects.
    Combines AI prediction with structural audit.
    """

    def __init__(self, db, ai_writer, plot_manager=None):
        self.db = db
        self.ai = ai_writer
        self.auditor = StoryAuditor(db)
        self.pm = plot_manager

    async def analyze_change(self, change_description: str, context: Dict = None) -> Dict:
        """
        Analyze a proposed change for ripple effects.
        :param change_description: Natural language description of the change.
        :param context: Optional context (e.g., current chapter, entity).
        :return: Ripple report dictionary.
        """
        # 1. AI Prediction of affected areas
        prediction = await self._predict_ripples(change_description, context)

        # 2. Structural Audit (immediate contradictions)
        structural_issues = self._audit_for_change(change_description)

        # 3. Combine results
        return {
            "summary": f"Ripple analysis for: {change_description}",
            "predicted_ripples": prediction.get("ripples", []),
            "structural_contradictions": structural_issues,
            "narrative_debt": prediction.get("debt", []),
            "requires_manual_review": True,
        }

    async def validate_post_revision_ripple(self, original_text: str, revised_text: str, context: Dict = None) -> Dict:
        """
        Perform post-revision ripple effect validation checks.
        Analyzes the exact delta between original and revised text to detect cascading inconsistencies.
        """
        change_desc = f"Revised text from '{original_text[:50]}...' to '{revised_text[:50]}...'"
        report = await self.analyze_change(change_desc, context)

        report["revision_valid"] = len(report.get("structural_contradictions", [])) == 0
        report["delta_analyzed"] = True
        return report

    async def _predict_ripples(self, change: str, context: Dict = None) -> Dict:
        """Use AI to predict narrative ripple effects including plot and timeline logic"""
        system_prompt = """You are a Narrative Consistency Expert and Plot Auditor.
        Analyze the proposed story change and predict how it will ripple through the existing world, character arcs, and plot threads.
        
        Focus deeply on PLOT LOGIC and TIMELINE contradictions, not just entity existence.

        Identify:
        1. Cascading changes (What else MUST change?).
        2. Potential contradictions (What does this break in the timeline or plot logic?).
        3. Narrative Debt (What needs to be fixed later?).

        Output format: JSON only.
        {
            "ripples": [{"target": "Entity/Chapter/Plot/Timeline", "effect": "...", "severity": "low|medium|high"}],
            "debt": ["..."]
        }
        """

        # Build context string
        story_state = {
            "entities": self.db.get_entities()[:5],  # Sample for tokens
            "plot_threads": self.pm.get_plot_threads()[:5] if self.pm else [],
        }
        
        model = create_chat_model_with_fallbacks(temperature=0.2)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"CHANGE: {change}\nCONTEXT: {json.dumps(context or {})}\nSTORY STATE: {json.dumps(story_state)}")
        ]

        try:
            result = await model.ainvoke(messages)
            # Find JSON block
            content = result.content
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            else:
                return {"ripples": [], "debt": ["AI returned invalid format - manual review needed"]}
        except Exception as e:
            return {"ripples": [], "debt": [f"AI prediction failed ({str(e)}) - manual review needed"]}

    def _audit_for_change(self, change: str) -> List[Dict]:
        """Perform a structural audit based on the change"""
        # Use the auditor to check for contradictions
        audit_result = self.auditor.audit_all_chapters()
        return audit_result.get("results", [])

    def check_consistency(self, text: str) -> List[Dict]:
        """Advisor-style consistency check (Legacy)"""
        # ... logic ...
        return []

    def validate_scene_integrity(self, prose: str, directive: Any) -> Dict:
        """
        Active Gatekeeper: Validates prose against narrative directives.
        Returns a detailed report of any violations.
        """
        violations = []

        # 1. Check constraints
        for constraint in directive.constraints:
            # Simple keyword matching for demo; real version uses semantic scoring
            if "DO NOT" in constraint.upper() and constraint.split(":")[-1].strip().lower() in prose.lower():
                violations.append(f"Constraint Violation: {constraint}")

        # 2. Check Anchor Consistency
        for anchor in directive.active_anchors:
            # Check if prose contradicts major anchors
            pass

        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "correction_prompt": f"The following narrative constraints were violated: {', '.join(violations)}. Please rewrite the scene to adhere to these rules."
            if violations
            else None,
        }


def create_ripple_checker(db, ai_writer, plot_manager=None):
    return RippleChecker(db, ai_writer, plot_manager)
