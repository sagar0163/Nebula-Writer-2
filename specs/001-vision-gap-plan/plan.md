# Implementation Plan: vision-gap-plan

**Branch**: `001-vision-gap-plan` | **Date**: 2026-05-16 | **Spec**: [spec.md](file:///home/sagar-jadhav/Documents/my%20project/nebula%20writer%202/specs/001-vision-gap-plan/spec.md)

**Input**: Feature specification from `/specs/001-vision-gap-plan/spec.md`

**Note**: This plan defines the concrete technical implementation strategy required to bridge the Six Gaps and Five Additions identified in the Nebula Writer 2 vision audit.

## Summary

This implementation plan establishes the architectural roadmap to transform Nebula Writer 2 into a professional, real-time AI co-writing platform. By maintaining the stable underlying engine layer (`nebula_writer/`), the plan introduces real-time Server-Sent Events (SSE) chapter streaming, hybrid regex/LLM intent classification, an autonomous 8-criteria quality gate, programmatic anti-slop filtering, character-offset anchored inline comments, bi-directional WebSocket live codex synchronization, and professional multi-format manuscript exports (EPUB, DOCX, PDF).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, uvicorn, pydantic, websockets, ebooklib, python-docx, weasyprint, jinja2

**Storage**: SQLite / PostgreSQL / Supabase (leveraging existing `postgres_db.py`, `supabase_db.py`, `codex.py` schemas)

**Testing**: pytest (executing the comprehensive 11-step Writer Experience Test suite)

**Target Platform**: Linux server backend / Modern Web Browser (Vue.js frontend)

**Project Type**: Web-service / Desktop-app hybrid platform

**Performance Goals**: Chapter generation streaming initial token latency < 2s; WebSocket live codex synchronization < 1s; Intent classification < 50ms for regex fast-path

**Constraints**: Minimum Change Principle strictly enforced for inline comments (revisions restricted solely to anchor span); Asynchronous background processing required for large multi-chapter document exports

**Scale/Scope**: Multi-chapter novel projects supporting dozens of linked character profiles, research nodes, and lookahead forecasting cards with real-time state broadcast

## Constitution Check

*GATE: Re-checked after Phase 1 design.*

- **Principle I (Library-First)**: Passed. Core capabilities are encapsulated in modular, testable engine files (`quality_engine.py`, `anti_slop.py`, `exporter.py`, `comment_system.py`) independent of HTTP transport layers.
- **Principle II (API/CLI Interface)**: Passed. Clean, documented I/O protocols and REST/WebSocket contracts are defined for all client-server interactions.
- **Principle III (Test-First / TDD)**: Passed. All requirements are backed by concrete acceptance criteria in the 11-step Writer Experience Test suite.
- **Principle IV (Integration Testing)**: Passed. Inter-service communication between the AI orchestrator, codex sync manager, and comment engine is fully covered by automated verification flows.
- **Principle V (Observability & Simplicity)**: Passed. Incorporates structured logging and transparent diagnostic flags (e.g., anti-slop markers in Studio Mode) while avoiding unnecessary transport complexity.

## Project Structure

### Documentation (this feature)

```text
specs/001-vision-gap-plan/
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Specification quality checklist
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── contracts/
    └── api.md           # Phase 1 output (/speckit-plan command)
```

### Source Code (repository root)

```text
nebula_writer/
├── __init__.py
├── main.py              # FastAPI server, SSE streaming, WebSocket sync endpoint
├── conversation.py      # Hybrid regex/LLM intent classification engine
├── quality_engine.py    # [NEW] Automated 8-criteria quality gate evaluation
├── anti_slop.py         # [NEW] Programmatic stylistic post-processor
├── comment_system.py    # Anchored inline comment engine and targeted revision
├── exporter.py          # EPUB 3.0, manuscript DOCX, and PDF document generation
├── research.py          # Brave Search API integration and research node management
├── lookahead_engine.py  # 3-card forecasting deck generation
├── codex.py             # Core story graph and entity database management
├── orchestrator.py      # Story graph updates and WebSocket event broadcast
└── ... (existing stable engine layer)

frontend/
└── index.html           # Vue.js frontend, Studio Mode Codex Browser, live WebSocket sync

tests/
├── test_core.py
└── test_writer_experience.py # [NEW] 11-step end-to-end verification suite
```

**Structure Decision**: The selected structure augments the existing `nebula_writer` package with dedicated quality and stylistic filtering modules while extending existing service handlers to support real-time streaming, live synchronization, and multi-format document generation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | No constitution violations introduced. |
