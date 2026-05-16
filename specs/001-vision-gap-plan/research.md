# Phase 0: Research & Architecture Decisions

**Feature**: vision-gap-plan
**Date**: 2026-05-16

## Executive Summary

Following a comprehensive audit of the Nebula Writer 2 codebase, the architectural gap between the existing implementation and the complete vision has been distilled into six core backend/frontend enhancements and five foundational feature additions. This document consolidates the technical research, architectural decisions, and design rationales required to implement these capabilities while preserving the stability of the core engine layer.

---

## Decision 1: Server-Sent Events (SSE) for Chapter Streaming

### Decision
Implement Server-Sent Events (SSE) via FastAPI's `StreamingResponse` for real-time chapter generation streaming at the `/api/chat` endpoint.

### Rationale
- **Unidirectional Efficiency**: Chapter generation is fundamentally a server-to-client streaming process. SSE operates over standard HTTP/1.1 and HTTP/2, leveraging built-in browser connection management, automatic reconnection, and firewall compatibility.
- **Simplicity & Performance**: Avoids the framing overhead and complex state management of WebSockets for simple text streaming, allowing tokens to render in the chat interface word by word with sub-second initial latency.

### Alternatives Considered
- **WebSockets**: Rejected for chapter streaming due to unnecessary bi-directional overhead, though adopted separately for Studio Mode live codex synchronization.
- **Long Polling / Chunked JSON**: Rejected due to high latency, poor user experience, and awkward client-side parsing.

---

## Decision 2: Hybrid Intent Classification Engine

### Decision
Adopt a two-tier hybrid intent classification architecture in `conversation.py`, combining a high-speed regular expression fast-path with an LLM-powered natural language fallback.

### Rationale
- **Optimal Latency & Cost**: Exact structural commands (e.g., `/new`, `/write 1000 words`) match regex patterns in <1ms with zero API cost. 
- **Nuanced Understanding**: Complex conversational requests (e.g., "Weave a subtle hint about the pendant into the dialogue") fallback to a fast, economical LLM call to extract intent, entities, and confidence scores.

### Alternatives Considered
- **Pure LLM Classification**: Rejected due to unnecessary latency and API costs for standard, predictable writer commands.
- **Pure Regex / Heuristics**: Rejected as too fragile and rigid for an intuitive, conversational AI co-writer.

---

## Decision 3: Automated Multi-Dimensional Quality Gate

### Decision
Create a dedicated evaluation loop (`nebula_writer/quality_engine.py`) that executes an automated 8-criteria scoring rubric on chapter drafts prior to streaming.

### Rationale
- **Autonomous Curation**: Evaluates drafts across Narrative Drive (20%), Show Don't Tell (15%), Character Voice (20%), Pacing (15%), Dialogue Naturalism (10%), World Consistency (10%), Tropes (5%), and Formatting (5%).
- **Self-Correction**: Drafts scoring below the quality threshold trigger targeted internal AI revisions (up to 3 passes), ensuring the writer never sees unpolished or substandard prose.

### Alternatives Considered
- **Single-Pass Generation**: Rejected as it places the entire burden of quality control and initial editing on the human writer.

---

## Decision 4: Programmatic Anti-Slop Filtering

### Decision
Implement an automated stylistic post-processor (`nebula_writer/anti_slop.py`) to detect and rectify overused AI cliches, repetitive cadences, and stylistic flattening.

### Rationale
- **Preserving Literary Quality**: Programmatically flags and replaces generic AI hallmarks (e.g., "shivers down the spine", "tapestry of lies", "testament to") and structural monotony (e.g., consecutive paragraphs starting with participial phrases).
- **Mode-Specific Behavior**: Operates silently in Chat Mode to ensure seamless prose delivery, while displaying transparent diagnostic flags in Studio Mode.

### Alternatives Considered
- **Negative Prompting**: Rejected as standalone negative prompts are notoriously unreliable at suppressing latent LLM stylistic biases over long token horizons.

---

## Decision 5: Minimum Change Principle for Inline Comments

### Decision
Extend `comment_system.py` and the Vue.js frontend to support character-offset anchored comments (`anchor_start`, `anchor_end`, `anchor_text`) with targeted AI revisions restricted strictly to the highlighted span.

### Rationale
- **Surgical Precision**: Authors require the ability to adjust specific sentences or paragraphs without the AI altering surrounding text or disrupting established rhythm.
- **Ripple Validation**: Confining revisions to the exact anchor span allows the system to execute subsequent `ripple_checker.py` evaluations to detect downstream narrative impacts safely.

### Alternatives Considered
- **Full Chapter Regeneration**: Rejected as destructive to authorial intent and violative of the Minimum Change Principle.

---

## Decision 6: Multi-Format Manuscript Export Ecosystem

### Decision
Integrate industry-standard document generation libraries in `exporter.py`: `ebooklib` for EPUB 3.0, `python-docx` for professional manuscript Word documents, and `weasyprint` for print-ready trade paperback PDFs.

### Rationale
- **Publishing-Grade Output**: 
  - `ebooklib` provides deep structural control over NCX/NAV navigation tables and XHTML formatting required to pass official `epubcheck` validation.
  - `python-docx` enables exact typographic styling (Courier New, 12pt, double-spaced, 1-inch margins, running headers) mandated by traditional publishing houses.
  - `weasyprint` leverages CSS Paged Media to produce flawless, print-ready PDF typography.

### Alternatives Considered
- **Basic HTML/Markdown Conversion**: Rejected as amateurish and unacceptable for professional authors preparing for commercial publication.

---

## Decision 7: WebSocket Live Codex Synchronization

### Decision
Establish a dedicated WebSocket connection manager (`/ws/sync/{project_id}`) in `main.py` to broadcast real-time story graph updates from `orchestrator.py` to connected Studio Mode clients.

### Rationale
- **Seamless Studio Experience**: When the AI orchestrator updates character arcs, tension states, or lookahead proposals in the background following a chapter approval, Studio Mode updates instantly without requiring a manual page refresh.
- **Robustness**: Incorporates a 30-second heartbeat ping/pong mechanism and automatic client-side reconnection to handle intermittent network drops gracefully.

### Alternatives Considered
- **Client-Side Polling**: Rejected due to unnecessary server load, database pressure, and noticeable UI synchronization lag.
