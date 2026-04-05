// types.ts — all TypeScript interfaces for API responses used across the frontend

export interface EvalResult {
  id: string
  timestamp: string
  question_id: string
  question_text: string
  category: string
  difficulty: string
  is_adversarial: boolean
  adversarial_category: string | null
  adversarial_triggered: boolean
  failure_mode_detected: string | null
  rufus_answer: string
  score_helpfulness: number
  score_accuracy: number
  score_hallucination: number
  score_safety: number
  score_overall: number
  anomaly_flagged: boolean
  anomaly_reason: string | null
}

export interface EvalListResponse {
  total: number
  page: number
  results: EvalResult[]
}

export interface OverviewStats {
  total_evals: number
  avg_overall: number
  avg_helpfulness: number
  avg_accuracy: number
  avg_hallucination: number
  avg_safety: number
  anomaly_count: number
  worst_category: string
}

export interface CategoryStat {
  category: string
  avg_overall: number
  count: number
}

export interface TrendPoint {
  date: string
  avg_overall: number
}

export interface AnomalyItem {
  eval_id: string
  timestamp: string
  question_text: string
  score_overall: number
  anomaly_reason: string
}

export interface AdversarialCategoryStat {
  category: string
  count: number
  triggered: number
  failure_rate: number
  avg_overall: number
}

export interface AdversarialSummary {
  total: number
  by_category: AdversarialCategoryStat[]
}
