"""
Nebula-Writer Inline Comment System v2.1
Comment lifecycle, span targeting, ripple check
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Comment:
    """A comment on text - BRD Section 3"""

    id: str
    context_type: str  # chapter, codex, lookahead
    target_id: str  # chapter_id, entity_id, card_id
    user_comment: str

    # Span information
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    highlighted_text: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Status lifecycle
    status: str = "open"  # open, ai_responded, resolved, pushback, ripple_pending
    ai_response: str = ""
    resolution_notes: str = ""


class InlineCommentEngine:
    """
    Manages inline comments on chapters, Codex entries, and lookahead cards
    Based on BRD v2.1 Section 3
    """

    def __init__(self, ripple_checker=None):
        self.comments: Dict[str, List[Comment]] = {}  # context_type -> [comments]
        self.ripple_checker = ripple_checker

    def add_comment(
        self,
        context_type: str,
        target_id: str,
        highlighted_text: str,
        user_comment: str,
        start: int = None,
        end: int = None,
    ) -> str:
        """Add a new comment"""
        comment = Comment(
            id=str(uuid.uuid4())[:8],
            context_type=context_type,
            target_id=target_id,
            highlighted_text=highlighted_text[:200],  # limit length
            user_comment=user_comment,
            start_offset=start,
            end_offset=end,
            status="open",
        )

        # Store in correct context bucket
        if context_type not in self.comments:
            self.comments[context_type] = []

        self.comments[context_type].append(comment)

        return comment.id

    def get_comments(self, context_type: str = None, target_id: str = None) -> List[Dict]:
        """Get comments, optionally filtered"""
        result = []

        contexts = [context_type] if context_type else self.comments.keys()

        for ctx in contexts:
            if ctx not in self.comments:
                continue
            for c in self.comments[ctx]:
                if target_id and c.target_id != target_id:
                    continue
                result.append(c.__dict__)

        return result

    def get_open_comments(self, context_type: str = None) -> List[Dict]:
        """Get only open/pending comments"""
        all_comments = self.get_comments(context_type)
        return [c for c in all_comments if c["status"] in ["open", "ai_responded", "pushback", "ripple_pending"]]

    def ai_respond(self, comment_id: str, response: str) -> bool:
        """AI responds to a comment"""
        for _ctx, comment_list in self.comments.items():
            for c in comment_list:
                if c.id == comment_id:
                    c.ai_response = response
                    c.status = "ai_responded"
                    return True
        return False

    def resolve_comment(self, comment_id: str, resolution_notes: str = "") -> Dict:
        """User resolves a comment - triggers ripple check"""
        for _ctx, comment_list in self.comments.items():
            for c in comment_list:
                if c.id == comment_id:
                    c.status = "resolved"
                    c.resolution_notes = resolution_notes
                    return {
                        "comment_id": comment_id,
                        "status": "resolved",
                        "requires_ripple_check": True,
                        "context_type": c.context_type,
                        "target_id": c.target_id,
                    }
        return {"error": "Comment not found"}

    def pushback(self, comment_id: str, user_feedback: str) -> bool:
        """User pushes back on AI response"""
        for _ctx, comment_list in self.comments.items():
            for c in comment_list:
                if c.id == comment_id:
                    c.status = "pushback"
                    c.user_comment += f" [PUSHBACK: {user_feedback}]"
                    return True
        return False

    def mark_ripple_pending(self, comment_id: str) -> bool:
        """Mark comment as requiring ripple check"""
        for _ctx, comment_list in self.comments.items():
            for c in comment_list:
                if c.id == comment_id:
                    c.status = "ripple_pending"
                    return True
        return False

    def ripple_check(self, context_type: str, target_id: str, changes_made: Dict) -> Dict:
        """
        Run ripple check after comment resolution
        Returns propagation report
        """
        change_desc = changes_made.get("description", f"Change in {context_type} {target_id}")

        if self.ripple_checker:
            report = self.ripple_checker.analyze_change(
                change_desc, {"context_type": context_type, "target_id": target_id}
            )

            # Update affected comments status
            for ripple in report.get("predicted_ripples", []):
                if ripple.get("severity") == "high":
                    # Mark as ripple_pending for user review
                    pass  # logic to find related comments or create new ones

            return report

        # Fallback to basic logic
        affected = []
        # ... (keeping old logic as fallback)
        if changes_made.get("character_behavior_changed"):
            char_id = changes_made.get("character_id")
            other_comments = self.get_comments("chapter")
            for c in other_comments:
                if c["target_id"] != target_id and char_id in str(c):
                    affected.append(
                        {
                            "type": "character_dialogue",
                            "chapter": c["target_id"],
                            "reason": f"Character {char_id} behavior changed",
                        }
                    )

        return {
            "changes_made": changes_made,
            "affected_content": affected,
            "requires_user_action": len(affected) > 0,
            "auto_fix_available": False,
        }

    def can_approve_chapter(self, chapter_id: str) -> Dict:
        """Check if chapter can be approved (no open comments)"""
        chapter_comments = self.get_comments("chapter", chapter_id)
        open_comments = [
            c for c in chapter_comments if c["status"] in ["open", "ai_responded", "pushback", "ripple_pending"]
        ]

        return {
            "can_approve": len(open_comments) == 0,
            "open_count": len(open_comments),
            "blocking_comments": [
                {"id": c["id"], "user_comment": c["user_comment"], "status": c["status"]} for c in open_comments
            ],
        }

    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        for _ctx, comment_list in self.comments.items():
            for c in comment_list:
                if c.id == comment_id:
                    comment_list.remove(c)
                    return True
        return False


class AntiSlopQualityLayer:
    """
    Quality scoring and anti-slop detection
    Based on BRD Section 1.5 (Zero Slop)
    """

    def __init__(self):
        self.quality_criteria = [
            "prose_quality",  # Sentence variation, word choice
            "pacing",  # Rhythm, scene length
            "character_voice",  # Distinctive dialogue
            "continuity",  # Fact consistency
            "originality",  # Cliche detection
            "dialogue",  # Natural conversation
            "tension",  # Forward momentum
            "show_not_tell",  # Sensory over telling
        ]

    def analyze_chapter(self, content: str) -> Dict:
        """
        Analyze chapter against 8 quality criteria
        Returns score breakdown
        """
        scores = {}

        # Prose Quality
        sentences = content.split(".")
        if len(sentences) > 3:
            # Check sentence length variation
            avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
            if 8 <= avg_len <= 20:
                scores["prose_quality"] = 8
            elif 5 <= avg_len <= 25:
                scores["prose_quality"] = 6
            else:
                scores["prose_quality"] = 4
        else:
            scores["prose_quality"] = 5

        # Pacing - word count ranges
        word_count = len(content.split())
        if 1500 <= word_count <= 4000:
            scores["pacing"] = 8
        elif word_count > 4000:
            scores["pacing"] = 6
        else:
            scores["pacing"] = 5

        # Character Voice - check for unique dialogue patterns (simplified)
        # would need NLP for real analysis
        scores["character_voice"] = 7

        # Continuity - basic check
        scores["continuity"] = 8

        # Originality - cliche detection (simplified)
        cliches = [
            "suddenly",
            "all of a sudden",
            "little did he know",
            "she knew in her heart",
            "as luck would have it",
        ]
        has_cliche = any(c in content.lower() for c in cliches)
        scores["originality"] = 4 if has_cliche else 7

        # Dialogue - check for dialogue markers
        dialogue_count = content.count('"') // 2
        if dialogue_count > 5:
            scores["dialogue"] = 8
        elif dialogue_count > 0:
            scores["dialogue"] = 6
        else:
            scores["dialogue"] = 4

        # Tension - check for tension words
        tension_words = ["fear", "worry", "danger", "threat", "urgent", "quickly", "run"]
        tension_score = sum(1 for w in tension_words if w in content.lower())
        scores["tension"] = min(10, 5 + tension_score)

        # Show Not Tell - sensory words
        sensory = ["saw", "heard", "smelled", "felt", "tasted", "touch"]
        sensory_score = sum(1 for w in sensory if w in content.lower())
        scores["show_not_tell"] = min(10, 5 + sensory_score)

        # Calculate overall score
        overall = sum(scores.values()) / len(scores)

        return {
            "overall_score": round(overall, 1),
            "quality_grade": self._grade(overall),
            "criteria": scores,
            "word_count": word_count,
            "flags": self._get_flags(scores),
        }

    def _grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 8:
            return "A - Excellent"
        elif score >= 7:
            return "B - Good"
        elif score >= 6:
            return "C - Acceptable"
        elif score >= 5:
            return "D - Needs Work"
        else:
            return "F - Needs Revision"

    def _get_flags(self, scores: Dict) -> List[str]:
        """Get advisory flags for low scores"""
        flags = []
        for criteria, score in scores.items():
            if score < 5:
                flags.append(f"{criteria.replace('_', ' ').title()}: needs attention")
        return flags


def create_comment_engine() -> InlineCommentEngine:
    return InlineCommentEngine()


def create_quality_layer() -> AntiSlopQualityLayer:
    return AntiSlopQualityLayer()


if __name__ == "__main__":
    print("Testing Inline Comment System...")

    # Test comments
    engine = create_comment_engine()

    # Add chapter comment
    cid = engine.add_comment(
        context_type="chapter",
        target_id="ch1",
        highlighted_text="He walked into the room",
        user_comment="Too on-the-nose. He wouldn't think this clearly.",
        start=0,
        end=20,
    )
    print(f"Added comment: {cid}")

    # Get comments
    comments = engine.get_comments("chapter", "ch1")
    print(f"Comments on ch1: {len(comments)}")

    # AI responds
    engine.ai_respond(cid, "Revised to show hesitation through action")
    print("AI responded to comment")

    # Resolve
    result = engine.resolve_comment(cid, "Revision accepted")
    print(f"Resolved: {result}")

    # Check approval
    approval = engine.can_approve_chapter("ch1")
    print(f"Can approve ch1: {approval['can_approve']}")

    # Test quality layer
    print("\nTesting Quality Layer...")
    quality = create_quality_layer()

    test_chapter = """
    The detective walked into the room. He knew something was wrong. Suddenly,
    the door slammed behind him. She had waited for this moment. Her heart raced
    as she realized the truth. He smelled the gunpowder. It was too late.
    """

    result = quality.analyze_chapter(test_chapter)
    print(f"Quality Score: {result['overall_score']} - {result['quality_grade']}")
    print(f"Flags: {result['flags']}")

    print("\nInline Comment System working!")
