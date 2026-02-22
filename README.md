# Nebula-Writer

An AI-powered fiction writing assistant with persistent memory. The "System of Record" for fiction that stores every character, location, and plot point so your AI never forgets.

## Features

- **The Codex** - SQLite database storing Characters, Locations, Items, Relationships, Events
- **Chapter Management** - Write and organize your story into chapters
- **Timeline** - Track plot events with significance levels
- **Relationship Graph** - Visualize connections between entities
- **Mermaid.js Export** - Generate relationship diagrams
- **REST API** - Full CRUD operations
- **Beautiful Web UI** - Vue.js + TailwindCSS interface

## Quick Start

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API will run on `http://localhost:8000`

### 2. Open the UI

Open `frontend/index.html` in your browser (or serve it):

```bash
# Using Python
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/entities` | List all entities |
| POST | `/api/entities` | Create entity |
| GET | `/api/entities/{id}` | Get entity details |
| PUT | `/api/entities/{id}` | Update entity |
| DELETE | `/api/entities/{id}` | Delete entity |
| GET | `/api/relationships` | List relationships |
| POST | `/api/relationships` | Create relationship |
| GET | `/api/chapters` | List chapters |
| POST | `/api/chapters` | Create chapter |
| PUT | `/api/chapters/{id}` | Update chapter |
| GET | `/api/events` | List events |
| POST | `/api/events` | Log event |
| GET | `/api/stats` | Get statistics |
| GET | `/api/search?q=query` | Search Codex |
| GET | `/api/export/mermaid` | Get Mermaid diagram |

## Architecture

```
nebula-writer/
├── backend/
│   ├── codex.py      # SQLite database manager
│   ├── main.py       # FastAPI server
│   └── requirements.txt
├── frontend/
│   └── index.html    # Vue.js UI
├── data/
│   └── codex.db      # SQLite database
├── SPEC.md           # Technical specification
└── README.md
```

## Tech Stack

- **Backend**: FastAPI, Python, SQLite
- **Frontend**: Vue.js 3, TailwindCSS
- **Database**: SQLite with custom schema

## License

MIT
