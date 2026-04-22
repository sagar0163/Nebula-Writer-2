# Nebula-Writer Documentation

## Quick Start

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` in your browser.

---

## API Endpoints

### Entities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/entities` | Get all entities |
| GET | `/api/entities/{id}` | Get entity by ID |
| POST | `/api/entities` | Create entity |
| PUT | `/api/entities/{id}` | Update entity |
| DELETE | `/api/entities/{id}` | Delete entity |

### Chapters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chapters` | Get all chapters |
| GET | `/api/chapters/{id}` | Get chapter with scenes |
| POST | `/api/chapters` | Create chapter |
| PUT | `/api/chapters/{id}` | Update chapter |
| DELETE | `/api/chapters/{id}` | Delete chapter |
| GET | `/api/chapters/{id}/versions` | Get version history |

### Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | Get all story templates |
| GET | `/api/templates/{id}` | Get specific template |

### Consistency
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/consistency` | Get all issues |
| POST | `/api/consistency/check` | Run consistency check |
| POST | `/api/consistency/{id}/resolve` | Resolve issue |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/mermaid` | Mermaid graph |
| GET | `/api/export/markdown` | Markdown format |
| GET | `/api/export/html` | HTML format |
| GET | `/api/export/text` | Plain text |
| GET | `/api/export/json` | Full JSON export |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/providers` | Available providers |
| POST | `/api/ai/client` | Generate with AI |
| POST | `/api/ai/write` | Write scene |
| POST | `/api/ai/rewrite` | Rewrite in style |
| POST | `/api/extract` | Extract entities |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Statistics |
| GET | `/api/search?q=` | Search |
| GET | `/api/relationships` | Get relationships |
| GET | `/api/events` | Get events |

---

## Environment Variables

```bash
export GEMINI_API_KEY=your_key          # For AI features
export OPENAI_API_KEY=your_key          # OpenAI support
export ANTHROPIC_API_KEY=your_key     # Claude support
```

---

## Story Templates

Available templates:
- **Three-Act Structure** - Classic setup/confrontation/resolution
- **Hero's Journey** - Departure/Initiation/Return
- **Save the Cat** - Blake Snyder's beat system
- **Seven-Point Plot** - Hook/Pinch/Resolution structure
- **Snowflake Method** - Expand from sentence to novel

---

## Database Schema

### Tables
- `entities` - Characters, locations, items
- `attributes` - Entity properties
- `relationships` - Entity connections
- `chapters` - Story chapters
- `scenes` - Chapter scenes
- `events` - Plot points
- `chapter_versions` - Version history
- `character_knowledge` - What characters know
- `story_templates` - Structure templates
- `consistency_issues` - Consistency problems

---

## Export Formats

### Markdown
```bash
curl http://localhost:8000/api/export/markdown
```

### HTML (for web publishing)
```bash
curl http://localhost:8000/api/export/html
```

### Plain Text
```bash
curl http://localhost:8000/api/export/text
```

### Mermaid Diagram
```bash
curl http://localhost:8000/api/export/mermaid
```

---

## Multi-AI Support

Nebula-Writer supports multiple AI providers:

1. **Google Gemini** (default) - Set `GEMINI_API_KEY`
2. **OpenAI GPT-4** - Set `OPENAI_API_KEY`
3. **Anthropic Claude** - Set `ANTHROPIC_API_KEY`

Example API call:
```bash
curl -X POST http://localhost:8000/api/ai/client \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "prompt": "Write a scene opener"}'
```