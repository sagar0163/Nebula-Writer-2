# Business Requirements Document (BRD): Nebula-Writer

## 1. Project Overview

**Project Name:** Nebula-Writer  
**Type:** AI-Powered Fiction Writing Assistant  
**Core Functionality:** A "System of Record" for fiction writing that stores every character, location, and plot point using SQLite, with RAG (Retrieval-Augmented Generation) powered by ChromaDB and Gemini AI for context-aware writing assistance.

**Target Users:** Fiction writers, novelists, and creative writers who want AI assistance while maintaining consistency in their stories.

---

## 2. Features

- **The Codex:** SQLite database for Characters, Locations, Items, Relationships
- **Chapter Management:** Write and organize story chapters
- **AI Writing:** Gemini-powered scene generation with context
- **Semantic Search:** ChromaDB-powered RAG memory
- **Story Audit:** Detect contradictions in your story
- **Visualization:** Mermaid.js relationship graphs
- **Web UI:** Beautiful Vue.js interface
- **CLI & REPL:** Command-line and interactive writing
- **Export:** Markdown, HTML, JSON formats
- **Docker:** Easy containerized deployment

---

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Python 3.11+ |
| **Database** | SQLite |
| **AI** | Google Gemini API |
| **Memory** | ChromaDB (RAG) |
| **Frontend** | Vue.js 3, TailwindCSS |
| **DevOps** | Docker |

---

## 4. User Stories

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US1 | As a writer, I want to manage characters | CRUD operations for characters work |
| US2 | As a writer, I want AI to generate scenes | Gemini generates context-aware scenes |
| US3 | As a writer, I want semantic search | ChromaDB provides relevant context |

---

## 5. Requirements

- FR1: SQLite database for entity storage
- FR2: Chapter management
- FR3: Gemini AI integration
- FR4: ChromaDB semantic search
- FR5: Story audit functionality
- FR6: Web UI and CLI interfaces

---

## 6. Future Enhancements

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| FE1 | More AI models | Medium |
| FE2 | Collaboration features | Medium |
| FE3 | Mobile app | Low |

---

*Document Version: 1.0*  
*Created: 2026-03-17*
