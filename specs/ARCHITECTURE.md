# Architecture Document: Nebula-Writer

## 1. System Overview

Nebula-Writer is a full-stack application with a FastAPI backend, Vue.js frontend, SQLite database, and ChromaDB for semantic search. It uses RAG architecture to provide AI-powered writing assistance.

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue.js)                      │
│              http://localhost:8000                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│  │ Codex       │ │ AI Writer   │ │ Memory (RAG)        │  │
│  │ (SQLite)    │ │ (Gemini)    │ │ (ChromaDB)          │  │
│  └─────────────┘ └─────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Components

### Backend (FastAPI)
- **codex.py:** SQLite database for entities
- **ai_writer.py:** Gemini AI integration
- **memory.py:** ChromaDB RAG implementation
- **audit.py:** Story consistency checking

### Frontend (Vue.js)
- Entity management UI
- Chapter editor
- Visualization (Mermaid.js)

## 4. File Structure

```
Nebula-Writer/
├── backend/          # FastAPI server
│   ├── codex.py     # SQLite
│   ├── ai_writer.py # Gemini
│   └── memory.py    # ChromaDB
├── frontend/         # Vue.js UI
├── repl.py          # Interactive REPL
├── specs/           # Documentation
└── README.md
```

---

*Document Version: 1.0*  
*Created: 2026-03-17*
