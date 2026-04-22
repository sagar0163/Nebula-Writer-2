# Development Guide

## Setup

```bash
# Clone
git clone https://github.com/sagar0163/Nebula-Writer.git
cd Nebula-Writer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_api_key
export OPENAI_API_KEY=your_api_key

# Run
cd backend
python -m uvicorn main:app --reload --port 8000
```

## Project Structure

```
backend/
├── main.py          # FastAPI app entry point
├── codex.py         # Database layer (600+ lines)
├── ai_writer.py    # AI writing logic
├── ai_client.py    # Multi-provider AI client
├── memory.py       # ChromaDB RAG
├── exporter.py     # Export formats
├── audit.py       # Story auditing
├── config.py     # Configuration
└── prompts.py   # Prompt templates

frontend/
└── index.html   # Vue 3 SPA
```

## Running Tests

```bash
pytest tests/
```

## Adding New Features

### 1. Add Database Table

Edit `codex.py`, add table in `_init_db()`:

```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
""")
```

### 2. Add API Endpoint

Edit `main.py`:

```python
@app.get("/api/new-endpoint")
def new_endpoint():
    """Description"""
    return db.get_new_data()
```

### 3. Add Frontend View

Edit `frontend/index.html`:

```html
<div v-if="currentView === 'new-view'" class="space-y-6">
    <!-- UI content -->
</div>
```

## Database Migrations

Database is auto-created on first run. For migrations:

```python
# In codex.py _init_db()
cursor.execute("""
    ALTER TABLE entities ADD COLUMN new_column TEXT
""")
```

## Code Style

- Python: Follow PEP 8
- JavaScript: Standard ESLint rules
- Use type hints in Python
- Use Pydantic models for API

## Adding AI Provider

Edit `ai_client.py`:

```python
def _init_provider(self):
    """Initialize provider"""
    if self.provider == 'new_provider':
        # Initialize new provider
        pass
```

## Building Docker Image

```bash
docker build -t nebula-writer .
docker run -p 8000:8000 -e GEMINI_API_KEY=key nebula-writer
```

## Performance Tips

1. Use connection pooling for SQLite
2. Index frequently queried columns
3. Cache ChromaDB embeddings
4. Use async for I/O operations

## Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Common Issues

### Import Error
- Run from `backend/` directory
- Check `sys.path` includes correct paths

### CORS Error
- Already configured in `main.py`
- Check `allow_origins=["*"]`

### Unicode Error
- Use ASCII characters in print statements on Windows
- Example: `[OK]` instead of `[OK]`