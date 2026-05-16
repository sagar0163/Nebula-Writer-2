# Feature Specification: True LLM Orchestration and Quality Engine

**Feature Branch**: `002-fix-quality-engine`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Replace mock QualityEngine and Chat routing stubs with true LLM orchestration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversational Chat & Story Q&A (Priority: P1)

As a writer, I want to have a natural, context-aware conversation with the AI assistant about my novel project, asking questions about characters, plot points, or general brainstorming without accidentally triggering repetitive chapter generation text.

**Why this priority**: A smooth, intelligent conversational interface is essential for building author trust and establishing the AI as a capable creative partner.

**Independent Test**: Can be fully tested by sending general chat messages and RAG-based story questions, verifying that the assistant provides relevant, coherent conversational responses rather than manuscript prose.

**Acceptance Scenarios**:

1. **Given** an active story project with codex entries, **When** the user asks a question about a character or plot detail, **Then** the assistant responds with an accurate, conversational answer drawing from story facts.
2. **Given** a chat session, **When** the user sends a general greeting or prompt like "is that all?", **Then** the assistant provides a helpful, conversational follow-up clarifying its capabilities.

---

### User Story 2 - AI-Powered Prose Quality Revision Loop (Priority: P2)

As a writer generating chapter drafts, I want the system to automatically evaluate the initial prose against professional storytelling criteria and perform intelligent, AI-driven revisions behind the scenes, ensuring the final output is rich, engaging, and devoid of repetitive filler.

**Why this priority**: Ensuring high-quality manuscript generation directly fulfills the core value proposition of the writing platform.

**Independent Test**: Can be fully tested by initiating chapter generation and verifying that the resulting text exhibits varied sentence structures, authentic character voices, and active narrative drive without repetitive phrases.

**Acceptance Scenarios**:

1. **Given** a request to write a chapter, **When** the initial draft is evaluated and scores below the quality threshold, **Then** the assistant automatically performs targeted revisions on weak passages before delivering the text.
2. **Given** an AI revision pass, **When** the text is processed, **Then** the resulting prose shows demonstrable improvement in narrative flow and sensory depth without appending disconnected sentences.

---

### User Story 3 - Automated Anti-Slop Filtering (Priority: P3)

As a writer, I want the assistant to automatically identify and eliminate common AI writing clichés and repetitive structural patterns from my chapter drafts before I see them, preserving an authentic human voice.

**Why this priority**: Eliminating obvious AI tells prevents the prose from feeling robotic or generic.

**Independent Test**: Can be fully tested by inspecting generated chapters for known AI clichés and verifying their complete absence.

**Acceptance Scenarios**:

1. **Given** a newly revised chapter draft, **When** the text passes through the final filtering stage, **Then** all common AI filler phrases and repetitive paragraph structures are removed or replaced with natural prose.

### Edge Cases

- What happens when the AI service experiences high latency or temporary unavailability during the multi-pass revision loop? (System gracefully falls back to the best available draft and informs the user).
- How does the system handle ambiguous chat prompts that could be interpreted as either general conversation or a command to begin chapter generation? (System asks a clarifying question before initiating lengthy generation).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accurately classify incoming user chat messages to distinguish between general conversation, story research questions, and explicit chapter generation commands.
- **FR-002**: The system MUST provide context-aware, conversational responses to general chat and RAG queries without emitting manuscript draft prose.
- **FR-003**: The system MUST evaluate generated chapter drafts against a standardized multi-criteria storytelling rubric (including narrative drive, character voice, pacing, and sensory depth).
- **FR-004**: The system MUST execute an automated, intelligent revision loop targeting specific low-scoring passages when a draft falls below the required quality benchmark.
- **FR-005**: The system MUST filter out common AI writing clichés, repetitive adverbs, and formulaic paragraph structures prior to delivering the final prose to the user.

### Key Entities *(include if feature involves data)*

- **Chat Message**: Represents the user's input prompt, categorized by intent and associated confidence scores.
- **Quality Evaluation Rubric**: Represents the scoring criteria, weightings, and historical performance metrics for generated prose.
- **Manuscript Draft**: Represents the story content undergoing iterative evaluation, revision, and anti-slop filtering.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of general chat and RAG questions receive accurate, conversational responses without triggering unintended manuscript generation.
- **SC-002**: Generated chapters achieve an average quality evaluation score of 7.5 or higher across a standard 10-chapter benchmark test.
- **SC-003**: Zero occurrences of defined AI filler phrases (e.g., "delve into", "testament to", "he felt") appear in delivered chapter prose.
- **SC-004**: The automated revision loop successfully resolves identified prose deficiencies in 90% of cases within a maximum of 3 revision passes.

## Assumptions

- Users expect the AI assistant to maintain a clear distinction between conversational dialogue and formal manuscript generation.
- The underlying AI language model is capable of performing targeted, high-quality stylistic revisions when provided with specific critique prompts.
- Author preferences regarding automated anti-slop corrections can be configured or toggled within project settings.
