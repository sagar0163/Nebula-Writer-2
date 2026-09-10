# Architecture Document: Nebula-Writer

## 1. System Overview

Nebula-Writer is a backend-first application with a FastAPI API server, a command-line interface (CLI), SQLite database, and ChromaDB for semantic search. It uses RAG architecture to provide AI-powered writing assistance. There is no separate frontend application; interaction happens through the REST API, the CLI, or the REPL.

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Client (API / CLI / REPL)                    │
│              http://localhost:8000                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │ Codex       │ │ AI Writer   │ │ Memory (RAG)        │  │
│  │ (SQLite)    │ │ (Multi-prov)│ │ (ChromaDB)          │  │
│  └─────────────┘ └─────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Components

### Backend (FastAPI)
- **nebula_writer/main.py:** FastAPI application and API server entry point
- **nebula_writer/codex.py:** SQLite database for entities, chapters, and events
- **nebula_writer/ai_writer.py:** Multi-provider AI writing integration
- **nebula_writer/memory.py:** ChromaDB RAG implementation
- **nebula_writer/audit.py:** Story consistency checking
- **nebula_writer/exporter.py:** Story export (Markdown, HTML, PDF, EPUB, DOCX)

### CLI
- **nebula-writer:** Command-line interface for entity/chapter management and relationship visualization

### REPL
- **repl.py:** Interactive Python REPL for story management

## 4. File Structure

```
Nebula-Writer/
├── nebula_writer/    # FastAPI server + all subsystems
│   ├── main.py      # API entry point
│   ├── codex.py     # SQLite
│   ├── ai_writer.py # Multi-model AI
│   └── memory.py    # ChromaDB
├── nebula-writer    # CLI entry point
├── repl.py          # Interactive REPL
├── specs/           # Documentation
└── README.md
```

---

*Document Version: 1.0*  
*Created: 2026-03-17*