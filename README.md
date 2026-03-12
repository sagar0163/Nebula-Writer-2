# Nebula-Writer

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
</p>

> AI-Powered Fiction Writing Assistant with Persistent Memory

Nebula-Writer is a "System of Record" for fiction that stores every character, location, and plot point so your AI never forgets. It uses RAG (Retrieval-Augmented Generation) to provide accurate context to AI writing.

## Features

- 📦 **The Codex** - SQLite database for Characters, Locations, Items, Relationships
- 📖 **Chapter Management** - Write and organize story chapters
- 🤖 **AI Writing** - Gemini-powered scene generation with context
- 🔍 **Semantic Search** - ChromaDB-powered RAG memory
- ✅ **Story Audit** - Detect contradictions in your story
- 📊 **Visualization** - Mermaid.js relationship graphs
- 🌐 **Web UI** - Beautiful Vue.js interface
- 📝 **CLI & REPL** - Command-line and interactive writing
- 📤 **Export** - Markdown, HTML, JSON formats
- 🐳 **Docker** - Easy containerized deployment

## Quick Start

```bash
# Clone and install
git clone https://github.com/sagar0163/Nebula-Writer.git
cd Nebula-Writer
pip install -r requirements.txt

# Run the server
make run

# Or use Docker
make docker-build
make docker-run
```

Set your Gemini API key:
```bash
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### Web UI
Open `http://localhost:8000` in your browser.

### CLI
```bash
# Add entity
python nebula-writer entity add "Ravi" --type character --desc "Detective"

# List chapters
python nebula-writer chapter list

# Visualize
python nebula-writer visualize
```

### REPL
```bash
python repl.py
```

## Architecture

```
nebula-writer/
├── backend/          # FastAPI server
│   ├── codex.py     # SQLite database
│   ├── ai_writer.py # AI writing
│   ├── memory.py    # ChromaDB RAG
│   ├── audit.py     # Story audit
│   └── ...
├── frontend/         # Vue.js UI
├── tests/           # Test suite
└── repl.py          # Interactive REPL
```

## Tech Stack

- **Backend**: FastAPI, Python 3.11+, SQLite
- **AI**: Google Gemini API
- **Memory**: ChromaDB
- **Frontend**: Vue.js 3, TailwindCSS
- **DevOps**: Docker, Makefile

## License

MIT License - feel free to use!

---

<p align="center">Made with ☕ by Sagar</p>
# Updated
