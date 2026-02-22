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
