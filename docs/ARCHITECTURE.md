# Architecture Guide

## Overview

Nebula-Writer is a FastAPI-based fiction writing assistant with SQLite persistence, AI integration, and RAG-based memory.

```
nebula-writer/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── codex.py        # SQLite database layer
│   ├── ai_writer.py    # AI writing assistant
│   ├── ai_client.py    # Multi-provider AI client
│   ├── memory.py       # ChromaDB RAG system
│   ├── exporter.py     # Export formats
│   ├── config.py      # Configuration
│   └── prompts.py   # Prompt templates
├── frontend/
│   └── index.html    # Vue.js SPA
├── data/              # SQLite database
└── docs/             # Documentation
```

## Backend Components

### CodexDatabase (`codex.py`)

Core data layer using SQLite:

```python
db = CodexDatabase("data/codex.db")

# Entity operations
db.add_entity("Ravi", "character", "Protagonist detective")
db.get_entities("character")
db.add_relationship(from_id, to_id, "loves", 0.9)

# Chapter operations
db.add_chapter(1, "The Beginning", "Content here...")
db.update_chapter(chapter_id, content="Updated...")

# Version history
db.save_version(chapter_id, content)
db.get_versions(chapter_id)

# Consistency
db.run_consistency_check()
```

### AIWriter (`ai_writer.py`)

Gemini-powered writing with Codex context:

```python
from ai_writer import AIWriter
ai = AIWriter()

# Write scene with context
result = ai.write_scene(
    db=db,
    beat="The detective finds a clue",
    word_count=500,
    entity_ids=[1, 2]
)
```

### AIClient (`ai_client.py`)

Multi-provider AI interface:

```python
from ai_client import AIClient

# Use any provider
client = AIClient(provider="gemini", api_key=key)
result = client.generate(prompt, system_prompt)
```

### MemorySystem (`memory.py`)

ChromaDB vector store for semantic search:

```python
from memory import MemorySystem
mem = MemorySystem()

# Index and search
mem.index_chapter(chapter_id, summary, content)
results = mem.search_chapters("mystery clue")
```

## Database Schema

### Entities
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('character', 'location', 'item')),
    description TEXT,
    is_alive INTEGER,
    current_location TEXT,
    image_url TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Relationships
```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    from_entity_id INTEGER REFERENCES entities(id),
    to_entity_id INTEGER REFERENCES entities(id),
    relationship_type TEXT,
    strength REAL DEFAULT 0.5,
    description TEXT
);
```

### Chapters
```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    number INTEGER UNIQUE,
    title TEXT,
    content TEXT,
    summary TEXT,
    word_count INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Version History
```sql
CREATE TABLE chapter_versions (
    id INTEGER PRIMARY KEY,
    chapter_id INTEGER REFERENCES chapters(id),
    content TEXT,
    word_count INTEGER,
    created_at TIMESTAMP
);
```

### Character Knowledge
```sql
CREATE TABLE character_knowledge (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    chapter_id INTEGER REFERENCES chapters(id),
    knowledge TEXT,
    created_at TIMESTAMP
);
```

## API Design

FastAPI with Pydantic models:

```python
class EntityCreate(BaseModel):
    name: str
    entity_type: str
    description: Optional[str] = None
    current_location: Optional[str] = None
    is_alive: bool = True
    image_url: Optional[str] = None
```

### Response Patterns

```python
# Success
{"id": 1, "message": "Entity created"}

# Error
raise HTTPException(status_code=404, detail="Not found")

# List
return db.get_entities()

# Detail
chapter = db.get_chapter(chapter_id)
chapter['scenes'] = db.get_scenes(chapter_id)
return chapter
```

## Frontend

Vue 3 SPA with TailwindCSS:

```javascript
const { createApp } = Vue;
createApp({
    data() {
        return {
            currentView: 'dashboard',
            entities: [],
            chapters: [],
            stats: {}
        }
    },
    async mounted() {
        await this.loadData();
    },
    methods: {
        async loadData() {
            const res = await fetch('/api/entities');
            this.entities = await res.json();
        }
    }
}).mount('#app');
```

## Data Flow

```
User Input -> Vue.js -> Fetch API -> FastAPI -> CodexDatabase -> SQLite
                <- JSON Response <------- Response <----------
```

## AI Flow

```
User Prompt -> AI Client -> Gemini/OpenAI/Claude API
                    <- AI Response
```

## RAG Flow

```
Chapter Content -> ChromaDB Index
Query -> Vector Search -> Relevant Chunks -> AI Context
```