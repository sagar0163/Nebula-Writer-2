# Features Guide

## Core Features

### 1. Entity Management
Track characters, locations, and items in your story.

**Create Entity:**
```bash
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{"name": "Ravi", "entity_type": "character", "description": "Detective"}'
```

**Add Attributes:**
```bash
curl -X POST http://localhost:8000/api/attributes \
  -H "Content-Type: application/json" \
  -d '{"entity_id": 1, "key": "age", "value": "32"}'
```

### 2. Relationships
Connect entities with weighted relationships.

**Create Relationship:**
```bash
curl -X POST http://localhost:8000/api/relationships \
  -H "Content-Type: application/json" \
  -d '{"from_entity_id": 1, "to_entity_id": 2, "relationship_type": "loves", "strength": 0.9}'
```

**Strength** ranges from 0.0 to 1.0:
- 0.0-0.3: Weak relationship
- 0.4-0.6: Medium relationship
- 0.7-1.0: Strong relationship

### 3. Chapter Management
Organize your story into chapters.

**Create Chapter:**
```bash
curl -X POST http://localhost:8000/api/chapters \
  -H "Content-Type: application/json" \
  -d '{"number": 1, "title": "The Beginning", "content": "It was a dark night..."}'
```

**Update Chapter:**
```bash
curl -X PUT http://localhost:8000/api/chapters/1 \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content..."}'
```

### 4. Version History
Track changes to chapters.

**Save Version:**
```bash
curl -X POST http://localhost:8000/api/versions \
  -H "Content-Type: application/json" \
  -d '{"chapter_id": 1, "content": "Version 1 content..."}'
```

**View History:**
```bash
curl http://localhost:8000/api/chapters/1/versions
```

### 5. Story Templates
Use established story structures.

Available templates:
- **Three-Act Structure**: Setup → Confrontation → Resolution
- **Hero's Journey**: Departure → Initiation → Return
- **Save the Cat**: Beat-based story beats
- **Seven-Point Plot**: Hook/Pinch/Resolution
- **Snowflake Method**: Expand from summary

**Use Template:**
```bash
curl http://localhost:8000/api/templates
```

### 6. Consistency Checking
Find continuity issues.

**Run Check:**
```bash
curl -X POST http://localhost:8000/api/consistency/check
```

**View Issues:**
```bash
curl http://localhost:8000/api/consistency
```

**Resolve Issue:**
```bash
curl -X POST http://localhost:8000/api/consistency/1/resolve
```

### 7. Character Knowledge
Track what each character knows at different points.

**Update Knowledge:**
```bash
curl -X POST http://localhost:8000/api/character-knowledge \
  -H "Content-Type: application/json" \
  -d '{"entity_id": 1, "chapter_id": 5, "knowledge": "Ravi knows about the murder"}'
```

**Get Knowledge:**
```bash
curl "http://localhost:8000/api/character-knowledge/1?chapter_id=5"
```

### 8. AI Writing
Generate content with AI using story context.

**Write Scene:**
```bash
curl -X POST http://localhost:8000/api/ai/write \
  -H "Content-Type: application/json" \
  -d '{"beat": "The detective makes a discovery", "word_count": 500}'
```

**Rewrite Style:**
```bash
curl -X POST http://localhost:8000/api/ai/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text": "He was scared.", "style": "noir"}'
```

Available styles:
- `noir` - Dark, gritty
- `romantic` - Passionate, poetic
- `horror` - Dreadful, unsettling
- `humor` - Comedic, witty
- `thriller` - Fast-paced, suspenseful

### 9. Auto-Extract
Find entities mentioned in prose.

```bash
curl -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Ravi walked through Mumbai. Priya waited at the cafe."}'
```

### 10. Export
Export your story in multiple formats.

**Markdown:**
```bash
curl http://localhost:8000/api/export/markdown
```

**HTML:**
```bash
curl http://localhost:8000/api/export/html
```

**Plain Text:**
```bash
curl http://localhost:8000/api/export/text
```

**Mermaid Diagram:**
```bash
curl http://localhost:8000/api/export/mermaid
```

### 11. Multi-AI Provider
Use different AI models.

```bash
curl -X POST http://localhost:8000/api/ai/client \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "prompt": "Write a scene"}'
```

Available providers:
- `gemini` - Google Gemini (default)
- `openai` - OpenAI GPT-4
- `claude` - Anthropic Claude

### 12. Visualize
View relationship graphs.

```bash
curl http://localhost:8000/api/export/mermaid
```

Copy the output to [Mermaid Live Editor](https://mermaid.live) to visualize.

## Keyboard Shortcuts (Frontend)

- `+` button - Open add modal
- Click entity - View/edit
- Click chapter - Open editor
- Click template - View structure

## Tips

1. **Save often** - Version history lets you revert
2. **Use relationships** - AI uses them for context
3. **Add attributes** - More detail = better AI output
4. **Run consistency** - Catch issues early
5. **Export regularly** - Backup your work