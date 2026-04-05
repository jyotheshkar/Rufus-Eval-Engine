// api.ts — all FastAPI calls; no fetch() allowed directly in components

import type {
  EvalResult,
  EvalListResponse,
  OverviewStats,
  CategoryStat,
  TrendPoint,
  AnomalyItem,
  AdversarialSummary,
} from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export async function getHealth(): Promise<{ status: string; total_evals: number; last_run: string | null }> {
  return fetchJson('/health')
}

export async function getEvals(params: {
  page?: number
  limit?: number
  category?: string
  is_adversarial?: boolean | null
}): Promise<EvalListResponse> {
  const query = new URLSearchParams()
  if (params.page !== undefined) query.set('page', String(params.page))
  if (params.limit !== undefined) query.set('limit', String(params.limit))
  if (params.category) query.set('category', params.category)
  if (params.is_adversarial !== undefined && params.is_adversarial !== null) {
    query.set('is_adversarial', String(params.is_adversarial))
  }
  const qs = query.toString()
  return fetchJson(`/evals${qs ? `?${qs}` : ''}`)
}

export async function getEvalById(id: string): Promise<EvalResult> {
  return fetchJson(`/evals/${id}`)
}

export async function getOverviewStats(): Promise<OverviewStats> {
  return fetchJson('/stats/overview')
}

export async function getCategoryStats(): Promise<CategoryStat[]> {
  return fetchJson('/stats/by-category')
}

export async function getTrendStats(days = 7): Promise<TrendPoint[]> {
  return fetchJson(`/stats/trend?days=${days}`)
}

export async function getAnomalies(): Promise<AnomalyItem[]> {
  return fetchJson('/stats/anomalies')
}

export async function getAdversarialSummary(): Promise<AdversarialSummary> {
  return fetchJson('/adversarial/summary')
}

export async function getDataProducts(): Promise<Record<string, unknown>[]> {
  return fetchJson('/data/products')
}

export async function getDataQuestions(): Promise<Record<string, unknown>[]> {
  return fetchJson('/data/questions')
}

export async function getDataAdversarial(): Promise<Record<string, unknown>[]> {
  return fetchJson('/data/adversarial')
}
