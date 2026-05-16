# Interface Contracts: Chat & Quality Engine API

**Feature**: True LLM Orchestration and Quality Engine
**Branch**: `002-fix-quality-engine`

## 1. POST `/api/chat` (Streaming Endpoint)

Handles conversational chat, RAG story Q&A, and chapter generation streaming requests.

### Request Payload (`ChatRequest`)
```json
{
  "message": "Write Chapter 1",
  "project_id": "default_project",
  "stream": true
}
```

### Response Format (Server-Sent Events - SSE)
When `stream` is `true`, the server responds with `Content-Type: text/event-stream`.

#### Stream Data Packets
```text
data: The 

data: dark 

data: night 

data: [DONE]
```

---

## 2. Quality Engine Internal Contract (`QualityEngine`)

Defines the core programmatic interface for evaluating and revising manuscript prose.

### `evaluate_prose(text: str) -> Tuple[float, Dict[str, float]]`
Evaluates the provided prose against the 8-criteria scoring rubric.

#### Parameters
- `text` (str): The manuscript text to evaluate.

#### Returns
- `overall_score` (float): The weighted composite score (0.0 to 10.0).
- `rubric_breakdown` (Dict[str, float]): A dictionary containing individual scores for each of the 8 criteria.

---

### `async revise_prose(text: str, target_score: float = 8.5, max_passes: int = 3) -> Tuple[str, float, int]`
Executes an internal AI revision loop (up to `max_passes`) to improve prose quality until `target_score` is achieved.

#### Parameters
- `text` (str): The initial draft text to revise.
- `target_score` (float): The desired quality benchmark score (default: 8.5).
- `max_passes` (int): Maximum number of revision iterations allowed (default: 3).

#### Returns
- `revised_text` (str): The fully revised manuscript prose.
- `final_score` (float): The final overall quality score achieved.
- `passes_used` (int): The number of revision iterations performed.
