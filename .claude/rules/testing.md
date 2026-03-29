# Testing Rules — Rufus Eval Engine

## Backend (FastAPI / pytest)

- Test framework: `pytest` with `pytest-asyncio` for async routes
- HTTP client: `httpx.AsyncClient` with FastAPI's `app` as the transport — do not spin up a live server
- File structure mirrors source: `backend/tests/test_pipeline.py` tests `backend/evaluation/pipeline.py`
- Every route must have at least one happy-path test and one error/validation test
- Mock external calls (Anthropic API) using `unittest.mock.patch` or `pytest-mock` — never call the live API in tests
- Use `USE_MOCK=true` fixtures; load from `backend/data/mocks/` for consistent assertions
- Test naming: `test_<function>_<scenario>` (e.g. `test_run_eval_returns_scores`, `test_judge_handles_empty_answer`)
- Do not assert on floating-point scores directly — use `pytest.approx` or range checks

### Example pattern
```python
# tests/test_pipeline.py
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_run_eval_returns_four_scores():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/eval/run", json={"question_id": "q1"})
    assert response.status_code == 200
    data = response.json()
    assert set(data["scores"].keys()) == {"helpfulness", "accuracy", "hallucination", "safety"}
```

## Frontend (Next.js / Jest + React Testing Library)

- Test framework: Jest with `@testing-library/react` and `@testing-library/user-event`
- Unit test individual components in `frontend/__tests__/components/`
- Never test implementation details — test what the user sees and can interact with
- Mock all API calls from `lib/api.ts` using `jest.mock('../lib/api')`
- Recharts components can be shallow-rendered; skip visual snapshot tests for charts
- Test naming mirrors component: `ScoreCard.test.tsx` for `ScoreCard.tsx`

### Example pattern
```tsx
// __tests__/components/ScoreCard.test.tsx
import { render, screen } from '@testing-library/react'
import { ScoreCard } from '@/components/ScoreCard'

test('displays score and dimension label', () => {
  render(<ScoreCard dimension="helpfulness" score={8.5} />)
  expect(screen.getByText('helpfulness')).toBeInTheDocument()
  expect(screen.getByText('8.5')).toBeInTheDocument()
})
```

## General

- Tests must pass before any phase is marked complete
- Never skip tests with `pytest.mark.skip` or `test.skip` without a comment explaining why
- CI should run `pytest backend/tests/` and `npm test` in the frontend
