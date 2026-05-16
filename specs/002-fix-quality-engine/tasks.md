# Tasks: True LLM Orchestration and Quality Engine

**Input**: Design documents from `/specs/002-fix-quality-engine/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/chat-api.md, quickstart.md

**Tests**: The examples below include test verification tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `nebula_writer/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify virtual environment and existing project dependencies in pyproject.toml
- [x] T002 [P] Inspect existing test suites in tests/test_writer_experience.py to establish baseline expectations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Establish Pydantic schemas for ChatMessage and ChatRequest in nebula_writer/conversation.py
- [x] T004 Establish Pydantic schemas for QualityRubric and ManuscriptDraft in nebula_writer/quality_engine.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Conversational Chat & Story Q&A (Priority: P1) 🎯 MVP

**Goal**: Enable natural, context-aware conversation with the AI assistant about novel projects without triggering repetitive chapter generation text.

**Independent Test**: Verify via cURL or pytest that general chat prompts return conversational responses rather than story prose.

### Implementation for User Story 1

- [x] T005 [US1] Refactor chat_with_ai in nebula_writer/main.py to extract AI response using raw_response.get("message") instead of raw_response.get("response")
- [x] T006 [US1] Verify intent routing logic in nebula_writer/conversation.py correctly classifies general chat and RAG queries
- [x] T007 [US1] Run unit tests in tests/test_writer_experience.py to verify conversational chat routing succeeds

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - AI-Powered Prose Quality Revision Loop (Priority: P2)

**Goal**: Automatically evaluate initial chapter drafts against professional storytelling criteria and perform intelligent, AI-driven revisions.

**Independent Test**: Verify that chapter generation requests invoke the asynchronous LLM revision loop and produce high-quality prose.

### Implementation for User Story 2

- [x] T008 [US2] Implement QualityEngine.evaluate_prose() in nebula_writer/quality_engine.py to score prose against the 8-criteria rubric
- [x] T009 [US2] Replace hardcoded string manipulation stubs in QualityEngine.revise_prose() in nebula_writer/quality_engine.py with authentic asynchronous LLM calls via AIWriter.generate()
- [x] T010 [US2] Update Orchestrator coordination logic in nebula_writer/services/orchestrator.py to handle the multi-pass quality engine revision loop
- [x] T011 [US2] Run unit tests in tests/test_writer_experience.py to verify quality engine evaluation and revision loop

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Automated Anti-Slop Filtering (Priority: P3)

**Goal**: Automatically identify and eliminate common AI writing clichés and repetitive structural patterns from chapter drafts before delivery.

**Independent Test**: Verify that generated chapters contain zero occurrences of defined AI filler phrases.

### Implementation for User Story 3

- [x] T012 [US3] Implement cliché scrubbing and structural filtering logic in nebula_writer/anti_slop.py
- [x] T013 [US3] Integrate AntiSlopLayer into the streaming generation pipeline in nebula_writer/main.py before SSE token streaming
- [x] T014 [US3] Run unit tests in tests/test_writer_experience.py to verify anti-slop filtering layer

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T015 [P] Verify quickstart instructions in specs/002-fix-quality-engine/quickstart.md against local environment
- [x] T016 Execute full end-to-end verification suite in tests/test_writer_experience.py to ensure complete regression safety

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch verification tasks for User Story 1 together:
Task: "Verify intent routing logic in nebula_writer/conversation.py correctly classifies general chat and RAG queries"
Task: "Run unit tests in tests/test_writer_experience.py to verify conversational chat routing succeeds"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
