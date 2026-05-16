# Implementation Plan: True LLM Orchestration and Quality Engine

**Branch**: `002-fix-quality-engine` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-fix-quality-engine/spec.md`

## Summary

Replace mock QualityEngine string manipulation stubs and Chat routing fallbacks with authentic, asynchronous LLM orchestration, enabling a robust multi-pass quality revision loop and real-time SSE token streaming.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Supabase, pytest, pydantic

**Storage**: PostgreSQL (via Supabase)

**Testing**: pytest

**Target Platform**: Linux server / Containerized deployment

**Project Type**: web-service / library

**Performance Goals**: <500ms initial TTFB (Time to First Token) for streaming responses

**Constraints**: Max 3 revision passes per chapter draft; strict avoidance of AI filler clichés

**Scale/Scope**: Support multi-chapter novel generation workflows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Library-First**: All core revision and filtering logic is encapsulated in decoupled, independently testable library modules (`quality_engine.py`, `conversation.py`).
- **II. CLI Interface**: Core engine capabilities can be invoked and verified via CLI / text-based test runners.
- **III. Test-First**: Test suites (`test_writer_experience.py`) validate the generation and revision contracts prior to deployment.
- **IV. Integration Testing**: End-to-end integration tests verify the SSE streaming pipeline and database interaction.
- **V. Observability**: Comprehensive structured logging tracks intent classification scores, rubric breakdowns, and revision pass counts.

## Project Structure

### Documentation (this feature)

```text
specs/002-fix-quality-engine/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
nebula_writer/
├── main.py              # FastAPI application, routing, and SSE streaming
├── conversation.py      # Chat routing, intent classification, and message processing
├── quality_engine.py    # Authentic LLM revision loop and 8-criteria scoring rubric
├── anti_slop.py         # AI cliché scrubbing and structural filtering layer
└── services/
    └── orchestrator.py  # High-level pipeline coordination
```

**Structure Decision**: Single project web-service layout utilizing FastAPI and decoupled domain modules.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - Zero constitution violations.
