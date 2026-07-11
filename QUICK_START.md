# Nebula-Writer — Quick Reference
*For rapid onboarding on new machine*

---

## 🚀 One-Command Start
```bash
# Terminal 1: Backend
cd E:\my project folder\Nebula-Writer-2
python -m uvicorn nebula_writer.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd E:\my project folder\Nebula-Writer-2\frontend
npm run dev
```

---

## 🔑 Required `.env` Keys
```env
MISTRAL_API_KEY=Gb3njaKZE1JsyNnbPSBQtuLvlMCVMXJY  # WORKING
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

SUPABASE_URL=https://slovnfrjidipspogvktb.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
POSTGRES_CONNECTION_STRING=postgresql://postgres.nwxlmmypbxotkjrtevoy:***@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

---

## 🧪 Quick Tests (Python)
```python
import sys
sys.path.insert(0, r"E:\my project folder\Nebula-Writer-2")
from dotenv import load_dotenv
load_dotenv(r"E:\my project folder\Nebula-Writer-2\.env")

from nebula_writer.supabase_db import SupabaseDB
from nebula_writer.ai_writer import AIWriter
from nebula_writer.services.pipeline_executor import PipelineExecutor
import asyncio

db = SupabaseDB()
ai = AIWriter()
executor = PipelineExecutor(db)

# Test 1: Basic DB connection + write_scene (int chapter = chapter number)
print(asyncio.run(ai.write_scene(db=db, beat="Test beat", chapter=1, word_count=200)))

# Test 2: Full pipeline
print(asyncio.run(executor.execute_write_flow("Test beat", {})))

# Test 3: Chat
print(asyncio.run(executor.handle_chat("Who is Arjun?")))
```

---

## 🐛 Known Working / Broken

| Feature | Status | Notes |
|---------|--------|-------|
| DB Connection | ✅ | 9 entities, 5 chapters |
| `/api/entities` | ✅ | |
| `/api/chapters` | ✅ | |
| `/api/stats` | ✅ | |
| `/api/export/mermaid` | ✅ | |
| `/api/pipeline/write` | ✅ | Full LangGraph, ~3.5k words |
| `AIWriter.write_scene(chapter=1)` | ✅ | Direct call, 13s |
| `/api/ai/write` | ❌ TIMEOUT | HTTP timeout, direct works |
| `/api/chat` | ? | Needs test |

---

## 🛠️ gstack Skills Available
```bash
/skill gstack           # Router
/skill investigate      # Debug bugs (4-phase)
/skill review           # PR review
/skill qa               # QA test + fix
/skill spec             # Idea → GitHub issue
/skill plan-eng-review  # Arch review
/skill ship             # Test → PR → merge
/skill autoplan         # Auto all reviews
/skill careful          # Destructive cmd guard
```

---

## 📁 Key Files
| File | Purpose |
|------|---------|
| `nebula_writer/main.py` | FastAPI server, all endpoints |
| `nebula_writer/ai_writer.py` | AI writing (LangChain) |
| `nebula_writer/supabase_db.py` | PostgreSQL layer (FIXED: UUID/int) |
| `nebula_writer/services/pipeline_executor.py` | LangGraph orchestrator |
| `nebula_writer/graph/narrative_graph.py` | Compiled LangGraph |
| `nebula_writer/conversation.py` | Chat engine |
| `nebula_writer/memory.py` | ChromaDB vector memory |

---

## 🔧 If Things Break

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: psycopg2` | `pip install psycopg2-binary` |
| `ModuleNotFoundError: langchain_chroma` | `pip install langchain-chroma` |
| `ModuleNotFoundError: sentence_transformers` | `pip install sentence-transformers` |
| `uuid = integer` | Already fixed in `supabase_db.py:get_chapter()` |
| LLM timeout | Reduce `max_tokens` in `models.py` or increase uvicorn timeout |

---

## 📦 Install All Deps
```bash
pip install -r nebula_writer/requirements.txt
pip install langchain-chroma sentence-transformers
```
