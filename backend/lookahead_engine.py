"""
Nebula-Writer Lookahead Engine v2.1
Generates rolling 3-chapter lookahead cards
"""
import json
from typing import List, Dict, Optional
from codex import CodexDatabase
from plot_manager import PlotManager
from ai_writer import AIWriter

class LookaheadEngine:
    """
    Rolling 3-Chapter Lookahead Engine - BRD Section 4
    Generates chapter proposals based on story compass and graph.
    """
    
    def __init__(self, db: CodexDatabase, plot_manager: PlotManager, ai_writer: AIWriter):
        self.db = db
        self.pm = plot_manager
        self.ai = ai_writer
        
    def generate_lookahead(self) -> List[Dict]:
        """
        Generate three lookahead cards - BRD Section 4.2
        """
        # 1. Get Story Compass State
        anchors = self.db.get_story_anchors()
        tensions = self.db.get_open_tensions()
        momentum = self.db.get_narrative_momentum()
        seeds = self.pm.get_foreshadowing(unfulfilled_only=True)
        chapters = self.db.get_chapters()
        last_chapter_num = chapters[-1]['number'] if chapters else 0
        
        # 2. Build Context for AI
        context = {
            "last_chapter": last_chapter_num,
            "anchors": anchors,
            "open_tensions": tensions,
            "momentum": momentum,
            "planted_seeds": [s['content'] for s in seeds[:5]], # top 5 seeds
            "entities": [{"name": e['name'], "type": e['type']} for e in self.db.get_entities()[:10]]
        }
        
        # 3. Request AI Proposals
        prompt = f"""
        Based on the current story state, generate a Rolling 3-Chapter Lookahead.
        Current Story State: {json.dumps(context)}
        
        Requirements:
        - Card 1: Next Chapter ({last_chapter_num + 1}). High certainty.
        - Card 2: Chapter +1 ({last_chapter_num + 2}). Medium certainty.
        - Card 3: Chapter +2 ({last_chapter_num + 3}). Low certainty, directional.
        
        Return ONLY a JSON array of 3 objects with these fields:
        "chapter_number", "title", "scene_intention", "opening_image", "character_in_focus", "story_question"
        """
        
        # Use AIWriter's generate method
        # Note: AIWriter uses _generate internally but exposes generate_scene which might be more suitable
        try:
            # We'll use a generic generation call
            response = self.ai._generate(prompt, system_prompt="You are an expert novelist planning the next steps of a story.")
        except AttributeError:
            # Fallback if _generate is private or named differently
            response = self.ai.generate_scene(prompt, system_prompt="You are an expert novelist planning the next steps of a story.")
        
        # Extract JSON (simplified extraction)
        try:
            # Find the first [ and last ]
            start = response.find('[')
            end = response.rfind(']') + 1
            cards = json.loads(response[start:end])
            
            # Save to database
            self.db.clear_lookahead_cards(status='draft')
            for card in cards:
                self.db.add_lookahead_card(
                    chapter_number=card['chapter_number'],
                    title=card.get('title'),
                    intention=card.get('scene_intention'),
                    opening=card.get('opening_image'),
                    focus=card.get('character_in_focus'),
                    question=card.get('story_question')
                )
            return cards
        except Exception as e:
            print(f"Error parsing lookahead: {response[:200]}... Error: {e}")
            return []

    def approve_card(self, card_id: int):
        """Approve a card - marks it for writing"""
        return self.db.update_lookahead_card_status(card_id, 'approved')

def create_lookahead_engine(db, pm, ai):
    return LookaheadEngine(db, pm, ai)
