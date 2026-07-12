"""
Nebula-Writer Interactive REPL
Interactive writing session
"""

from pathlib import Path

from nebula_writer.supabase_db import SupabaseDB as CodexDatabase


def print_banner():
    print("""
╔═══════════════════════════════════════════╗
║     NEBULA-WRITER Interactive Session     ║
║     AI-Powered Fiction Writing            ║
╚═══════════════════════════════════════════╝
""")


def cmd_entities(db):
    entities = db.get_entities()
    print(f"\nEntities ({len(entities)}):")
    for e in entities:
        print(f"  [{e['id']}] {e['name']} ({e['entity_type']})")


def cmd_chapters(db):
    chapters = db.get_chapters()
    print(f"\nChapters ({len(chapters)}):")
    for c in chapters:
        print(f"  Ch {c['number']}: {c['title']} [{c.get('word_count', '?')} words]")


def cmd_write(db):
    chapters = db.get_chapters()
    if not chapters:
        print("No chapters yet. Create one first.")
        return
    ch = chapters[-1]
    print(f"Current chapter: Ch {ch['number']}: {ch['title']}")
    print("(Writing functionality requires AIWriter setup)")


def cmd_stats(db):
    stats = db.get_stats()
    print("\nStory Statistics:")
    for k, v in stats.items():
        print(f"  {k}: {v}")


def print_help():
    print("""
Commands:
  entities           List all entities
  chapters           List all chapters
  write              Continue writing
  stats              Show statistics
  help               Show this help
  exit               Exit REPL
""")


def main():
    print_banner()

    db = CodexDatabase()

    print("Type 'help' for commands.\n")

    while True:
        try:
            cmd = input("nebula> ").strip().lower()

            if not cmd:
                continue
            elif cmd == "exit" or cmd == "quit":
                print("Goodbye!")
                break
            elif cmd == "entities":
                cmd_entities(db)
            elif cmd == "chapters":
                cmd_chapters(db)
            elif cmd == "write":
                cmd_write(db)
            elif cmd == "stats":
                cmd_stats(db)
            elif cmd == "help":
                print_help()
            else:
                print(f"Unknown command: {cmd}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
