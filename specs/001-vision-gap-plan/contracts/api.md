# Phase 1: API & WebSocket Interface Contracts

**Feature**: vision-gap-plan
**Date**: 2026-05-16

This document defines the formal REST API contracts and WebSocket protocols required to support the real-time streaming, targeted commenting, live synchronization, and multi-format export capabilities of Nebula Writer 2.

---

## 1. Real-Time Chapter Streaming Endpoint (Gap 1)

### `POST /api/chat`

Processes writer prompts, executes intent classification, performs internal quality evaluations, and streams chapter prose word by word to the client.

#### Request Headers
- `Content-Type`: `application/json`
- `Accept`: `text/event-stream`

#### Request Body (JSON)
```json
{
  "project_id": "uuid-string",
  "message": "Write the next scene where John confronts the council",
  "context_overrides": {}
}
```

#### Response Stream (`text/event-stream`)

##### Event: `action_started`
Fired when internal processing or quality evaluation commences.
```text
event: action_started
data: {"action": "Evaluating chapter draft against 8 quality criteria..."}

```

##### Event: `token`
Fired continuously as chapter prose words are generated.
```text
event: token
data: {"content": "The "}

event: token
data: {"content": "council "}

event: token
data: {"content": "chamber "}
```

##### Event: `lookahead_updated` (Addition 14)
Fired upon chapter approval/locking to deliver new forecasting cards.
```text
event: lookahead_updated
data: {"cards": [{"card_index": 0, "title": "The Trial", "scene_intention": "..."}]}

```

---

## 2. Targeted Inline Comment Endpoint (Gap 5)

### `POST /api/comments`

Creates a character-offset anchored comment and triggers an immediate asynchronous AI revision restricted solely to the highlighted span.

#### Request Headers
- `Content-Type`: `application/json`

#### Request Body (JSON)
```json
{
  "chapter_id": 42,
  "anchor_start": 1024,
  "anchor_end": 1150,
  "anchor_text": "The high inquisitor slammed his fist on the marble table.",
  "comment_text": "Make his reaction more subtle and chilling."
}
```

#### Response (JSON, `200 OK`)
```json
{
  "id": 108,
  "chapter_id": 42,
  "anchor_start": 1024,
  "anchor_end": 1150,
  "anchor_text": "The high inquisitor slammed his fist on the marble table.",
  "comment_text": "Make his reaction more subtle and chilling.",
  "ai_response": "Revised to: \"The high inquisitor went perfectly still, his fingers lightly tracing the grain of the marble table.\"",
  "revised_text": "The high inquisitor went perfectly still, his fingers lightly tracing the grain of the marble table.",
  "status": "ai_responded"
}
```

---

## 3. Multi-Format Export Endpoints (Gap 6)

### `GET /api/export/epub`

Generates and downloads the complete novel project as a validated EPUB 3.0 ebook.

#### Query Parameters
- `project_id` (string, required): The unique identifier of the novel project.

#### Response
- `Status`: `200 OK`
- `Content-Type`: `application/epub+zip`
- `Content-Disposition`: `attachment; filename=novel.epub`
- `Body`: Binary EPUB archive payload.

---

### `GET /api/export/docx`

Generates and downloads the complete novel project as a standard publishing manuscript Word document (Courier New, 12pt, double-spaced, 1-inch margins).

#### Query Parameters
- `project_id` (string, required): The unique identifier of the novel project.

#### Response
- `Status`: `200 OK`
- `Content-Type`: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `Content-Disposition`: `attachment; filename=manuscript.docx`
- `Body`: Binary DOCX document payload.

---

## 4. Live Codex Synchronization Protocol (Addition 16)

### `WebSocket /ws/sync/{project_id}`

Maintains a persistent, full-duplex connection between Studio Mode clients and the AI orchestrator to broadcast real-time story graph and entity updates.

#### Connection Handshake
- Client initiates WebSocket connection to `ws://host/ws/sync/{project_id}`.
- Server accepts connection and adds client to the project broadcast room.

#### Heartbeat Protocol
To prevent load balancers and firewalls from dropping idle connections, a bi-directional ping/pong heartbeat operates every 30 seconds.

##### Client Ping Payload
```json
{"type": "ping"}
```

##### Server Pong Payload
```json
{"type": "pong"}
```

#### Broadcast Event Payloads (Server-to-Client)

##### Event: `codex_entity_updated`
Fired when a character, setting, or lore attribute is modified in the background.
```json
{
  "type": "codex_entity_updated",
  "entity_type": "character",
  "entity_id": "char-789",
  "fields_changed": ["arc_current_state"]
}
```

##### Event: `compass_updated`
Fired when new open tensions or narrative momentums are calculated.
```json
{
  "type": "compass_updated",
  "component": "open_tensions",
  "new_count": 5
}
```

##### Event: `propagation_item_added`
Fired when an entity edit introduces a potential downstream narrative contradiction.
```json
{
  "type": "propagation_item_added",
  "item": {
    "entity_id": "char-789",
    "description": "Character desire changed to pacifism, conflicting with Chapter 12 battle scene."
  }
}
```
