# Nebula-Writer-2

> **AI-powered writing assistant with multi-model support, document analysis, and content generation**

[![CI](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/main.yml/badge.svg)](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/main.yml)
[![Release](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/release.yml/badge.svg)](https://github.com/sagar0163/Nebula-Writer-2/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)

---

## 🎯 Problem

Writers, researchers, and content teams juggle multiple AI tools for drafting, editing, summarizing, and analyzing documents. Context switching kills productivity.

## 💡 Solution

A **unified writing workspace** that combines:

- **Multi-model AI** — OpenAI, Anthropic, local (Ollama), NVIDIA NIM, together
- **Document intelligence** — semantic search, Q&A, extraction, structure analysis
- **Content generation** — articles, reports, code docs, emails, creative writing
- **Workflow automation** — pipelines for research → outline → draft → polish

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Nebula-Writer Core                        │
├─────────────┬─────────────┬─────────────┬──────────────────────┤
│  Model      │  Document   │  Pipeline   │  Export              │
│  Router     │  Store      │  Engine     │  (MD/PDF/DOCX/HTML)  │
└─────────────┴─────────────┴─────────────┴──────────────────────┘
```

## 🚀 Quick Start

```bash
# Install
pip install nebula-writer

# Or with poetry
poetry add nebula-writer

# Initialize workspace
nebula-writer init my-project
cd my-project

# Configure models
nebula-writer config set openai.api_key $OPENAI_API_KEY
nebula-writer config set anthropic.api_key $ANTHROPIC_API_KEY
```

## ⚙️ Configuration

```yaml
# nebula.yaml
models:
  default: gpt-4o-mini
  available:
    - name: gpt-4o
      provider: openai
      tier: premium
    - name: claude-3-5-sonnet
      provider: anthropic
      tier: premium
    - name: llama-3.1-70b
      provider: ollama
      tier: local
    - name: nemotron-3-ultra
      provider: nvidia
      tier: free

document_store:
  type: sqlite  # or chromadb, pgvector
  path: ./data/documents.db

pipelines:
  - name: research-to-article
    steps:
      - search_web
      - extract_key_points
      - generate_outline
      - write_draft
      - fact_check
      - polish
```

## 📖 Usage

### Interactive mode
```bash
nebula-writer chat
> Summarize the PDF in ./docs/research.pdf
> Generate a blog outline from these notes
> Rewrite this section for technical audience
```

### Pipeline execution
```bash
nebula-writer run research-to-article --topic "AI agents in 2025"
```

### Document analysis
```bash
nebula-writer analyze ./docs/large-report.pdf \
  --extract entities,key-points,citations \
  --output analysis.json
```

## 🔌 Extending

### Custom pipeline step
```python
# steps/my_step.py
from nebula_writer.pipeline import Step


class MyStep(Step):
    name = "my_step"

    async def run(self, context):
        # Transform context
        return context
```

### Custom model provider
```python
# providers/my_provider.py
from nebula_writer.models import BaseProvider


class MyProvider(BaseProvider):
    async def complete(self, prompt, **kwargs):
        # Your implementation
        pass
```

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ --cov=nebula_writer
```

## 📦 Release

```bash
poetry version patch
git push origin main --tags
# GitHub Actions: test → build → release → PyPI
```

## 📄 License

MIT License

---

**Transform your writing workflow with AI that understands your context**