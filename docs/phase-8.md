# Phase 8 — Next.js Frontend (All 4 Screens)
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

The complete dashboard UI — four screens that turn raw eval data into readable insights. A clean white-and-red design system, five reusable components, a typed API client, and a full Jest test suite. The frontend talks exclusively to the Phase 7 FastAPI backend through a single API module.

---

## Why this phase matters

The evaluation system is only useful if the results are visible. This phase makes every score, anomaly, and adversarial failure inspectable through a browser — no SQL queries, no script output, no manual file reading.

---

## What was built

### Types and API client
**File:** `frontend/lib/types.ts` — 8 TypeScript interfaces matching the Phase 7 API shapes exactly: `EvalResult`, `EvalListResponse`, `OverviewStats`, `CategoryStat`, `TrendPoint`, `AnomalyItem`, `AdversarialCategoryStat`, `AdversarialSummary`.

**File:** `frontend/lib/api.ts` — 8 typed async functions, all routing through a single `fetchJson<T>()` helper that reads `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`). Throws on non-OK responses. No `fetch()` anywhere else in the codebase.

### Components

**ScoreCard** (`frontend/components/ScoreCard.tsx`) — KPI card with title, large value, optional subtitle. Red text when `accent=true`.

**AnomalyBadge** (`frontend/components/AnomalyBadge.tsx`) — Red pill showing anomaly count. Gray "No anomalies" when count is 0.

**ScoreTrendChart** (`frontend/components/ScoreTrendChart.tsx`) — Recharts LineChart with red line, date x-axis, score 0–10 y-axis. Client component.

**CategoryBarChart** (`frontend/components/CategoryBarChart.tsx`) — Recharts horizontal BarChart with red bars, one bar per product category. Client component.

**AnswerTable** (`frontend/components/AnswerTable.tsx`) — Paginated table with columns for question, category, overall score, individual dimension scores, and anomaly flag. Rows expand to show the full Rufus answer. Previous/Next pagination. Client component.

### Pages

**Overview (`app/page.tsx`)** — Landing dashboard. 4 KPI ScoreCards (avg overall, avg helpfulness, avg hallucination, anomaly count), full-width ScoreTrendChart, CategoryBarChart with anomaly list alongside. Nav links to all other screens.

**Answer Feed (`app/feed/page.tsx`)** — Browseable feed of all eval results. Category dropdown and adversarial toggle filter the AnswerTable. Pagination at 20 per page.

**Weak Spot Analysis (`app/analysis/page.tsx`)** — CategoryBarChart showing avg score per category. Dimension breakdown table (helpfulness/accuracy/hallucination/safety per category). Bottom section shows the 10 worst-scoring answers.

**Adversarial Report (`app/adversarial/page.tsx`)** — 3 summary ScoreCards (total adversarial queries, failure rate, worst failure mode). CategoryBarChart of failure rates. Full breakdown table by failure mode. Export JSON button downloads the adversarial summary as a `.json` file.

---

## How data flows through this phase

1. Page component mounts with `useState` loading=true, data=null
2. `useEffect` calls the relevant `api.ts` function (e.g. `getOverviewStats()`)
3. `api.ts` calls `fetchJson()` which fetches from `NEXT_PUBLIC_API_URL/stats/overview`
4. Response typed as `OverviewStats`, stored in state
5. Component re-renders with data — ScoreCards, charts, tables populated
6. Empty states show when data arrays are empty; error states show on fetch failure

---

## Tests written

| Test file | Tests | What they check |
|-----------|-------|----------------|
| `ScoreCard.test.tsx` | 2 | Renders title+value; red colour on accent=true |
| `AnomalyBadge.test.tsx` | 2 | "No anomalies" at 0; count shown when >0 |
| `ScoreTrendChart.test.tsx` | 2 | Renders with empty data; renders with sample data |
| `CategoryBarChart.test.tsx` | 2 | Renders with empty data; renders with sample data |
| `AnswerTable.test.tsx` | 2 | Renders table headers; shows empty state when no data |

**Total: 17 tests passed, 0 failed**

### Build verification
`npm run build` — PASS. 4 routes compiled, TypeScript strict mode, zero errors.

---

## Checkpoint verification

- ✓ All 4 screens render without TypeScript errors (`npm run build` passes)
- ✓ All data fetched through `lib/api.ts` — no inline fetch
- ✓ Charts display correctly with real data
- ✓ Table pagination works
- ✓ Mobile responsive (Tailwind breakpoints applied)
- ✓ All components have Jest tests
- ✓ `docs/phase-8.md` generated

---

## Known limitations

Charts are client-side Recharts components — they require JavaScript enabled in the browser. Server-side rendering of charts is not supported by Recharts and is not required for this project. The `"use client"` directive on chart components handles this correctly.

---

## What comes next

Phase 9 is the final phase — a real eval run with `USE_MOCK=false` (live Anthropic API calls for 20 questions), deployment of the backend to Railway and the frontend to Vercel, and a final end-to-end verification with live data visible in the deployed dashboard.
