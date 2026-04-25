"""
Nebula-Writer Export Module
Export story to various formats (JSON, Markdown, HTML, ePub)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

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
            attrs = self.db.get_attributes(e["id"])
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
            for ch in sorted(chapters, key=lambda x: x["number"]):
                md += f"### Chapter {ch['number']}: {ch.get('title', 'Untitled')}\n\n"
                if ch.get("summary"):
                    md += f * "Summary: {ch['summary']}*\n\n"
                md += (ch.get("content") or "") + "\n\n"

        return md

    def to_html(self) -> str:
        """Export story as HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Story</title>
    <style>
        body { font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; }
        h1 { text-align: center; color: #333; }
        h2 { color: #555; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        h3 { color: #666; }
        .character { background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 3px solid #8b5cf6; }
        .location { background: #f0f9ff; padding: 15px; margin: 10px 0; border-left: 3px solid #06b6d4; }
        .chapter { margin: 40px 0; }
        .summary { font-style: italic; color: #666; }
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
            for ch in sorted(chapters, key=lambda x: x["number"]):
                html += f'    <div class="chapter">\n        <h2>Chapter {ch["number"]}: {ch.get("title", "Untitled")}</h2>\n'
                if ch.get("summary"):
                    html += f'        <p class="summary">{ch["summary"]}</p>\n'
                content = ch.get("content", "")
                # Simple paragraph wrapping
                for para in content.split("\n\n"):
                    if para.strip():
                        html += f"        <p>{para}</p>\n"
                html += "    </div>\n"

        html += """
</body>
</html>"""
        return html

    def to_json(self) -> Dict:
        """Export as JSON"""
        return {
            "metadata": {"generated": datetime.now().isoformat(), "version": "1.0"},
            "entities": self.db.get_entities(),
            "relationships": self.db.get_relationships(),
            "events": self.db.get_events(),
            "chapters": self.db.get_chapters(),
            "stats": self.db.get_stats(),
        }

    def to_epub(self, title: str = "My Novel", author: str = "Author", description: str = "") -> tuple:
        """
        Export story as proper EPUB 3.0
        Returns tuple of (container_xml, content_opf, content_html_list)
        """
        import uuid
        import zipfile
        from datetime import datetime
        from io import BytesIO

        chapters = self.db.get_chapters()
        self.db.get_entities()

        # Create ZIP in memory
        epub_bytes = BytesIO()
        with zipfile.ZipFile(epub_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. mimetype (must be first, uncompressed)
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

            # 2. META-INF/container.xml
            container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
            zf.writestr("META-INF/container.xml", container_xml)

            # 3. OEBPS/content.opf
            uuid_str = str(uuid.uuid4())
            modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # Build manifest
            manifest_items = []
            nav_id = "nav"
            manifest_items.append(
                f'    <item id="{nav_id}" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
            )
            manifest_items.append('    <item id="css" href="styles.css" media-type="text/css"/>')

            chapter_items = []
            for i, ch in enumerate(sorted(chapters, key=lambda x: x["number"])):
                ch_id = f"ch{i + 1}"
                manifest_items.append(
                    f'    <item id="{ch_id}" href="chapter_{ch_id}.xhtml" media-type="application/xhtml+xml"/>'
                )
                chapter_items.append(ch_id)

            manifest = "\n".join(manifest_items)
            spine_items = [f'<itemref idref="{nav_id}"/>']
            spine_items += [f'<itemref idref="{ch}"/>' for ch in chapter_items]
            spine = "\n".join(spine_items)

            content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookId">urn:uuid:{uuid_str}</dc:identifier>
    <dc:title>{self._escape_xml(title)}</dc:title>
    <dc:creator>{self._escape_xml(author)}</dc:creator>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">{modified}</meta>
  </metadata>
  <manifest>
{manifest}
  </manifest>
  <spine>
{spine}
  </spine>
</package>"""
            zf.writestr("OEBPS/content.opf", content_opf)

            # 4. OEBPS/nav.xhtml (Navigation Document)
            nav_items = []
            nav_items.append('    <li><a href="chapter_ch1.xhtml">Chapter 1</a></li>')
            for ch in chapters[1:]:
                nav_items.append(
                    f'    <li><a href="chapter_ch{chapters.index(ch) + 1}.xhtml">Chapter {chapters.index(ch) + 1}: {self._escape_xml(ch.get("title", "Untitled"))}</a></li>'
                )

            nav_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{self._escape_xml(title)}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
{chr(10).join(nav_items)}
    </ol>
  </nav>
</body>
</html>"""
            zf.writestr("OEBPS/nav.xhtml", nav_xhtml)

            # 5. CSS
            css = """body { font-family: Georgia, serif; margin: 5%; line-height: 1.6; }
h1 { text-align: center; margin-bottom: 2em; }
h2 { border-bottom: 1px solid #ccc; padding-bottom: 0.5em; margin-top: 1.5em; }
.chapter { margin-bottom: 2em; }
p { text-indent: 1.5em; margin: 0.5em 0; }
p.first { text-indent: 0; }
.character { background: #f5f5f5; padding: 1em; margin: 1em 0; }
"""
            zf.writestr("OEBPS/styles.css", css)

            # 6. Chapters
            for i, ch in enumerate(sorted(chapters, key=lambda x: x["number"])):
                content = ch.get("content", "")
                paragraphs = content.split("\n\n")
                para_html = "\n".join(
                    [
                        f'<p class="{"first" if j == 0 else ""}">{self._escape_xml(p)}</p>'
                        for j, p in enumerate(paragraphs)
                        if p.strip()
                    ]
                )

                ch_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{self._escape_xml(ch.get("title", f"Chapter {ch['number']}"))}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <div class="chapter">
    <h2>{self._escape_xml(ch.get("title", f"Chapter {ch['number']}"))}</h2>
{para_html}
  </div>
</body>
</html>"""
                zf.writestr(f"OEBPS/chapter_ch{i + 1}.xhtml", ch_xhtml)

        return epub_bytes.getvalue()

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def to_pdf_html(self) -> str:
        """Generate HTML optimized for PDF conversion"""
        chapters = self.db.get_chapters()
        entities = self.db.get_entities()

        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Manuscript</title>
  <style>
    @page { size: 8.5in 11in; margin: 1in 1in 1in 1in; }
    body { font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 24pt; margin: 0; padding: 0; }
    h1 { text-align: center; font-size: 14pt; margin: 24pt 0 12pt 0; page-break-after: avoid; }
    h2 { font-size: 12pt; margin: 18pt 0 6pt 0; page-break-after: avoid; }
    p { text-indent: 0.5in; margin: 0; text-align: justify; }
    p.first { text-indent: 0; margin-bottom: 12pt; }
    .characters { page-break-before: always; }
    .character { margin-bottom: 12pt; }
    @media print { body { print-color-adjust: exact; } }
  </style>
</head>
<body>
  <h1>MANUSCRIPT</h1>
  <p class="first" style="text-align: center; font-style: italic;">A Novel</p>

  <div class="characters">
    <h1>CHARACTERS</h1>"""

        for e in entities:
            if e.get("type") == "character":
                html += f"""
    <div class="character">
      <strong>{e["name"]}</strong><br/>
      {e.get("description", "")}
    </div>"""

        html += "\n  </div>\n"

        for ch in sorted(chapters, key=lambda x: x["number"]):
            content = ch.get("content", "")
            paragraphs = content.split("\n\n")
            html += f"""
  <h2>{ch.get("title", f"Chapter {ch['number']}")}</h2>"""
            for i, para in enumerate(paragraphs):
                if para.strip():
                    html += f'\n  <p class="{"first" if i == 0 else ""}">{para}</p>'

        html += """
</body>
</html>"""
        return html

    def to_docx(self) -> bytes:
        """Export story as DOCX (simplified RTF that Word can open)"""
        chapters = self.db.get_chapters()
        entities = self.db.get_entities()

        # Build RTF content
        rtf = r"{\rtf1\ansi\deff0"
        rtf += r"{\fonttbl{\f0 Times New Roman;}}"
        rtf += r"{\colortbl\red0\green0\blue0;}"
        rtf += r"\fs24"

        # Title
        rtf += r"{\b\fs36 My Novel\par}"
        rtf += r"\par "

        # Characters
        rtf += r"{\b\fs28 Characters\par}"
        for e in entities:
            if e.get("type") == "character":
                rtf += f"{{\\b {e['name']}}} "
                rtf += rf"{e.get('description', '')}\par "

        rtf += r"\par "

        # Chapters
        rtf += r"{\b\fs28 Chapters\par}"
        for ch in sorted(chapters, key=lambda x: x["number"]):
            rtf += r"{\b\fs32 Chapter }"
            rtf += f"{{\\b {ch['number']}}}: "
            rtf += f"{{\\b {ch.get('title', 'Untitled')}}}\\par "
            content = ch.get("content", "")
            # Preserve line breaks
            for para in content.split("\n"):
                if para.strip():
                    rtf += f"{para}\\par "
            rtf += r"\par "

        rtf += "}"
        return rtf.encode("utf-8")

    def to_plain_text(self) -> str:
        """Export as plain text (no formatting)"""
        chapters = self.db.get_chapters()
        entities = self.db.get_entities()

        text = "MY NOVEL\n\n"
        text += "=" * 40 + "\n\n"

        # Characters
        text += "CHARACTERS\n"
        text += "-" * 20 + "\n"
        for e in entities:
            if e.get("type") == "character":
                text += f"\n{e['name']}\n"
                text += f"  {e.get('description', '')}\n"
                attrs = self.db.get_attributes(e["id"])
                if attrs:
                    text += "  " + ", ".join([f"{a['key']}: {a['value']}" for a in attrs]) + "\n"

        text += "\n\n"

        # Chapters
        text += "CHAPTERS\n"
        text += "-" * 20 + "\n"
        for ch in sorted(chapters, key=lambda x: x["number"]):
            text += f"\nChapter {ch['number']}: {ch.get('title', 'Untitled')}\n"
            text += "=" * 30 + "\n"
            text += ch.get("content", "") + "\n"

        return text

    def to_epub_bytes(self, title: str = "My Novel", author: str = "Author") -> bytes:
        """Export as EPUB bytes"""
        return self.to_epub(title, author)[0]

    def save(self, format: str, filepath: str):
        """Save to file"""
        if format == "markdown":
            content = self.to_markdown()
        elif format == "html":
            content = self.to_html()
        elif format == "json":
            content = json.dumps(self.to_json(), indent=2)
        elif format == "txt":
            content = self.to_plain_text()
        elif format == "docx":
            content = self.to_docx()
        elif format == "epub":
            content = self.to_epub_bytes()
        elif format == "pdf":
            content = self.to_pdf_html()
        else:
            raise ValueError(f"Unknown format: {format}")

        if isinstance(content, bytes):
            Path(filepath).write_bytes(content)
        else:
            Path(filepath).write_text(content, encoding="utf-8")
        return filepath


if __name__ == "__main__":
    db = CodexDatabase()
    exporter = StoryExporter(db)

    print("Exported to Markdown:", exporter.save("markdown", "story.md"))
    print("Exported to HTML:", exporter.save("html", "story.html"))
    print("Exported to JSON:", exporter.save("json", "story.json"))
