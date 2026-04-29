"""
Nebula-Writer Ripple Checker v2.1
Detects narrative inconsistencies and cascading effects of story changes.
"""

import json
from typing import Any, Dict, List

from nebula_writer.audit import StoryAuditor


class RippleChecker:
    """
    Analyzes story changes for ripple effects.
    Combines AI prediction with structural audit.
    """

    def __init__(self, db, ai_writer):
        self.db = db
        self.ai = ai_writer
        self.auditor = StoryAuditor(db)

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

    async def _predict_ripples(self, change: str, context: Dict = None) -> Dict:
        """Use AI to predict narrative ripple effects"""
        system_prompt = """You are a Narrative Consistency Expert.
        Analyze the proposed story change and predict how it will ripple through the existing world, character arcs, and plot threads.

        Identify:
        1. Cascading changes (What else MUST change?).
        2. Potential contradictions (What does this break?).
        3. Narrative Debt (What needs to be fixed later?).

        Output format: JSON only.
        {
            "ripples": [{"target": "Entity/Chapter/Plot", "effect": "...", "severity": "low|medium|high"}],
            "debt": ["..."]
        }
        """

        # Build context string
        story_state = {
            "entities": self.db.get_entities()[:5],  # Sample for tokens
            "plot_threads": self.db.get_plot_threads()[:5],
        }

        prompt = f"CHANGE: {change}\nCONTEXT: {json.dumps(context or {})}\nSTORY STATE: {json.dumps(story_state)}"

        try:
            response = await self.ai.generate(prompt, system_prompt=system_prompt, role="ripple")
            # Find JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            return json.loads(response[start:end])
        except:
            return {"ripples": [], "debt": ["AI prediction failed - manual review needed"]}

    def _audit_for_change(self, change: str) -> List[Dict]:
        """Perform a structural audit based on the change"""
        # This uses the heuristics in StoryAuditor
        # For now, we'll return a general check
        # In a real implementation, we'd map the 'change' to specific audit calls
        return self.auditor.audit_all_chapters().get("results", [])[:1]  # Just a sample

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
            "correction_prompt": f"The following narrative constraints were violated: {', '.join(violations)}. Please rewrite the scene to adhere to these rules." if violations else None
        }


def create_ripple_checker(db, ai_writer):
    return RippleChecker(db, ai_writer)
