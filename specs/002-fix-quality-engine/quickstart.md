# Quickstart: Testing LLM Orchestration & Quality Engine

**Feature**: True LLM Orchestration and Quality Engine
**Branch**: `002-fix-quality-engine`

This guide explains how developers and testers can verify the newly refactored conversational chat routing and authentic LLM-driven Quality Engine.

## Prerequisites

Ensure your Python virtual environment is active and all required dependencies are installed:
```bash
poetry install
# or pip install -r requirements.txt
```

Verify that your Supabase database and LLM API keys are correctly configured in your `.env` file:
```bash
SUPABASE_URL="https://your-supabase-url.supabase.co"
SUPABASE_KEY="your-supabase-key"
LLM_API_KEY="your-llm-api-key"
```

## Running the Application Locally

Start the FastAPI development server:
```bash
poetry run uvicorn nebula_writer.main:app --reload --port 8000
```

## Manual Verification via cURL

### 1. Test General Conversational Chat
Send a general greeting or clarifying question to verify that the assistant responds conversationally without triggering chapter generation:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me develop my main character?", "project_id": "default_project", "stream": true}'
```

### 2. Test Chapter Generation & Quality Engine
Send an explicit chapter generation command to verify the multi-pass revision loop and token streaming:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write Chapter 1", "project_id": "default_project", "stream": true}'
```

## Running Automated Tests

Run the dedicated test suite using `pytest` to verify intent classification, quality engine scoring, and anti-slop filtering:
```bash
poetry run pytest tests/test_writer_experience.py -v
```
