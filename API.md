# Nebula-Writer API Documentation

## Base URL
```
http://localhost:8000/api
```

## Endpoints Overview

### Entities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entities` | List all entities |
| POST | `/entities` | Create entity |
| GET | `/entities/{id}` | Get entity details |
| PUT | `/entities/{id}` | Update entity |
| DELETE | `/entities/{id}` | Delete entity |

### Attributes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entities/{id}/attributes` | Get entity attributes |
| POST | `/attributes` | Add attribute |
| DELETE | `/attributes/{id}` | Delete attribute |

### Relationships
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/relationships` | List relationships |
| POST | `/relationships` | Create relationship |
| DELETE | `/relationships/{id}` | Delete relationship |

### Chapters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chapters` | List chapters |
| POST | `/chapters` | Create chapter |
| GET | `/chapters/{id}` | Get chapter |
| PUT | `/chapters/{id}` | Update chapter |
| DELETE | `/chapters/{id}` | Delete chapter |

### Events
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/events` | List events |
| POST | `/events` | Log event |

### AI Writing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/write` | Write scene |
| POST | `/ai/rewrite` | Rewrite in style |
| POST | `/ai/describe` | Generate description |
| POST | `/ai/show-not-tell` | Convert telling→showing |

### Tools
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit` | Run story audit |
| POST | `/memory/rebuild` | Rebuild vector index |
| GET | `/memory/search` | Semantic search |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/export/mermaid` | Mermaid diagram |
| GET | `/export/json` | Full JSON export |
| GET | `/export/markdown` | Export story as Markdown |
| GET | `/export/html` | Export story as HTML |
| GET | `/export/text` | Export story as Plain Text |
| GET | `/export/epub` | Export story as EPUB 3.0 (base64) |
| GET | `/export/docx` | Export story as Manuscript DOCX (base64) |
| GET | `/export/pdf` | Export story as Print-Ready PDF (base64) |

### Real-time & Synchronization
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/ws/sync/{project_id}` | Real-time WebSocket live collaboration & event broadcasting |
| GET | `/api/lookahead/stream` | SSE stream for real-time lookahead forecasting cards |
| GET | `/api/chapters/{id}/stream` | SSE stream for real-time chapter prose generation |

### Research Engine
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/research/search` | Search the web for research using Brave Search API |
| POST | `/research/store` | Store a research result as a persistent research node |
| GET | `/research/nodes` | List stored research nodes |

### Inline Comments & Targeted Revision
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/comments` | List inline comments by context/target |
| POST | `/comments` | Create inline comment with character-offset anchoring |
| POST | `/comments/{id}/ai-respond` | AI responds to a specific comment |
| POST | `/comments/{id}/resolve` | Resolve comment & trigger post-revision ripple check |
| POST | `/comments/{id}/pushback` | Push back on AI response |

## Example Usage

### Create Entity
```bash
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ravi",
    "entity_type": "character",
    "description": "Protagonist detective"
  }'
```

### Write Scene
```bash
curl -X POST http://localhost:8000/api/ai/write \
  -H "Content-Type: application/json" \
  -d '{
    "beat": "Ravi discovers the hidden key",
    "word_count": 500
  }'
```

### Search Memory
```bash
curl "http://localhost:8000/api/memory/search?q=blue+key+chapter+2"
```
