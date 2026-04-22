# BRD Gap Analysis: Nebula-Writer vs AutoNovelist

## Source Document
- **File:** `docs/AutoNovelist_BRD.docx`
- **Product:** AutoNovelist - AI-Powered Novel Writing Platform
- **Version:** 1.0 (Draft, April 21, 2026)

---

## What Was Planned (BRD) vs What Was Built

### FR-01: Idea Intake & Project Initialization
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Accept single-sentence idea | Required | ❌ Not built |
| Infer genre, tone, target audience | Required | ❌ No inference |
| Generate draft title and tagline | Required | ❌ Not built |
| Propose story structure | Required | ✅ Templates exist |
| Suggest chapter count | Required | ❌ Not built |
| Research agenda | Required | ❌ Not built |

### FR-02: Internet Research Engine
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Autonomous web searches | Required | ❌ Not built |
| Source citation storage | Required | ❌ Not built |
| Research linked to entities | Required | ❌ Not built |
| Searchable by AI | Required | ❌ Not built |

### FR-03: Story Bible
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Characters with arc status | Required | ⚠️ Partial |
| Locations with scenes | Required | ✅ Basic |
| Timeline event log | Required | ⚠️ Basic events |
| World Rules | Required | ❌ Not built |
| Plot Threads tracking | Required | ❌ Not built |
| Research citations | Required | ❌ Not built |

### FR-04: Character Deep Mapping
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Full identity fields | Required | ⚠️ Basic |
| Big Five personality traits | Required | ❌ Not built |
| Backstory | Required | ⚠️ In description |
| Voice profile | Required | ❌ Not built |
| Arc tracking | Required | ⚠️ Basic |
| Continuity flags per chapter | Required | ⚠️ character_knowledge table |

### FR-05: Location & World-Building
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Spatial map | Required | ❌ Not built |
| Sensory palette | Required | ❌ Not built |
| History and lore | Required | ⚠️ In description |
| Mood tags | Required | ❌ Not built |

### FR-06: Chapter Generation Engine
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Pre-generation context load | Required | ⚠️ Basic |
| Word count control (1500-5000) | Required | ✅ Basic |
| Pacing mode | Required | ❌ Not built |
| POV selection | Required | ❌ Not built |
| Tone selection | Required | ✅ Style rewrite |
| Post-generation update | Required | ❌ Not automated |

### FR-07: Continuity & Consistency
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Character fact check | Required | ⚠️ Basic |
| Timeline paradox detection | Required | ⚠️ Basic |
| World rule violations | Required | ❌ Not built |
| Location contradictions | Required | ❌ Not built |
| Foreshadowing tracker | Required | ❌ Not built |

### FR-08: User Editing
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| Inline editing | Required | ❌ Not built |
| Annotations | Required | ❌ Not built |
| Manual overrides | Required | ⚠️ CRUD exists |
| Regenerate with changes | Required | ❌ Not built |
| Style capture | Required | ❌ Not built |

### FR-09: Export
| Requirement | Status in BRD | Built? |
|-------------|---------------|--------|
| EPUB export | Required | ⚠️ Basic skeleton |
| DOCX export | Required | ⚠️ RTF format |
| PDF export | Required | ❌ Not built |
| Story Bible export | Required | ⚠️ JSON |
| Chapter-by-chapter | Required | ✅ Manual |
| Manuscript formatting | Required | ❌ Not built |

---

## Missing Features Summary

### Critical (Not Built)
1. **Internet Research Engine** - No web search integration
2. **Plot Threads tracking** - No tracking of open storylines
3. **Foreshadowing tracker** - No plant/payoff tracking
4. **Voice Profile generation** - No character speech patterns
5. **Pacing/Tone/POV controls** - Limited generation control
6. **Style capture from edits** - AI doesn't learn from user
7. **Spatial mapping** - No visual location maps
8. **PDF export** - Not built

### Medium Priority
1. Idea-to-blueprint inference (AI parsing)
2. Research agenda generation
3. World Rules storage
4. Continuity Checker (full)
5. Manuscript formatting

### Nice to Have
1. Vision statement in UI
2. Research citations display
3. Character arc visualization
4. Mood/atmosphere tags

---

## Architecture Gaps

| BRD Architecture | Built Architecture |
|-----------------|------------------|
| Neo4j graph database | SQLite |
| 6 subsystems | 3 modules |
| Research engine | ChromaDB only |
| Web search API | No |
| Style capture | No |
| Plot thread manager | No |
| Foreshadowing tracker | No |

---

## Recommendations

### Phase 1 Priority (Quick Wins)
1. Add idea parsing → auto-generate template selection
2. Expand entity fields (personality, backstory, voice)
3. Add timeline visualization
4. Build simple plot thread tracker

### Phase 2 (Medium Effort)
1. Integrate web search (SerpAPI or similar)
2. Add research citation storage
3. Build continuity checker
4. Add POV/pacing controls to generation

### Phase 3 (Full Vision)
1. Switch to graph database (Neo4j or similar)
2. Build research engine
3. Add style capture
4. Full foreshadowing tracking
5. EPUB/PDF export

---

*Analysis Date: 2026-04-21*
*Gap: ~60% of BRD requirements not built*