"""
Nebula-Writer Export Module
Export story to various formats (JSON, Markdown, HTML, ePub)
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from codex import CodexDatabase


class StoryExporter:
    """Export story to various formats"""
    
    def __init__(self, db: CodexDatabase):
        self.db = db
    
    def to_markdown(self) -> str:
        """Export story as Markdown"""
        md = f"# Story\n\n*Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Entities
        md += "## Characters\n\n"
        for e in self.db.get_entities("character"):
            md += f"### {e['name']}\n{e.get('description', '')}\n\n"
            attrs = self.db.get_attributes(e['id'])
            if attrs:
                md += "**Attributes:** " + ", ".join([f"{a['key']}: {a['value']}" for a in attrs]) + "\n\n"
        
        # Locations
        md += "## Locations\n\n"
        for e in self.db.get_entities("location"):
            md += f"### {e['name']}\n{e.get('description', '')}\n\n"
        
        # Chapters
        chapters = self.db.get_chapters()
        if chapters:
            md += "---\n\n## Chapters\n\n"
            for ch in sorted(chapters, key=lambda x: x['number']):
                md += f"### Chapter {ch['number']}: {ch.get('title', 'Untitled')}\n\n"
                if ch.get('summary'):
                    md += f*"Summary: {ch['summary']}*\n\n"
                md += (ch.get('content') or '') + "\n\n"
        
        return md
    
    def to_html(self) -> str:
        """Export story as HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Story</title>
    <style>
        body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; }}
        h1 {{ text-align: center; color: #333; }}
        h2 {{ color: #555; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #666; }}
        .character {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 3px solid #8b5cf6; }}
        .location {{ background: #f0f9ff; padding: 15px; margin: 10px 0; border-left: 3px solid #06b6d4; }}
        .chapter {{ margin: 40px 0; }}
        .summary {{ font-style: italic; color: #666; }}
    </style>
</head>
<body>
    <h1>Story</h1>
    
    <h2>Characters</h2>
"""
        for e in self.db.get_entities("character"):
            html += f'    <div class="character">\n        <h3>{e["name"]}</h3>\n        <p>{e.get("description", "")}</p>\n    </div>\n'
        
        html += "\n    <h2>Locations</h2>\n"
        for e in self.db.get_entities("location"):
            html += f'    <div class="location">\n        <h3>{e["name"]}</h3>\n        <p>{e.get("description", "")}</p>\n    </div>\n'
        
        chapters = self.db.get_chapters()
        if chapters:
            html += "\n    <hr>\n\n"
            for ch in sorted(chapters, key=lambda x: x['number']):
                html += f'    <div class="chapter">\n        <h2>Chapter {ch["number"]}: {ch.get("title", "Untitled")}</h2>\n'
                if ch.get('summary'):
                    html += f'        <p class="summary">{ch["summary"]}</p>\n'
                content = ch.get('content', '')
                # Simple paragraph wrapping
                for para in content.split('\n\n'):
                    if para.strip():
                        html += f'        <p>{para}</p>\n'
                html += "    </div>\n"
        
        html += """
</body>
</html>"""
        return html
    
    def to_json(self) -> Dict:
        """Export as JSON"""
        return {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "entities": self.db.get_entities(),
            "relationships": self.db.get_relationships(),
            "events": self.db.get_events(),
            "chapters": self.db.get_chapters(),
            "stats": self.db.get_stats()
        }
    
    def save(self, format: str, filepath: str):
        """Save to file"""
        if format == "markdown":
            content = self.to_markdown()
        elif format == "html":
            content = self.to_html()
        elif format == "json":
            content = json.dumps(self.to_json(), indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        Path(filepath).write_text(content)
        return filepath


if __name__ == "__main__":
    db = CodexDatabase()
    exporter = StoryExporter(db)
    
    print("Exported to Markdown:", exporter.save("markdown", "story.md"))
    print("Exported to HTML:", exporter.save("html", "story.html"))
    print("Exported to JSON:", exporter.save("json", "story.json"))
