# Nebula-Writer - Technical Specification

## Project Overview
- **Name**: Nebula-Writer
- **Type**: AI-Powered Fiction Writing Assistant with RAG
- **Core Functionality**: A "System of Record" for fiction that stores entities, relationships, and events in a database, then feeds an LLM the exact context it needs to never hallucinate.
- **Target Users**: Fiction writers, novelists, game writers who need long-term memory for their stories

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite (Codex), ChromaDB (Vector Memory)
- **LLM**: Google Gemini API (configurable)
- **Frontend**: Vue.js 3 + TailwindCSS (single-page app)

### Data Models

#### 1. Entities Table
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('character', 'location', 'item')),
    description TEXT,
    is_alive BOOLEAN DEFAULT 1,
    current_location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Attributes Table
```sql
CREATE TABLE attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    effective_from TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);
```

#### 3. Relationships Table
```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_entity_id INTEGER NOT NULL,
    to_entity_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 0.5,
    FOREIGN KEY (from_entity_id) REFERENCES entities(id),
    FOREIGN KEY (to_entity_id) REFERENCES entities(id)
);
```

#### 4. Events Table
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    chapter INTEGER,
    scene TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. Chapters Table
```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER NOT NULL UNIQUE,
    title TEXT,
    content TEXT,
    summary TEXT,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. Scenes Table
```sql
CREATE TABLE scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    beat TEXT,
    content TEXT,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);
```

## Core Features

### Phase 1: Codex (Database Layer)
- CRUD operations for all entities
- Attribute versioning (temporal tracking)
- Relationship graph with strength scores
- Event logging for plot points

### Phase 2: Memory System (RAG)
- ChromaDB integration for semantic search
- Chapter summarization
- Context retrieval before writing

### Phase 3: Agentic Workflow
- Context Retrieval → Strategic Planning → Prose Execution
- Chain-of-thought hidden steps
- Beat-based writing

### Phase 4: CLI Commands
- `nebula-writer entity add --name "Ravi" --type character --desc "Protagonist"`
- `nebula-writer write --beat "They fight in the rain" --words 500`
- `nebula-writer audit --check contradictions`
- `nebula-writer visualize --format mermaid`

### Phase 5: Web UI
- Dashboard with entity overview
- Entity management (CRUD)
- Story timeline view
- Writing interface with beat tracking
- Relationship visualizer

## UI/UX Specification

### Color Palette
- **Background**: `#0a0a0f` (deep space black)
- **Surface**: `#12121a` (card background)
- **Surface Elevated**: `#1a1a24` (hover states)
- **Primary**: `#8b5cf6` (violet)
- **Primary Light**: `#a78bfa`
- **Accent**: `#06b6d4` (cyan)
- **Text Primary**: `#f1f5f9`
- **Text Secondary**: `#94a3b8`
- **Success**: `#10b981`
- **Warning**: `#f59e0b`
- **Error**: `#ef4444`

### Typography
- **Font Family**: "JetBrains Mono" for code, "Outfit" for UI
- **Headings**: Outfit, 600 weight
- **Body**: Outfit, 400 weight

### Layout
- Sidebar navigation (240px)
- Main content area with max-width 1400px
- Responsive: collapses to hamburger on mobile

### Components
- Entity cards with type badges
- Relationship graph (D3.js or similar)
- Chapter timeline
- Beat editor
- Command palette (Cmd+K)

## Acceptance Criteria
1. ✅ SQLite database created with all tables
2. ✅ CRUD APIs for entities, relationships, events
3. ✅ ChromaDB integration for chapter memory
4. ✅ FastAPI server runs on port 8000
5. ✅ Web UI loads and connects to API
6. ✅ Entity creation from UI works
7. ✅ Chapter writing with beat tracking
8. ✅ Relationship visualization
