# Nebula-Writer Strategy — The Core Differentiated Experience

> **One line:** Nebula-Writer is the AI co-author that never forgets your story.
>
> Status: Ratified (Issue #146) · Source of truth for product direction · Overrides README/SPEC framing where they conflict

---

## 1. Executive Summary

Nebula-Writer is not "a unified writing workspace," "a content generator," or "a multi-model LLM router." Those framings try to be everything to everyone and collapse under first-principles scrutiny. This document cuts through the noise.

### The single core experience

> **The Canon-Safe Co-Writing Loop** — from a one-line idea to a finished, internally-consistent novel, every interaction flows through a living story canon (the Codex) that the AI maintains *for* the writer, not the writer for the AI.

Concretely: the writer describes an idea, Nebula-Writer builds a persistent story canon (characters, relationships, plot threads, world rules, timeline). Every chapter it writes, every targeted rewrite it drafts, and every direction-change the writer makes is validated against that canon — with ripple detection that surfaces exactly what breaks and rewrites only what needs to change.

**The single proof moment that no competitor delivers**: a writer says *"Actually, the killer is the brother"* and Nebula-Writer shows precisely what now contradicts (earlier scenes, character knowledge, plot threads) and rewrites the affected prose so the whole manuscript stays consistent — without the writer manually updating a story bible.

That loop is the product. Nothing else matters until it works perfectly.

---

## 2. First-Principles Reasoning

### 2.1 Why this, and not the alternatives

We applied the discipline: *name the job-to-be-done, not the features.*

| Candidate core experience | Why it is NOT the core |
|---|---|
| "Chat that writes chapters" | ChatGPT, Sudowrite, Claude already do this. No moat. |
| "Multi-model router / best model" | A technical property, not an experience. Table stakes. |
| "Document analysis & content generation" | Generic; competes with every AI writing tool. Not differentiated. |
| "Story bible / Codex CRUD" | A tool, not an outcome. The writer still does the librarian work. |
| "Export to manuscript formats" | A finish-line convenience. Needed eventually, never a reason to switch. |
| **"Canon-safe co-writing"** | **Solves the #1 writer pain — continuity — that none of the above solve end-to-end. This is the moat.** |

### 2.2 The writer's real pain

Professional and serious amateur writers already have plenty of tools that produce *nice prose*. What they do **not** have is a tool that:

1. Remembers every established fact across a 90k-word manuscript without being told twice.
2. Keeps character knowledge, timeline, relationships, and world rules consistent **automatically**.
3. Lets them change their mind late in the draft **without** re-reading three hundred pages to fix contradictions by hand.

That is where novel-writing hours die. That is the job Nebula-Writer exists to do — and it is the one job Chat-GPT, Sudowrite, and Novelcrafter leave on the table.

### 2.3 Why the Codex is the moat, not the UI

Any competitor can copy a chat UI or a commenting UI. The hard moat is **state**: a machine-maintained, growing canon that is authoritative enough that generated prose is canon-correct by construction, and that can answer "what breaks if I change X?" across an entire manuscript. The longer a writer's project lives in Nebula-Writer, the deeper their canon becomes, and the more painful it is to leave. That is a compounding, switch-cost moat — not a feature people can clone in a sprint.

---

## 3. The Core Experience, Specified

### 3.1 The loop

```
  Idea ──► Codex         canonical state built from a one-line description
   │                      (characters, relationships, plot threads,
   │                       world rules, timeline, knowledge per chapter)
   ▼
  Chapters ──► Write       prose generated from beats, grounded in Codex
   │
   ▼
  Comment ──► Rewrite      highlight + comment → minimum-change targeted rewrite
   │
   ▼
  Pivot ──► Ripple         "what breaks if I change X?" → surface contradictions
   │                        → resolve → propagate fixes
   ▼
  Export ──► Manuscript    finished, consistent novel → publishable formats
```

Five steps. Each one feeds the same canon. Features that don't serve at least one of these five steps are noise until the core is flawless.

### 3.2 Success definition (the "perfect" bar)

The loop is done perfectly when a writer can go from *"a mystery set in Mumbai"* to a 100k-word manuscript where:

- **Zero hallucinated canon**: the AI never invents a fact contradicting the Codex (NFR-3 in SPEC.md).
- **Ripple is a superpower**: any direction change produces an explicit, trustworthy breakdown of affected scenes — and a one-click path to rewrite just those.
- **Targeted rewrite is surgical**: a comment rewrites the selected span and *only* the selected span (Minimum Change Principle), then re-checks the canon.
- **The writer never does librarian work**: story-bible maintenance is automatic, silent, and invisible until there's a decision to make.

### 3.3 The single proof moment (what we demo to a skeptic)

> "Actually, the killer is the brother."

If that one interaction is jaw-dropping — the writer sees the affected chapters, the contradictory knowledge-carrying scenes, the alternatives, and the ripple-safe rewrite — Nebula-Writer has differentiated. If that interaction is mediocre, nothing else in the product matters.

---

## 4. Noise Inventory — What Is NOT Core

Everything below **must not** be marketed, prioritized, or invested in before the core loop is flawless. They are either supporting infrastructure, phase-later enhancements, or future bets. Marked accordingly.

### 4.1 Supporting (build, but never lead with)

These exist in the codebase today and serve the loop, but are **not** the pitch:

| Item | Role today | Decision |
|---|---|---|
| Multi-provider model router (Mistral/Gemini/OpenAI/Ollama/NVIDIA) | Backend fallback chain for availability & cost | Keep as infrastructure. **Not a selling point.** Ship with sensible default; never market "N models." |
| Quality engine / anti-slop scrubber | Raises floor on generated prose | Keep — it makes the loop output good. **Not the differentiator.** |
| Real-time SSE streaming | Perceived latency | Keep. Nice but table stakes; polish in Phase 2. |

### 4.2 Phase 2 (core-depth, after Phase 1 is perfect)

| Item | Notes |
|---|---|
| Studio Mode / lookahead cards / live Codex sync | Deepens the loop UX but is *over* the same canon. Build on a working core. |
| Style learner / mimic author voice | Powerful, but secondary to "never contradicts the canon." |
| Templates (Three-Act, Hero's Journey, Save the Cat...) | Onboarding accelerators. Useful, not differentiating. |
| Timeline & location continuity depth | Absorbed into ripple checker quality. |
| Rich Studio visualizations (Mermaid, arcs) | Delight, not core. |

### 4.3 Phase 3 (breadth — after the loop is genuinely loved)

| Item | Notes |
|---|---|
| Publication-grade export (EPUB, DOCX, PDF) | Finish-line. Needed for the "finished novel" promise, but never a reason someone chooses us. |
| Web research engine / citations | Adjacent to fiction writing; defer. |
| Semantic search / RAG polish | Infrastructure, defer. |
| Collaboration / beta-reader system | Different product; defer. |
| Mobile app | Defer. |
| Plugin system / SDK | Ecosystem bet; only after traction. |

### 4.4 Explicitly NOT the product (stop mentioning in docs/pitch)

- "Unified writing workspace"
- "Document intelligence / analysis"
- "Content generation for articles, reports, emails"
- "Multi-model leaderboard" style positioning

These are the noise. The README currently leads with them; per this document, README/SPEC must lead with the Canon-Safe Co-Writing Loop instead.

---

## 5. Core-First Roadmap

### Phase 1 — "The Loop Works" (now → next milestone)

Make the five-step loop undeniable end-to-end. Priority order:

1. **Beat → canon-correct chapter** (pipeline grounded in full Codex context; zero canon hallucination enforced by post-write validation)
2. **Comment → surgical targeted rewrite** (anchor to span, Minimum Change, accept/reject)
3. **Pivot → ripple analysis** ("what breaks if I change X" with trustworthy impact list)
4. **Ripple → resolution loop** (rewrite affected scenes atomically, re-validate)
5. **Idea → Codex** (from a one-liner or a pitch to a usable first canon)
6. **Export** (basic MD/plain-text manuscript so the story leaves cleanly)

**Gate for Phase 1 exit:** the proof moment in §3.3 demonstrably works on a 10+ chapter manuscript with a skeptical user saying "show me what breaks." Anything not in service of that gate is deferred.

### Phase 2 — "The Loop Feels Like Magic"

Make the core loop feel effortless and fast:

- Streaming polish + <500ms first token
- Studio Mode + live Codex sync + lookahead cards over the same canon
- Ripple intelligence depth (timeline, location, knowledge-per-chapter, foreshadowing)
- Style learner integrated into rewrite suggestions
- Templates as onboarding accelerators

### Phase 3 — "The Loop Ships Novels"

Finish the edges so the promise is complete:

- Publication-grade EPUB/DOCX/PDF export (manuscript formatting)
- Web research engine with citations (opt-in, not core)
- Collaboration / beta-reader / plugins — only after demonstrated traction

---

## 6. Decision Guardrails

Every feature request, integration, or architectural proposal is evaluated with one question:

> **"Does this make the Canon-Safe Co-Writing Loop more undeniable?"**

- **YES** → it is core. Prioritize it.
- **Indirectly** (e.g., streaming, quality engine, export) → supporting. Build it, but never lead with it.
- **NO / only marketing** (e.g., "more models," "document analysis") → defer or cut. This is the noise we are disciplined about.

---

## 7. Team Alignment

- **Engineers**: when a ticket doesn't trace to a loop step (§3.1) or the proof moment (§3.3), push back — it's phase-later.
- **Docs/README**: position with the Canon-Safe Co-Writing Loop; remove "workspace / content generation" framing.
- **Roadmap/planning**: Phase 1 is the only thing that exists until the Phase 1 gate passes.
- **Team definition of done for differentiation**: a writer can change a core plot fact late in a draft, see what breaks, and land a consistent manuscript — faster than they can by hand.

---

*Ratified via Issue #146 — War Room. This document is the single source of truth for product direction; where it conflicts with SPEC.md / BRD.md / README.md, this document wins.*