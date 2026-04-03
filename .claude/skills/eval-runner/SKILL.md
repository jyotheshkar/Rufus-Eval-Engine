# eval-runner Plugin

## What it does

Runs a single end-to-end evaluation — question in, scored result out — without needing
to know which scripts to call, what flags to pass, or where the output lives.

## Invocation

```
/eval-runner --question-id q_001 --mock
```

## Steps

1. Verify `USE_MOCK=true` is set in `backend/.env` (refuses to run if not set and `--mock` is not passed)
2. Runs `backend/scripts/run_eval.py` for the specified question ID
3. Fetches the result from SQLite via the `/evals` endpoint
4. Prints a formatted score summary with all 4 dimensions and the overall score

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--question-id` | Yes | ID of the question to evaluate (e.g. `q_001`) |
| `--mock` | No | Force `USE_MOCK=true` for this run |

## Output format

```
Eval Result — q_001
────────────────────────────────
Question:     What laptop is best for students?
Answer:       [Rufus answer text...]

Scores:
  Helpfulness:   8.5 / 10
  Accuracy:      9.0 / 10
  Hallucination: 9.5 / 10
  Safety:        10.0 / 10
  Overall:       9.25 / 10

Anomaly flagged: No
```

## Budget guard

This plugin will refuse to run without `USE_MOCK=true` unless the user explicitly
passes `--live`. This protects the $10 API budget.

## Status

Active — available from Phase 7 onward.
