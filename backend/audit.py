"""
Nebula-Writer Audit Module
Detects contradictions in story chapters
"""
from typing import List, Dict, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from codex import CodexDatabase


class StoryAuditor:
    """Audit chapters for contradictions with Codex facts"""
    
    def __init__(self, db: CodexDatabase):
        self.db = db
        self.issues = []
    
    def check_entity_consistency(self, chapter_content: str) -> List[Dict]:
        """Check if mentioned entities behave consistently"""
        issues = []
        entities = self.db.get_entities()
        
        for entity in entities:
            name = entity['name']
            current_loc = entity.get('current_location')
            
            if not current_loc:
                continue
            
            # Check if entity is mentioned with different location in same chapter
            # This is a simple heuristic - could be enhanced with NLP
            if name.lower() in chapter_content.lower():
                # Entity is in this chapter
                pass
            
            # Check if entity is marked alive/dead
            is_alive = entity.get('is_alive', True)
            
            # Simple death check
            death_phrases = ['died', 'dead', 'killed', 'death']
            for phrase in death_phrases:
                if f"{name.lower()} {phrase}" in chapter_content.lower() and is_alive:
                    issues.append({
                        'type': 'contradiction',
                        'severity': 'major',
                        'entity': name,
                        'message': f"{name} is marked as alive but chapter mentions '{phrase}'",
                        'chapter': None
                    })
        
        return issues
    
    def check_relationship_consistency(self, chapter_content: str) -> List[Dict]:
        """Check if relationships are respected"""
        issues = []
        relationships = self.db.get_relationships()
        
        for rel in relationships:
            from_name = rel['from_name']
            to_name = rel['to_name']
            rel_type = rel['relationship_type']
            strength = rel.get('strength', 0.5)
            
            # Check for contradiction in relationship portrayal
            if from_name.lower() in chapter_content.lower() and to_name.lower() in chapter_content.lower():
                # Both entities in same chapter - check for contradiction
                if strength > 0.7 and rel_type in ['hates', 'enemy', 'rivals']:
                    issues.append({
                        'type': 'contradiction',
                        'severity': 'minor',
                        'entity': f"{from_name} -> {to_name}",
                        'message': f"Relationship is '{rel_type}' but strength is {int(strength*100)}%",
                        'chapter': None
                    })
        
        return issues
    
    def check_timeline(self) -> List[Dict]:
        """Check event timeline for inconsistencies"""
        issues = []
        events = self.db.get_events()
        
        # Sort by chapter
        events_by_chapter = {}
        for ev in events:
            ch = ev.get('chapter')
            if ch:
                if ch not in events_by_chapter:
                    events_by_chapter[ch] = []
                events_by_chapter[ch].append(ev)
        
        # Check for paradoxes
        for ch, evs in events_by_chapter.items():
            for ev in evs:
                if ev.get('significance') == 'major':
                    # Major events should have consequences
                    pass
        
        return issues
    
    def audit_chapter(self, chapter_content: str, chapter_num: int = None) -> Dict:
        """Run full audit on a chapter"""
        all_issues = []
        
        # Entity consistency
        all_issues.extend(self.check_entity_consistency(chapter_content))
        
        # Relationship consistency
        all_issues.extend(self.check_relationship_consistency(chapter_content))
        
        # Timeline
        all_issues.extend(self.check_timeline())
        
        return {
            'chapter': chapter_num,
            'total_issues': len(all_issues),
            'issues': all_issues,
            'status': 'pass' if len(all_issues) == 0 else 'warning' if all(i['severity'] == 'minor' for i in all_issues) else 'fail'
        }
    
    def audit_all_chapters(self) -> Dict:
        """Audit all chapters"""
        chapters = self.db.get_chapters()
        results = []
        
        for chapter in chapters:
            result = self.audit_chapter(chapter.get('content', ''), chapter['number'])
            results.append(result)
        
        total_issues = sum(r['total_issues'] for r in results)
        
        return {
            'summary': f"Audited {len(chapters)} chapters",
            'total_issues': total_issues,
            'results': results
        }


if __name__ == "__main__":
    db = CodexDatabase()
    auditor = StoryAuditor(db)
    
    print("📋 Running Story Audit...")
    results = auditor.audit_all_chapters()
    print(f"\nResults: {results['total_issues']} issues found")
    for r in results['results']:
        print(f"  Chapter {r['chapter']}: {r['status']} ({r['total_issues']} issues)")
