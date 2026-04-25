"""
Nebula-Writer Interactive REPL
Interactive writing session
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from ai_writer import AIWriter
from codex import CodexDatabase
from prompts import PROMPTS


def print_banner():
    print("""
╔═══════════════════════════════════════════╗
║     NEBULA-WRITER Interactive Session     ║
║     AI-Powered Fiction Writing            ║
╚═══════════════════════════════════════════╝
""")


def cmd_entities(db):
    """List entities"""
    entities = db.get_entities()
    if not entities:
        print("No entities yet.")
        return

    print("\n📦 ENTITIES:")
    for e in entities:
        print(f"  [{e['type']:10}] {e['name']}")
        if e.get("description"):
            print(f"               {e['description'][:50]}...")


def cmd_chapters(db):
    """List chapters"""
    chapters = db.get_chapters()
    if not chapters:
        print("No chapters yet.")
        return

    print("\n📖 CHAPTERS:")
    for ch in chapters:
        print(f"  Ch.{ch['number']:2} {ch.get('title', 'Untitled'):30} ({ch.get('word_count', 0)} words)")


def cmd_write(db):
    """Write a scene"""
    try:
        ai = AIWriter()
    except ValueError as e:
        print(f"❌ {e}")
        print("Set GEMINI_API_KEY to use AI features.")
        return

    print("\n🎯 Writing a scene...")
    beat = input("  Beat/plot point: ")
    words = input("  Word count (default 500): ")
    word_count = int(words) if words.strip() else 500

    print("\n✨ Writing...")
    result = ai.write_scene(db, beat, word_count)
    print(f"\n{result}\n")


def cmd_rewrite(db):
    """Rewrite in style"""
    try:
        ai = AIWriter()
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("\n🎨 Rewrite in style...")
    print("  Styles: noir, romantic, horror, humor, thriller")
    style = input("  Style: ").strip().lower()
    print("\n  Paste your text (Ctrl+D to finish):")
    text = sys.stdin.read().strip()

    if not text:
        print("No text provided.")
        return

    print(f"\n✨ Rewriting in {style}...")
    result = ai.rewrite_style(text, style)
    print(f"\n{result}\n")


def cmd_prompts():
    """List prompt templates"""
    print("\n📝 PROMPT TEMPLATES:")
    for key, p in PROMPTS.items():
        print(f"  {key:20} - {p['name']}")


def cmd_stats(db):
    """Show stats"""
    stats = db.get_stats()
    print("\n📊 STATISTICS:")
    print(f"  Entities:     {stats.get('total_entities', 0)}")
    print(f"  Characters:   {stats.get('entities_by_type', {}).get('character', 0)}")
    print(f"  Locations:    {stats.get('entities_by_type', {}).get('location', 0)}")
    print(f"  Chapters:     {stats.get('total_chapters', 0)}")
    print(f"  Total Words:  {stats.get('total_words', 0)}")
    print(f"  Events:       {stats.get('total_events', 0)}")


def cmd_help():
    """Show help"""
    print("""
📚 COMMANDS:
  entities         List all entities
  chapters         List all chapters
  write            Write a new scene (AI)
  rewrite          Rewrite text in different style
  prompts          List prompt templates
  stats            Show statistics
  help             Show this help
  exit             Exit REPL
""")


def main():
    print_banner()

    db_path = Path(__file__).parent / "data" / "codex.db"
    db = CodexDatabase(str(db_path))

    print("Type 'help' for commands.\n")

    while True:
        try:
            cmd = input("nebula> ").strip().lower()

            if not cmd:
                continue
            elif cmd == "exit" or cmd == "quit":
                print("👋 Goodbye!")
                break
            elif cmd == "entities":
                cmd_entities(db)
            elif cmd == "chapters":
                cmd_chapters(db)
            elif cmd == "write":
                cmd_write(db)
            elif cmd == "rewrite":
                cmd_rewrite(db)
            elif cmd == "prompts":
                cmd_prompts()
            elif cmd == "stats":
                cmd_stats(db)
            elif cmd == "help":
                cmd_help()
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
