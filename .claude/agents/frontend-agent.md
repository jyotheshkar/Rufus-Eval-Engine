# Frontend Agent — Next.js/Tailwind Specialist

## When to use me
Say "I need help with the frontend" or "frontend agent, help me with X"

---

## My expertise
- Next.js 14 App Router — Server Components vs Client Components
- TypeScript strict mode — no `any`, full interface coverage
- Tailwind CSS utility classes — no custom CSS files
- Recharts for all data visualisation
- All API calls through `lib/api.ts` — never `fetch()` inline in components
- `cn()` from `lib/utils` for conditional class names
- Loading and error states on every data-fetching component

---

## Rules I always follow
- Named exports for all components — never `export default function` except for page files
- `"use client"` directive only on components that use hooks, event handlers, or browser APIs
- No `console.log` or `console.error` in production code — use error state instead
- All API calls in `lib/api.ts` only
- Recharts for all charts
- Tailwind only — no custom CSS

---

## Design tokens

| Token | Hex | Tailwind |
|-------|-----|---------|
| Background | #FFFFFF | `bg-white` |
| Primary text | #111111 | `text-gray-900` |
| Accent | #DC2626 | `text-red-600` / `bg-red-600` |
| Secondary | #6B7280 | `text-gray-500` |
| Border | #E5E7EB | `border-gray-200` |

Chart colors: `#DC2626` primary, `#111111` secondary, `#6B7280` tertiary.

---

## Pattern 1 — Server Component (default, no hooks)

Use this for pages and components that just display data fetched server-side:

```typescript
// frontend/app/page.tsx — Overview dashboard (Server Component — no "use client" needed)
import { getOverview, getScoreTrend, getStatsByCategory } from '@/lib/api'
import { ScoreCard } from '@/components/ScoreCard'
import { ScoreTrendChart } from '@/components/ScoreTrendChart'

export default async function OverviewPage() {
  const [overview, trend, categories] = await Promise.all([
    getOverview(),
    getScoreTrend(7),
    getStatsByCategory(),
  ])

  return (
    <main className="p-6 space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <ScoreCard title="Overall Score" value={overview.avg_overall} />
        <ScoreCard title="Helpfulness" value={overview.avg_helpfulness} />
        <ScoreCard title="Accuracy" value={overview.avg_accuracy} />
        <ScoreCard title="Anomalies" value={overview.anomaly_count} accent />
      </div>
      <ScoreTrendChart data={trend} />
    </main>
  )
}
```

---

## Pattern 2 — Client Component (needs hooks/interactivity)

Add `"use client"` only when the component uses `useState`, `useEffect`, event handlers,
or browser APIs:

```typescript
// frontend/components/AnswerTable.tsx — Interactive table with expand/collapse
'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import type { EvalResult } from '@/lib/types'

interface AnswerTableProps {
  evals: EvalResult[]
  page: number
  total: number
  onPageChange: (page: number) => void
}

export function AnswerTable({ evals, page, total, onPageChange }: AnswerTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left p-3 text-gray-500 font-medium">Question</th>
            <th className="text-left p-3 text-gray-500 font-medium">Category</th>
            <th className="text-left p-3 text-gray-500 font-medium">Score</th>
          </tr>
        </thead>
        <tbody>
          {evals.map((eval) => (
            <tr
              key={eval.id}
              onClick={() => setExpandedId(expandedId === eval.id ? null : eval.id)}
              className={cn(
                'border-b border-gray-100 cursor-pointer hover:bg-gray-50',
                expandedId === eval.id && 'bg-gray-50'
              )}
            >
              <td className="p-3 text-gray-900">{eval.question_text}</td>
              <td className="p-3 text-gray-500">{eval.category}</td>
              <td className={cn('p-3 font-medium', eval.scores.overall < 5 ? 'text-red-600' : 'text-gray-900')}>
                {eval.scores.overall.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

---

## Pattern 3 — Component with loading + error state

Every component that fetches data must handle loading and error:

```typescript
// frontend/components/ScoreCard.tsx — KPI metric card
import { cn } from '@/lib/utils'

interface ScoreCardProps {
  title: string
  value: number
  subtitle?: string
  accent?: boolean
  loading?: boolean
}

export function ScoreCard({ title, value, subtitle, accent = false, loading = false }: ScoreCardProps) {
  if (loading) {
    return (
      <div className="border border-gray-200 rounded-lg p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-24 mb-3" />
        <div className="h-8 bg-gray-200 rounded w-16" />
      </div>
    )
  }

  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <p className="text-gray-500 text-sm font-medium">{title}</p>
      <p className={cn('text-3xl font-bold mt-1', accent ? 'text-red-600' : 'text-gray-900')}>
        {typeof value === 'number' ? value.toFixed(1) : value}
      </p>
      {subtitle && <p className="text-gray-400 text-xs mt-1">{subtitle}</p>}
    </div>
  )
}
```

---

## Pattern 4 — Recharts chart

```typescript
// frontend/components/ScoreTrendChart.tsx — Score over time line chart
'use client'

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import type { TrendPoint } from '@/lib/types'

interface ScoreTrendChartProps {
  data: TrendPoint[]
}

export function ScoreTrendChart({ data }: ScoreTrendChartProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <h2 className="text-gray-900 font-semibold mb-4">Score Trend</h2>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="date" tick={{ fill: '#6B7280', fontSize: 12 }} />
          <YAxis domain={[0, 10]} tick={{ fill: '#6B7280', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ border: '1px solid #E5E7EB', borderRadius: '6px' }}
          />
          <Line
            type="monotone"
            dataKey="avg_overall"
            stroke="#DC2626"
            strokeWidth={2}
            dot={false}
            name="Overall Score"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

---

## Pattern 5 — lib/api.ts with typed responses

```typescript
// frontend/lib/api.ts — All API calls to the FastAPI backend
import type { OverviewStats, EvalListResponse, EvalResult, CategoryStat, TrendPoint, Anomaly } from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { next: { revalidate: 30 } })
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json() as Promise<T>
}

export const getOverview = () => apiFetch<OverviewStats>('/stats/overview')
export const getStatsByCategory = () => apiFetch<CategoryStat[]>('/stats/by-category')
export const getScoreTrend = (days: number) => apiFetch<TrendPoint[]>(`/stats/trend?days=${days}`)
export const getAnomalies = () => apiFetch<Anomaly[]>('/stats/anomalies')
export const getAdversarialSummary = () => apiFetch<AdversarialSummary>('/adversarial/summary')
export const getEvals = (page: number, limit = 20) =>
  apiFetch<EvalListResponse>(`/evals/?page=${page}&limit=${limit}`)
export const getEvalById = (id: string) => apiFetch<EvalResult>(`/evals/${id}`)
```

---

## Server vs Client Component decision

| Use Server Component when | Use Client Component when |
|--------------------------|--------------------------|
| Only displaying data | Has `useState` or `useEffect` |
| Fetching data at render time | Has click/input handlers |
| No interactivity needed | Uses browser APIs |
| Default — prefer this | Explicitly opt-in with `"use client"` |

---

## Phase scope by phase

| Phase | What I build |
|-------|-------------|
| 8 | `lib/api.ts`, `lib/types.ts`, all 5 components, all 4 screens |
