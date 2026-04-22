# Nebula-Writer v2.0

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
</p>

> AI-Powered Fiction Writing Assistant with Persistent Memory

Nebula-Writer is a "System of Record" for fiction that stores every character, location, and plot point so your AI never forgets. It uses RAG (Retrieval-Augmented Generation) to provide accurate context to AI writing, with support for multiple AI providers.

## Features

- **The Codex** - SQLite database for Characters, Locations, Items, Relationships
- **Chapter Management** - Write chapters with version history
- **Story Templates** - Three-Act, Hero's Journey, Save the Cat, Snowflake
- **Multi-AI** - Gemini, OpenAI GPT-4, Anthropic Claude
- **Consistency Check** - Auto-detect story contradictions
- **Character Knowledge** - Track what each character knows
- **Auto-Extract** - Extract entities from prose text
- **Semantic Search** - ChromaDB-powered RAG memory
- **Version History** - Full chapter version tracking
- **Visualization** - Mermaid.js relationship graphs
- **Web UI** - Beautiful Vue.js interface
- **Export** - Markdown, HTML, Plain Text, DOCX

## Quick Start

```bash
# Clone and install
git clone https://github.com/sagar0163/Nebula-Writer.git
cd Nebula-Writer
pip install -r requirements.txt

# Run the server
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

## Environment Variables

```bash
# Required for AI features
export GEMINI_API_KEY=your_gemini_key

# Optional - additional AI providers
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_claude_key
```

## Documentation

See the `docs/` folder for full documentation:
- [API Reference](docs/API.md)
- [Features Guide](docs/FEATURES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.10+, SQLite |
| AI | Gemini, OpenAI GPT-4, Claude |
| Memory | ChromaDB (RAG) |
| Frontend | Vue.js 3, TailwindCSS |
| DevOps | Docker |

## Project Structure

```
nebula-writer/
├── backend/          # FastAPI server
│   ├── main.py      # API entry point
│   ├── codex.py    # SQLite database layer
│   ├── ai_writer.py    # AI writing
│   ├── ai_client.py  # Multi-AI client (NEW)
│   ├── memory.py    # ChromaDB RAG
│   └── exporter.py  # Export formats
├── frontend/         # Vue.js SPA
│   └── index.html
├── docs/            # Documentation (NEW)
├── tests/           # Test suite
└── specs/          # BRD and architecture
```

## License

MIT License - feel free to use!

---

<p align="center">Made with love by Sagar</p>