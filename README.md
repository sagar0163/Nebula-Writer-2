# Nebula-Writer-2
# Nebula-Writer-2
> **The AI co-author that never forgets your story.**
[![CI](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/main.yml/badge.svg)](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/main.yml)
[![Release](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/release.yml/badge.svg)](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org/)

---

## 🎯 Problem

Generic AI chat tools produce nice prose, but they cannot keep a novel consistent. Writers burn hundreds of hours manually maintaining story bibles and hunting contradictions after a direction change — new writers and seasoned novelists alike.

## 💡 Solution — The Canon-Safe Co-Writing Loop

Nebula-Writer's single core experience: from a one-line idea to a finished novel, every interaction flows through a living story canon (the **Codex**) that the AI maintains *for* you.

```
 Idea ─► Codex ─► Chapters ─► Comment ─► Ripple ─► Manuscript
        (canon)    (write)     (rewrite)  (what breaks)
```

- **Idea → Codex** — describe a concept; Nebula-Writer builds persistent characters, relationships, plot threads, world rules, and timeline.
- **Beat → Chapter** — chapters are generated grounded in the full canon; no invented facts, no contradictions.
- **Comment → Rewrite** — highlight a span, leave a note, get a surgical rewrite that changes *only* what you asked.
- **Pivot → Ripple** — "actually, the killer is the brother" shows you exactly what breaks and rewrites the affected scenes to keep the whole manuscript consistent.
- **Manuscript** — a finished, internally-consistent novel you can export.

> **Strategy:** see [docs/STRATEGY.md](docs/STRATEGY.md) — the ratified core-first roadmap and full noise inventory (Issue #146).

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Nebula-Writer Core                     │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Codex       │  AI Writer   │  Ripple      │  Quality      │
│  (canon)     │  (pipeline)  │  Checker     │  Engine       │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

Built on FastAPI + LangGraph (PLAN → WRITE → VALIDATE → EVALUATE) with a multi-provider LLM fallback chain (Mistral / Gemini / OpenAI / local) and SQLite/Supabase persistence.

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# Run the API server
uvicorn nebula_writer.main:app --host 0.0.0.0 --port 8000 --reload

# Chat-driven writing (SSE streaming)
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write Chapter 1", "stream": true}'
```

See [QUICK_START.md](QUICK_START.md) and [API.md](API.md) for full setup and endpoints.

## 📖 Core Commands

```bash
# Seed a project from an idea
nebula-writer idea "a mystery set in Mumbai" --project my-novel

# Write a scene
curl -X POST http://localhost:8000/api/ai/write \
  -H "Content-Type: application/json" \
  -d '{"beat": "The detective makes a discovery", "word_count": 500}'
```

## 🧪 Testing

```bash
pytest tests/ -v
ruff check . && ruff format --check .
```

## 🗺️ Roadmap (core-first)

- **Phase 1 — The Loop Works:** canon-correct chapters, surgical comment rewrites, ripple analysis, idea→Codex, basic manuscript export.
- **Phase 2 — The Loop Feels Like Magic:** streaming polish, Studio Mode, deeper ripple intelligence, style learning.
- **Phase 3 — The Loop Ships Novels:** publication-grade EPUB/DOCX/PDF, research engine, collaboration.

Everything not in service of the core loop is deferred. See [docs/STRATEGY.md](docs/STRATEGY.md) for the full inventory and decision guardrails.

## 📄 License

MIT License

---

**Someday, every serious novelist will have a co-author that never loses the thread. That co-author is this one.**