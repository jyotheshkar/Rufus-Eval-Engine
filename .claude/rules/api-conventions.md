# API Conventions — Rufus Eval Engine

## FastAPI Route Patterns

- All routes use `async def`
- Group routes by domain using `APIRouter` — one router per module, mounted in `main.py`
- Route paths use `kebab-case` (e.g. `/eval/run`, `/eval/results`, `/adversarial/run`)
- Always declare a `response_model` on every route
- Return HTTP 422 automatically via Pydantic validation — do not write manual validation for body fields

```python
# backend/routes/eval.py
from fastapi import APIRouter, HTTPException
from backend.models import RunEvalRequest, EvalResult

router = APIRouter(prefix="/eval", tags=["eval"])

@router.post("/run", response_model=EvalResult)
async def run_eval(request: RunEvalRequest) -> EvalResult:
    try:
        result = await pipeline.run(request.question_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Eval pipeline failed")
```

## Pydantic Models

- All request and response bodies are Pydantic `BaseModel` subclasses
- Define models in `backend/models.py` (or a `models/` package for larger groupings)
- Use `Field()` with a `description` for every field — this auto-generates OpenAPI docs
- Use `model_validator` or `field_validator` for cross-field business rules
- Scores are always `float` in range 0–10; use `Field(ge=0, le=10)` to enforce

```python
# backend/models.py
from pydantic import BaseModel, Field

class EvalScores(BaseModel):
    helpfulness: float = Field(..., ge=0, le=10, description="How well the answer addressed the question")
    accuracy: float = Field(..., ge=0, le=10, description="Factual correctness of product information")
    hallucination: float = Field(..., ge=0, le=10, description="Absence of invented facts (10 = no hallucination)")
    safety: float = Field(..., ge=0, le=10, description="No misleading or pressuring language")

class EvalResult(BaseModel):
    id: str = Field(..., description="Unique eval run ID")
    question_id: str
    answer: str
    scores: EvalScores
    anomaly_flagged: bool
    created_at: str
```

## Response Shapes

All endpoints return one of three shapes:

### Success (single object)
```json
{
  "id": "eval_abc123",
  "question_id": "q1",
  "answer": "...",
  "scores": { "helpfulness": 8.5, "accuracy": 9.0, "hallucination": 9.5, "safety": 10.0 },
  "anomaly_flagged": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Success (list)
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### Error
```json
{
  "detail": "Human-readable error message"
}
```
FastAPI uses `detail` automatically for `HTTPException` — match this shape for consistency.

## Environment & Mock Guard

- All LLM calls must check `USE_MOCK` before hitting the Anthropic API:
```python
import os

async def call_llm(prompt: str) -> str:
    if os.getenv("USE_MOCK", "true").lower() == "true":
        return load_mock_response(prompt)
    return await anthropic_client.messages.create(...)
```
- Mock responses live in `backend/data/mocks/`
- Never remove the mock guard without explicit user instruction ("run live")

## CORS

- In development, allow `http://localhost:3000` (Next.js dev server)
- Configure in `main.py` via `CORSMiddleware` — do not use a wildcard `*` in production
