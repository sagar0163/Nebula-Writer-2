# Nebula-Writer Project State
*Last updated: July 12, 2026*

---

## 📍 Project Location
```
E:\my project folder\Nebula-Writer-2\
```

## 🎯 Project Overview
**Nebula-Writer v2.1** — AI-powered fiction writing assistant ("System of Record" for novels)

### Architecture
```
Vue.js Frontend (5173) → FastAPI Backend (8000) → PostgreSQL (Supabase) + ChromaDB (Vector) + LangChain (LLM Router)
```

### Core Stack
| Layer | Technology |
|-------|------------|
| **Database** | PostgreSQL (Supabase) — entities, chapters, relationships, events |
| **Vector Memory** | ChromaDB via `langchain-chroma` — semantic search over prose |
| **LLM Orchestration** | LangChain + LangGraph — pipeline: PLAN → WRITE → VALIDATE → EVALUATE |
| **Models** | Mistral (primary), Gemini, OpenAI, Anthropic (fallback chain) |
| **Frontend** | Vue.js + Tailwind (port 5173) |

### Key Features (Implemented)
- ✅ **Codex CRUD** — entities, attributes, relationships (`/api/entities`, `/api/relationships`)
- ✅ **Chapter/Scene Management** — version history (`/api/chapters`, `/api/scenes`)
- ✅ **AI Scene Writing** — pacing, POV, tone controls (`/api/ai/write`, `AIWriter`)
- ✅ **Story Architect Chat** — full context awareness (`/api/chat`, `ConversationEngine`)
- ✅ **Consistency Audit** — contradiction detection (`/api/audit`, `RippleChecker`)
- ✅ **Style Learning** — mimics author voice (`StyleLearner`)
- ✅ **Plot Threads/Tensions/Anchors** — `PlotManager`
- ✅ **Narrative State Engine** — phase, momentum (`NarrativeStateEngine` v2.1)
- ✅ **LangGraph Pipeline** — `PipelineExecutor` with evaluation harness
- ✅ **Character Agents** — derived goals/intent (`CharacterAgent`)
- ✅ **Export** — MD, HTML, DOCX, Mermaid graphs (`Exporter`)

---

## 🛠️ gstack — AI Engineering Toolkit (Embedded)

Located at `E:\my project folder\Nebula-Writer-2\gstack\`

### What It Is
A collection of **80+ specialized SKILL.md files** that give AI agents structured roles for software engineering workflows. Not part of the novel-writing product — it's the **meta-toolkit used to build Nebula-Writer**.

### Available Skills (Key Ones)
| Category | Skills |
|----------|--------|
| **Planning** | `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `autoplan`, `spec` |
| **Review/QA** | `review`, `codex`, `investigate`, `design-review`, `qa`, `devex-review`, `qa-only` |
| **Release** | `ship`, `land-and-deploy`, `canary`, `landing-report` |
| **Operations** | `context-save`, `context-restore`, `learn`, `retro`, `health`, `benchmark`, `setup-gbrain` |
| **Browser** | `browse`, `open-gstack-browser`, `setup-browser-cookies`, `pair-agent` |
| **iOS QA** | `ios-qa`, `ios-fix`, `ios-design-review` |

### How to Use (in any AI agent that supports skills)
```bash
# Load the gstack router skill
/skill gstack

# Then invoke specific skills
/skill review          # Code review
/skill investigate     # Debug a bug
/skill qa              # Full QA test + fix
/skill ship            # Create PR, run tests, merge
/skill spec            # Turn vague idea into executable spec
/skill plan-eng-review # Architecture review before coding
```

### Host Adapters
- `gstack/hosts/opencode.ts` — OpenCode
- `.opencode/skills/gstack/` — OpenCode skill symlinks
- `.claude/skills/gstack/` — Claude Code skill symlinks
- `.cursor/skills/gstack/` — Cursor skill symlinks

---

## 🐛 Issues Found & Fixed (This Session)

### ✅ FIXED: Chapter ID Type Mismatch
**Location:** `nebula_writer/ai_writer.py` → `get_context()` → `db.get_chapter()` / `db.get_events()`

**Problem:** `AIWriteRequest.chapter` is `int` (chapter number), but `get_chapter(chapter_id)` treated truthy int as UUID, causing PostgreSQL error: `operator does not exist: uuid = integer`

**Fix Applied:**
1. `supabase_db.py` — `get_chapter()`: Check if `chapter_id` looks like UUID (contains `-`, len > 10) before querying by `id`
2. `supabase_db.py` — `get_events()`: Added `chapter_id` parameter, resolves to chapter number internally
3. `ai_writer.py` — `get_context()`: Pass UUID as `chapter_id`, int as `chapter` to both methods

**Verification:** Direct `AIWriter.write_scene(chapter=1)` works ✅

---

### ✅ FIXED: Missing Dependencies
| Package | Purpose |
|---------|---------|
| `langchain-chroma` | Vector memory for chat (`MemorySystem` in `memory.py`) |
| `sentence-transformers` | Local embeddings (fallback when no API keys) |

Installed via `pip install langchain-chroma sentence-transformers`

---

### ⚠️ REMAINING: Code Quality Issues

| Issue | Files Affected | Count |
|-------|---------------|-------|
| **Bare `except:` clauses** | `research.py`, `ripple_checker.py`, `spatial_mapper.py` | 4 |
| **Print statements** (should use logging) | Across codebase | 79 |
| **Type hints missing** | Various modules | — |

---

## 🔌 API Endpoint Status

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/entities` | GET/POST | ✅ | 9 entities loaded |
| `/api/entities/{id}` | GET/PUT/DELETE | ✅ | |
| `/api/chapters` | GET/POST | ✅ | 5 chapters (769 words) |
| `/api/chapters/{id}` | GET/PUT | ✅ | |
| `/api/stats` | GET | ✅ | |
| `/api/export/mermaid` | GET | ✅ | Relationship graph |
| `/api/pipeline/write` | POST | ✅ | Full LangGraph pipeline, ~3500 words |
| `/api/pipeline/evaluate` | POST | ✅ | Evaluation harness |
| `/api/ai/write` | POST | ⚠️ **TIMEOUT** | Works direct (13s), times out via HTTP |
| `/api/ai/rewrite` | POST | ⚠️ | Untested |
| `/api/ai/describe` | POST | ⚠️ | Untested |
| `/api/ai/show-not-tell` | POST | ⚠️ | Untested |
| `/api/chat` | POST | ⚠️ | Needs testing after deps installed |
| `/api/audit` | GET | ⚠️ | Server crashed on test |

---

## 🗄️ Database State (Supabase)

### Current Data
| Table | Count | Details |
|-------|-------|---------|
| `entities` | 9 | 5 characters, 4 locations |
| `chapters` | 5 | Ch 1–5, ~150 words each |
| `relationships` | 6 | haunted_by, investigates, protects, suspects, reluctant_partners |
| `events` | 1 | Test event |
| `total_words` | 769 | |

### Key Entities
- **Detective Arjun Rathore** — protagonist, haunted by Maya's disappearance
- **Maya (Missing Girl)** — cold case from 5 years ago
- **Mohan Bhosle** — construction magnate, suspect
- **Sundar** — protected by Arjun
- **Zara Khan** — journalist, investigates Bhosle

---

## 🚀 How to Run

### Backend
```bash
cd E:\my project folder\Nebula-Writer-2
# .env must exist with:
# GEMINI_API_KEY, MISTRAL_API_KEY, HUGGINGFACE_API_KEY
# SUPABASE_URL, SUPABASE_ANON_KEY, POSTGRES_CONNECTION_STRING

python -m uvicorn nebula_writer.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (separate terminal)
```bash
cd E:\my project folder\Nebula-Writer-2\frontend
npm install
npm run dev
# Opens http://localhost:5173
```

### Test Direct (Python)
```python
import sys
sys.path.insert(0, r"E:\my project folder\Nebula-Writer-2")
from dotenv import load_dotenv
load_dotenv(r"E:\my project folder\Nebula-Writer-2\.env")

from nebula_writer.supabase_db import SupabaseDB
from nebula_writer.ai_writer import AIWriter
import asyncio

db = SupabaseDB()
ai = AIWriter()

# Test write_scene
result = asyncio.run(ai.write_scene(
    db=db,
    beat="Arjun finds a mysterious key",
    word_count=300,
    chapter=1,  # int = chapter number
    pacing="steady",
    pov="third_person_limited",
    tone="suspenseful"
))
print(result)
```

---

## 📋 Next Steps Priority

### High Priority
1. **Fix `/api/ai/write` timeout** — Direct call works (13s), but HTTP times out. Options:
   - Increase uvicorn timeout
   - Make async with background task + polling endpoint
   - Reduce `max_tokens` / optimize prompt

2. **Test `/api/chat`** — Now that `langchain-chroma` is installed, should work

3. **Fix bare `except:` clauses** — Replace with specific exceptions

### Medium Priority
4. **Replace print → logging** — Add `logging.config` setup in `main.py`

5. **Add type hints** — Run `mypy` / `pyright` for CI

6. **Run full QA** — Use gstack `/skill qa` on the running app

### Low Priority
7. **Clean up gstack** — It's 200MB+ in repo; consider git submodule or separate repo

8. **Add real API keys** — Only Mistral is real; Gemini/OpenAI/Anthropic are placeholders

9. **Frontend integration** — Test Vue app against backend

---

## 🔑 Environment Variables (`.env`)
```env
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key_here
MISTRAL_API_KEY=Gb3njaKZE1JsyNnbPSBQtuLvlMCVMXJY  # WORKING
HUGGINGFACE_API_KEY=your_huggingface_token_here

# Database - Supabase PostgreSQL
SUPABASE_URL=https://slovnfrjidipspogvktb.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
POSTGRES_CONNECTION_STRING=postgresql://postgres.nwxlmmypbxotkjrtevoy:***@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Optional
NEBULA_MEMORY_PATH=data/memory
NEBULA_DEFAULT_WORD_COUNT=500
```

---

## 📝 Session Context for Continuation

### What We Did This Session
1. Discovered Nebula-Writer at `E:\my project folder\Nebula-Writer-2`
2. Mapped full codebase (40+ Python modules)
3. Installed missing dependencies (`psycopg2`, `langchain*`, `sentence-transformers`)
4. Verified database connectivity and existing story data
5. Tested core pipeline — `/api/pipeline/write` works end-to-end
6. **Fixed Chapter ID type mismatch bug** in `supabase_db.py` and `ai_writer.py`
7. Installed `langchain-chroma` and `sentence-transformers` for chat/memory
8. Documented gstack skill system (80+ skills available)

### Key Files Modified
| File | Change |
|------|--------|
| `nebula_writer/supabase_db.py` | `get_chapter()` UUID detection, `get_events()` accepts `chapter_id` |
| `nebula_writer/ai_writer.py` | `get_context()` passes correct params to fixed DB methods |

### To Resume on Another Machine
1. Copy `E:\my project folder\Nebula-Writer-2` to new machine
2. Ensure Python 3.11+ and Node.js 18+
3. `pip install -r nebula_writer/requirements.txt` (plus `langchain-chroma sentence-transformers`)
4. Copy `.env` with valid API keys
5. Run backend + frontend as shown above
6. Use gstack skills: `/skill investigate` for bugs, `/skill qa` for testing, `/skill review` for PRs

---

## 🎭 gstack Quick Reference

```bash
# In any supported agent (OpenCode, Claude Code, Cursor, Hermes):
/skill gstack           # Router - asks which skill you need
/skill review           # Pre-landing PR review (SQL safety, LLM trust boundaries)
/skill investigate      # Systematic debugging (4 phases: investigate → analyze → hypothesize → implement)
/skill qa               # Full QA test + fix cycle (Quick/Standard/Exhaustive)
/skill spec             # Turn vague intent into executable GitHub issue
/skill plan-eng-review  # Architecture review before coding
/skill ship             # Run tests, review diff, bump version, update CHANGELOG, push, create PR
/skill autoplan         # Auto-run all reviews with 6 decision principles
/skill careful          # Guardrails for destructive commands
/skill learn            # Save learnings to ~/.gstack/projects/{slug}/learnings.jsonl
```

---

*Generated by Hermes Agent using gstack investigation methodology*
