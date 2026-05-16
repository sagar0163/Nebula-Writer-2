# Tasks: vision-gap-plan

**Input**: Design documents from `/specs/001-vision-gap-plan/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: The task list includes dedicated automated test tasks for each user story to ensure full adherence to the 11-step Writer Experience Test suite.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `nebula_writer/` at repository root
- **Frontend**: `frontend/` at repository root
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment verification

- [ ] T001 Initialize Python virtual environment and verify python 3.11+ in .venv
- [ ] T002 Update requirements.txt with fastapi, uvicorn, pydantic, websockets, ebooklib, python-docx, weasyprint, jinja2, pytest
- [ ] T003 [P] Copy .env.example to .env and configure BRAVE_API_KEY placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create database schema migration script for projects, chapters, characters, comments, research_nodes, lookahead_cards in nebula_writer/schema.sql
- [ ] T005 Implement core database access methods for new entities in nebula_writer/postgres_db.py
- [ ] T006 Implement core database access methods for new entities in nebula_writer/supabase_db.py
- [ ] T007 [P] Create base Pydantic domain models for API requests and responses in nebula_writer/models.py
- [ ] T008 Configure structured logging and error handling middleware in nebula_writer/main.py
- [ ] T009 Create end-to-end test harness structure in tests/test_writer_experience.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-Time Chapter Streaming & Quality Assurance (Priority: P1) 🎯 MVP

**Goal**: Deliver real-time Server-Sent Events (SSE) chapter streaming with automated background quality gate evaluation and anti-slop cliches filtering.

**Independent Test**: Request a chapter generation in Chat Mode and verify real-time word-by-word streaming of high-quality, non-repetitive prose.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Create automated test for SSE chapter streaming and quality gate evaluation in tests/test_writer_experience.py

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create QualityEngine class implementing 8-criteria scoring rubric in nebula_writer/quality_engine.py
- [ ] T012 [P] [US1] Create AntiSlop filter class detecting and replacing AI cliches in nebula_writer/anti_slop.py
- [ ] T013 [US1] Implement internal AI revision loop (up to 3 passes) within QualityEngine in nebula_writer/quality_engine.py
- [ ] T014 [US1] Implement POST /api/chat endpoint returning StreamingResponse with SSE token emission in nebula_writer/main.py
- [ ] T015 [US1] Integrate QualityEngine and AntiSlop filtering into chapter generation stream in nebula_writer/main.py
- [ ] T016 [US1] Implement real-time SSE token rendering in Vue.js chat interface in frontend/index.html

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Intuitive Natural Language Interaction (Priority: P1)

**Goal**: Deliver hybrid intent classification combining high-speed regex matching with an LLM fallback for nuanced conversational requests.

**Independent Test**: Submit varied natural language requests and verify accurate intent classification and entity extraction.

### Tests for User Story 2 ⚠️

- [ ] T017 [P] [US2] Create automated test for natural language intent classification and entity extraction in tests/test_writer_experience.py

### Implementation for User Story 2

- [ ] T018 [US2] Implement regex fast-path matching for structured writer commands in nebula_writer/conversation.py
- [ ] T019 [US2] Implement LLM fallback classification and entity extraction in nebula_writer/conversation.py
- [ ] T020 [US2] Integrate hybrid classification engine into message routing flow in nebula_writer/conversation.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Interactive Studio Mode & Live Codex Synchronization (Priority: P2)

**Goal**: Deliver dedicated Studio Mode Codex Browser with bi-directional WebSocket live synchronization and inline character lore editing.

**Independent Test**: Modify a character attribute inline in Studio Mode and verify instant background propagation updates across active sessions without page reloads.

### Tests for User Story 3 ⚠️

- [ ] T021 [P] [US3] Create automated test for WebSocket live codex synchronization and inline character editing in tests/test_writer_experience.py

### Implementation for User Story 3

- [ ] T022 [P] [US3] Implement CodexSyncManager connection manager class in nebula_writer/main.py
- [ ] T023 [US3] Implement WebSocket endpoint /ws/sync/{project_id} with 30s heartbeat ping/pong in nebula_writer/main.py
- [ ] T024 [US3] Implement background story graph event broadcast methods in nebula_writer/services/orchestrator.py
- [ ] T025 [US3] Implement 3-card lookahead forecasting deck generation and SSE emission in nebula_writer/lookahead_engine.py
- [ ] T026 [US3] Implement Brave Search API integration and research node storage in nebula_writer/research.py
- [ ] T027 [US3] Implement Studio Mode Codex Browser UI, character inline editing, and WebSocket client sync in frontend/index.html

**Checkpoint**: All P1 and P2 user stories should now be independently functional

---

## Phase 6: User Story 4 - Precision Inline Commenting & Targeted Revision (Priority: P2)

**Goal**: Deliver character-offset anchored inline comments with targeted AI revisions restricted solely to the highlighted span.

**Independent Test**: Highlight a text span, submit a revision comment, and verify only the selected text changes while triggering a subsequent ripple consistency check.

### Tests for User Story 4 ⚠️

- [ ] T028 [P] [US4] Create automated test for anchored inline comments and targeted AI revision spans in tests/test_writer_experience.py

### Implementation for User Story 4

- [ ] T029 [US4] Implement POST /api/comments endpoint accepting character-offset anchor fields in nebula_writer/main.py
- [ ] T030 [US4] Implement targeted AI revision span generation adhering to Minimum Change Principle in nebula_writer/comment_system.py
- [ ] T031 [US4] Implement post-revision ripple effect validation checks in nebula_writer/ripple_checker.py
- [ ] T032 [US4] Implement text highlighting, comment anchoring, and accept/reject revision UI in frontend/index.html

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Professional Multi-Format Manuscript Export (Priority: P3)

**Goal**: Deliver publishing-grade multi-format document exports including EPUB 3.0, manuscript DOCX, and print-ready PDF.

**Independent Test**: Trigger an export for EPUB, DOCX, and PDF on a completed novel project and verify valid document formatting.

### Tests for User Story 5 ⚠️

- [ ] T033 [P] [US5] Create automated test for EPUB, manuscript DOCX, and PDF document generation in tests/test_writer_experience.py

### Implementation for User Story 5

- [ ] T034 [P] [US5] Implement EPUB 3.0 export generation using ebooklib in nebula_writer/exporter.py
- [ ] T035 [P] [US5] Implement manuscript DOCX export generation using python-docx in nebula_writer/exporter.py
- [ ] T036 [P] [US5] Implement print-ready PDF export generation using weasyprint in nebula_writer/exporter.py
- [ ] T037 [US5] Implement GET /api/export/epub and GET /api/export/docx endpoints in nebula_writer/main.py
- [ ] T038 [US5] Implement multi-format export download buttons in Chat Mode and Studio Mode UI in frontend/index.html

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: System verification, documentation updates, and cross-cutting improvements

- [ ] T039 [P] Update project API documentation in API.md
- [ ] T040 Execute full 11-step Writer Experience Test suite using pytest tests/test_writer_experience.py
- [ ] T041 Verify quickstart onboarding instructions and validate clean startup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independently testable Studio Mode UI and WebSocket sync
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independently testable inline comment anchoring
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independently testable document export generation

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- All tests for a user story marked [P] can run in parallel
- Export generators within US5 marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch test task for User Story 1:
Task: "Create automated test for SSE chapter streaming and quality gate evaluation in tests/test_writer_experience.py"

# Launch core engine modules for User Story 1 in parallel:
Task: "Create QualityEngine class implementing 8-criteria scoring rubric in nebula_writer/quality_engine.py"
Task: "Create AntiSlop filter class detecting and replacing AI cliches in nebula_writer/anti_slop.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo real-time SSE chapter streaming

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 & 2 (Core Chat & Intent)
   - Developer B: User Story 3 (Studio Mode & WebSocket Sync)
   - Developer C: User Story 4 & 5 (Inline Comments & Multi-Format Export)
3. Stories complete and integrate independently
