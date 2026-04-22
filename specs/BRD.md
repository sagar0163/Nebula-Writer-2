# Business Requirements Document (BRD): Nebula-Writer v2.0

## 1. Project Overview

**Project Name:** Nebula-Writer  
**Type:** AI-Powered Fiction Writing Assistant  
**Version:** 2.0.0
**Core Functionality:** A "System of Record" for fiction writing that stores every character, location, and plot point using SQLite, with RAG (Retrieval-Augmented Generation) powered by ChromaDB and multi-model AI (Gemini, OpenAI, Claude) for context-aware writing assistance.

**Target Users:** Fiction writers, novelists, and creative writers who want AI assistance while maintaining consistency in their stories.

---

## 2. Core Features

### 2.1 Entity Management
- **The Codex:** SQLite database for Characters, Locations, Items
- **Attributes:** Custom key-value attributes per entity
- **Relationships:** Directed graph connections with strength ratings
- **Character Knowledge:** Track what each character knows at each chapter

### 2.2 Chapter Management
- **Chapters:** Write and organize story chapters with word count tracking
- **Scenes:** Split chapters into scenes with beat markers
- **Version History:** Full version history with rollback capability
- **Rich Text Editor:** Built-in text editor in Vue.js frontend

### 2.3 Story Templates
- **Three-Act Structure:** Classic setup/confrontation/resolution
- **Hero's Journey:** Departure/Initiation/Return model
- **Save the Cat:** Blake Snyder's beat system
- **Seven-Point Plot:** Hook/Pinch/Resolution structure
- **Snowflake Method:** Expand from one-sentence summary

### 2.4 AI Writing
- **Multi-Model Support:** Gemini, OpenAI GPT-4, Anthropic Claude
- **Context-Aware:** AI uses Codex (entities, relationships, events) for accurate writing
- **Style Rewriting:** Noir, romantic, horror, humor, thriller styles
- **Show Not Tell:** Convert telling to showing prose
- **Scene Generation:** Write scenes from beats with word count targets

### 2.5 Semantic Search
- **ChromaDB RAG:** Vector-based semantic search
- **Memory Index:** Index chapters and entities for retrieval
- **Context Retrieval:** Get relevant story context for writing

### 2.6 Story Audit
- **Consistency Checking:** Detect timeline and entity contradictions
- **Auto-Extract:** Extract entities from prose text
- **Issue Tracking:** Track and resolve consistency issues

### 2.7 Export Formats
- **Markdown:** Export story as .md file
- **HTML:** Export as web-ready HTML
- **Plain Text:** Export as .txt file
- **DOCX:** RTF format compatible with Word
- **Mermaid Diagrams:** Visual relationship graphs
- **JSON:** Full Codex export

### 2.8 User Interface
- **Vue.js SPA:** Single-page application
- **TailwindCSS:** Dark space-themed UI
- **Responsive:** Works on desktop browsers
- **Multiple Views:** Dashboard, Entities, Chapters, Templates, Consistency, AI, Export

### 2.9 Developer Features
- **FastAPI Backend:** RESTful API
- **Docker Support:** Containerized deployment
- **CLI & REPL:** Command-line interface
- **Full Documentation:** API, Architecture, Features guides

---

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Python 3.10+ |
| **Database** | SQLite |
| **AI Models** | Google Gemini, OpenAI GPT-4, Anthropic Claude |
| **Memory** | ChromaDB (RAG) |
| **Frontend** | Vue.js 3, TailwindCSS |
| **DevOps** | Docker |

---

## 4. User Stories

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US1 | As a writer, I want to manage characters, locations, and items | CRUD operations work for all entity types |
| US2 | As a writer, I want to track character relationships | Directed relationships with strength ratings |
| US3 | As a writer, I want AI to generate scenes | Multi-model AI generates context-aware scenes |
| US4 | As a writer, I want semantic search | ChromaDB provides relevant context |
| US5 | As a writer, I want to use story templates | Multiple structure templates available |
| US6 | As a writer, I want version history | Can save and restore chapter versions |
| US7 | As a writer, I want consistency checking | Detects and tracks issues |
| US8 | As a writer, I want to export my work | Multiple format export options |
| US9 | As a writer, I want character knowledge tracking | Track what each character knows at each chapter |
| US10 | As a writer, I want auto-extract entities | Extracts entities from prose text |

---

## 5. Functional Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| FR1 | SQLite database for entity storage | ✅ Implemented |
| FR2 | Chapter management with versioning | ✅ Implemented |
| FR3 | Multi-model AI integration (Gemini, OpenAI, Claude) | ✅ Implemented |
| FR4 | ChromaDB semantic search | ✅ Implemented |
| FR5 | Story audit and consistency checking | ✅ Implemented |
| FR6 | Web UI (Vue.js) and API interfaces | ✅ Implemented |
| FR7 | Version history for chapters | ✅ Implemented |
| FR8 | Character knowledge tracking | ✅ Implemented |
| FR9 | Story structure templates | ✅ Implemented |
| FR10 | Multi-format export (MD, HTML, TXT, DOCX) | ✅ Implemented |
| FR11 | Auto-extract entities from prose | ✅ Implemented |
| FR12 | Relationship visualization (Mermaid) | ✅ Implemented |

---

## 6. Database Schema

### 6.1 Core Tables
- `entities` - Characters, locations, items
- `attributes` - Entity properties
- `relationships` - Entity connections
- `chapters` - Story chapters
- `scenes` - Chapter scenes
- `events` - Plot points

### 6.2 New Tables (v2.0)
- `chapter_versions` - Version history
- `character_knowledge` - Character knowledge by chapter
- `story_templates` - Story structure templates
- `consistency_issues` - Consistency problems

---

## 7. API Endpoints

### 7.1 Core Endpoints
- `/api/entities` - CRUD for entities
- `/api/relationships` - Manage relationships
- `/api/chapters` - Chapter management
- `/api/events` - Plot events

### 7.2 New Endpoints (v2.0)
- `/api/templates` - Story templates
- `/api/consistency` - Consistency checking
- `/api/versions` - Version history
- `/api/character-knowledge` - Knowledge tracking
- `/api/extract` - Auto-extract entities
- `/api/ai/client` - Multi-provider AI
- `/api/ai/providers` - Available providers
- `/api/export/markdown` - Markdown export
- `/api/export/html` - HTML export
- `/api/export/text` - Plain text export

---

## 8. Future Enhancements

| Enhancement | Description | Priority | Status |
|-------------|-------------|----------|--------|
| FE1 | More AI models | Medium | ✅ Implemented |
| FE2 | Collaboration features | Medium | Pending |
| FE3 | Mobile app | Low | Pending |
| FE4 | EPUB export | High | Partial |
| FE5 | Real-time auto-save | High | Pending |
| FE6 | Character arc visualization | Medium | Pending |
| FE7 | Beta reader system | Medium | Pending |
| FE8 | Plugin system | Low | Pending |

---

## 9. Competitive Analysis

Nebula-Writer compares to:
- **Novelcrafter** - Codex system (similar concept, cloud-only)
- **Novelium** - Auto-tracks from prose (similar features)
- **Sudowrite** - Story Bible (similar concept)
- **PlotForge** - Structure templates (similar features)

**Differentiation:** Free, self-hosted, multi-AI provider, RAG-powered

---

*Document Version: 2.0*  
*Updated: 2026-04-21*  
*Status: Current*