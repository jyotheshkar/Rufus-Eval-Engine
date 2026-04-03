# Phase 8 — Next.js Frontend (All 4 Screens)

## Goal
Build the dashboard. Four screens, clean black/white aesthetic with red accents,
all data fetched from the FastAPI backend. Recharts for all visualisations.

---

## Design system

| Token | Value | Tailwind class |
|-------|-------|----------------|
| Background | #FFFFFF | bg-white |
| Primary text | #111111 | text-gray-900 |
| Accent | #DC2626 | text-red-600 / bg-red-600 |
| Secondary | #6B7280 | text-gray-500 |
| Border | #E5E7EB | border-gray-200 |
| Font | Inter (system) | font-sans |

All charts: `#DC2626` primary line, `#111111` secondary, `#6B7280` tertiary.

---

## Step 1 — Build lib/api.ts

All fetch calls in one place. Never `fetch()` directly in components.

```typescript
// All API calls for the Rufus Eval Engine dashboard
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getOverview(): Promise<OverviewStats> { ... }
export async function getEvals(params: EvalParams): Promise<EvalListResponse> { ... }
export async function getEvalById(id: string): Promise<EvalResult> { ... }
export async function getStatsByCategory(): Promise<CategoryStat[]> { ... }
export async function getScoreTrend(days: number): Promise<TrendPoint[]> { ... }
export async function getAnomalies(): Promise<Anomaly[]> { ... }
export async function getAdversarialSummary(): Promise<AdversarialSummary> { ... }
```

Define all TypeScript interfaces in `frontend/lib/types.ts`.

---

## Step 2 — Build shared components

All components use named exports. Components with hooks require `"use client"`.
All components handle loading and error states.

### ScoreCard.tsx
```
┌─────────────────┐
│  Avg Score      │
│  7.4 / 10      │
│  ▲ +0.3 today  │
└─────────────────┘
```
Props: `{ title: string; value: number; subtitle?: string; trend?: number }`

### AnomalyBadge.tsx
Red pill badge: "12 anomalies detected"
Props: `{ count: number }`

### ScoreTrendChart.tsx
Line chart. X: date, Y: score 0-10. Red line.
Props: `{ data: TrendPoint[] }`

### CategoryBarChart.tsx
Horizontal bar chart. Each bar = one category.
Props: `{ data: CategoryStat[] }`

### AnswerTable.tsx
Columns: question, category, overall score, dimension scores, anomaly flag.
Expandable row: full Rufus answer + judge reasoning.
Props: `{ evals: EvalResult[]; page: number; total: number; onPageChange: (p: number) => void }`

---

## Step 3 — Build Overview screen (app/page.tsx)

```
Row 1: 4 KPI ScoreCards (avg overall, avg helpfulness, avg accuracy, anomaly count)
Row 2: ScoreTrendChart — full width
Row 3: CategoryBarChart (left 60%) + Recent anomalies list (right 40%)
```

Data: `getOverview()` + `getScoreTrend(7)` + `getStatsByCategory()`

---

## Step 4 — Build Answer Feed (app/feed/page.tsx)

```
Filter bar: category dropdown | difficulty dropdown | score range slider | adversarial toggle
AnswerTable: paginated, 20 per page, expandable rows
```

---

## Step 5 — Build Weak Spot Analysis (app/analysis/page.tsx)

```
Row 1: CategoryBarChart — avg score per category
Row 2: Dimension comparison table (avg helpfulness/accuracy/hallucination/safety per category)
Row 3: Worst 10 answers table (lowest overall score)
```

---

## Step 6 — Build Adversarial Report (app/adversarial/page.tsx)

```
Row 1: Summary ScoreCards (total adversarial, failure rate %, worst failure mode)
Row 2: Failure mode breakdown bar chart
Row 3: Adversarial results table, filterable by failure mode
Row 4: Export button → downloads results as JSON
```

---

## Phase 8 complete when:
- All 4 screens render without TypeScript errors (`npm run build` passes)
- All data fetched through `lib/api.ts` — no inline fetch
- Charts display correctly with real data
- Table pagination works
- Mobile responsive (Tailwind breakpoints applied)
- All components have Jest tests
- `docs/phase-8.md` generated
