# Phase 0: Outline & Research

**Feature**: True LLM Orchestration and Quality Engine
**Branch**: `002-fix-quality-engine`

## Research Findings & Architectural Decisions

### 1. Chat Routing & Message Handling (`nebula_writer/main.py`)
- **Decision**: Modify `chat_with_ai` in `main.py` to extract the AI response using `raw_response.get("message")` instead of `raw_response.get("response")`.
- **Rationale**: The underlying `ConversationEngine.process_message` returns its generated text under the key `"message"`. Attempting to fetch `"response"` causes a silent fallback to the hardcoded default string `"Here is your generated chapter content."`, completely bypassing the actual conversation context.
- **Alternatives Considered**: Modifying `ConversationEngine` to return `"response"` instead of `"message"`. Rejected because `"message"` is the established standard across all intent handlers in `conversation.py`.

### 2. Authentic LLM Quality Revision Loop (`nebula_writer/quality_engine.py`)
- **Decision**: Replace the hardcoded string manipulation stubs in `QualityEngine.revise_prose()` with an authentic asynchronous LLM call (`AIWriter.generate()`).
- **Rationale**: The previous implementation literally hardcoded string appends (`current_text += " He darted across the shattered cobblestones..."`) to artificially inflate regex word counts and pass unit tests. Replacing this with an LLM prompt that includes the evaluation rubric breakdown ensures high-quality, context-aware prose revision.
- **Alternatives Considered**: Retaining regex heuristics but expanding the dictionary of replacement phrases. Rejected because regex cannot evaluate or improve true narrative rhythm, character voice, or thematic resonance.

### 3. Asynchronous Streaming Integration (`nebula_writer/main.py`)
- **Decision**: Retain the Server-Sent Events (SSE) generator pattern in `chat_with_ai`, but ensure it awaits the fully evaluated, revised, and anti-slop filtered prose before streaming token-by-token.
- **Rationale**: Providing real-time streaming feedback is critical for the author experience, but streaming must only begin after the multi-pass quality engine and anti-slop layer have completed their checks on the full draft.
- **Alternatives Considered**: Streaming intermediate revision passes to the client. Rejected because Section 5.4 of the Vision Document explicitly states: "The writer never sees the intermediate drafts or revision attempts."
