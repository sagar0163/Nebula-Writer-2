# Phase 1: Developer Quickstart Guide

**Feature**: vision-gap-plan
**Date**: 2026-05-16

This guide provides developer onboarding instructions for setting up the local development environment, configuring external API integrations, running the backend server, and executing the automated verification test suite for Nebula Writer 2.

---

## Prerequisites

Ensure the following system dependencies are installed:
- **Python**: Version 3.11 or higher.
- **Git**: For version control and branch management.
- **Node.js / npm** (Optional): For advanced frontend asset bundling, though Vue.js can operate via direct CDN inclusion in `index.html`.

---

## 1. Environment Setup

1. **Clone and Checkout**: Ensure you are on the correct feature branch:
   ```bash
   git checkout 001-vision-gap-plan
   ```

2. **Virtual Environment**: Create and activate a dedicated Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**: Install all required core packages, including the new document export and websocket libraries:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn pydantic websockets ebooklib python-docx weasyprint jinja2 pytest
   ```

---

## 2. Configuration & API Keys

The platform relies on environment variables for external service integration.

1. **Copy Environment Template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure External Search** (Addition 13):
   Open `.env` in your preferred editor and add your Brave Search API key to enable verified factual research queries without falling back to basic web scraping:
   ```env
   BRAVE_API_KEY=your_actual_brave_search_api_key_here
   ```

---

## 3. Running the Application Server

Start the FastAPI backend server using `uvicorn` with live reloading enabled for local development:

```bash
uvicorn nebula_writer.main:app --reload --port 8000
```

The application will be accessible at:
- **Web Interface**: `http://localhost:8000/`
- **Interactive API Docs (Swagger)**: `http://localhost:8000/docs`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/sync/{project_id}`

---

## 4. Running the Automated Verification Suite

To verify that all Six Gaps and Five Additions operate correctly and adhere to the project constitution, run the comprehensive `pytest` suite covering the 11-step Writer Experience Test:

```bash
pytest tests/ -v
```

### Expected Output
The test execution should validate all core flows:
- Real-time SSE streaming token rendering.
- Regex and LLM intent classification accuracy.
- Automated 8-criteria quality gate evaluation and internal revision loops.
- Programmatic anti-slop filtering.
- Anchored inline comments and targeted AI revision spans.
- Validated EPUB, manuscript DOCX, and PDF document generation.
- Bi-directional WebSocket live codex synchronization.
