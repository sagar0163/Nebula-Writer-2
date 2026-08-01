# SPEC: Nebula-Writer — Complete Novel Writing Assistant

## Vision
An AI-powered fiction writing assistant that takes a user from initial idea to finished novel, with persistent memory, real-time editing, comment-driven rewrites, direction changes, and improvisation support.

## Core User Journey
1. **Idea → Codex**: User describes concept → AI builds persistent Codex (entities, relationships, plot threads, tensions, anchors)
2. **Beat → Chapter**: User provides story beats → AI generates chapters with full Codex context
3. **Comment → Rewrite**: User highlights text + adds comment → AI rewrites per direction
4. **Direction Change**: User changes plot → Ripple checker identifies contradictions → User resolves
5. **Improvise**: User asks for alternatives → AI provides options (tone, POV, pacing, "what if" scenarios)

## Functional Requirements

### 1. Story Architect (Chat Interface)
- **FR-1.1**: Natural language idea ingestion → structured Codex creation
- **FR-1.2**: Context-aware Q&A about story state
- **FR-1.3**: Proactive suggestions (plot threads, character arcs, tension escalation)

### 2. Chapter/Scene Generation
- **FR-2.1**: Beat → full chapter via LangGraph pipeline (Plan → Write → Validate → Evaluate)
- **FR-2.2**: Scene-level generation with pacing/POV/tone controls
- **FR-2.3**: Version history with diff view and rollback

### 3. Comment-Driven Editing
- **FR-3.1**: Inline comments on generated prose (highlight + comment)
- **FR-3.3**: AI rewrite per comment (style, direction, fix, expand)
- **FR-3.3**: Accept/reject/revise workflow for AI suggestions

### 4. Direction Change & Continuity
- **FR-4.1**: Plot thread/tension/anchor management
- **FR-4.2**: Ripple checker: detects contradictions (entity state, timeline, location, knowledge)
- **FR-4.3**: "What breaks if I change X?" impact analysis

### 5. Improvisation Tools
- **FR-5.1**: Alternative generations (tone, POV, pacing, "what if")
- **FR-5.2**: Style mimicry from user's own writing
- **FR-5.3**: "Show don't tell", sensory expansion, dialogue polish

### 6. Persistence & Export
- **FR-6.1**: PostgreSQL (Supabase) for structured data
- **FR-6.2**: pgvector for semantic search over prose
- **FR-6.3**: Export: Markdown, DOCX, HTML, Mermaid graphs

## Non-Functional Requirements
- **NFR-1**: Sub-30s chapter generation (pipeline)
- **NFR-2**: Sub-5s scene generation (quick write)
- **NFR-3**: Zero hallucination of Codex facts
- **NFR-4**: <100ms comment rewrite latency

## Acceptance Criteria
- [ ] User can go from "I want a mystery about X" to 10 polished chapters
- [ ] User can highlight text, comment "make it darker", get rewrite
- [ ] User can say "Actually the killer is the brother" → system shows what breaks
- [ ] User can request 3 alternatives for any scene
- [ ] Export produces publishable manuscript

## Current Gaps (from audit)
| Gap | Priority |
|-----|----------|
| Ripple checker only checks entity existence, not plot logic | P0 |
| Comment system doesn't auto-rewrite | P0 |
| No "what if" / alternative generation | P1 |
| Style learner not integrated into pipeline | P1 |
| pgvector not configured (using ChromaDB fallback) | P1 |
| No timeline/location continuity checks | P1 |
| No manuscript-level export (DOCX/PDF) | P2 |

## Technical Approach
Use existing Nebula-Writer architecture:
- FastAPI + LangGraph pipeline (extend nodes)
- Supabase PostgreSQL + pgvector (migrate from ChromaDB)
- Vue.js frontend (extend comment UI, alternative picker)
- Mistral/Gemini/OpenAI via LangChain fallback chain
