// Overview screen — KPI cards, score trend chart, anomaly count
'use client'

import { useState, useEffect } from 'react'
import { getOverviewStats, getCategoryStats, getTrendStats, getAnomalies } from '@/lib/api'
import type { OverviewStats, CategoryStat, TrendPoint, AnomalyItem } from '@/lib/types'
import { ScoreCard } from '@/components/ScoreCard'
import { ScoreTrendChart } from '@/components/ScoreTrendChart'
import { CategoryBarChart } from '@/components/CategoryBarChart'
import { AnomalyBadge } from '@/components/AnomalyBadge'

export default function OverviewPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [categoryStats, setCategoryStats] = useState<CategoryStat[]>([])
  const [trendData, setTrendData] = useState<TrendPoint[]>([])
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        const [s, cats, trend, anom] = await Promise.all([
          getOverviewStats(),
          getCategoryStats(),
          getTrendStats(7),
          getAnomalies(),
        ])
        setStats(s)
        setCategoryStats(cats)
        setTrendData(trend)
        setAnomalies(anom)
      } catch {
        setError('Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-3rem)]">
        <p className="text-gray-300 text-sm">Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-3rem)]">
        <p className="text-red-500 text-sm">{error}</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-sm font-semibold text-black mb-1">Overview</h1>
      <p className="text-[13px] text-gray-400 mb-8">Quality metrics across all evaluated answers</p>

      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
          <ScoreCard title="Avg Overall" value={stats.avg_overall.toFixed(1)} subtitle={`${stats.total_evals} evals`} />
          <ScoreCard title="Helpfulness" value={stats.avg_helpfulness.toFixed(1)} subtitle="Out of 10" />
          <ScoreCard title="Hallucination" value={stats.avg_hallucination.toFixed(1)} subtitle="10 = none" />
          <ScoreCard title="Anomalies" value={stats.anomaly_count} subtitle={stats.worst_category} accent={stats.anomaly_count > 0} />
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
        <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-4">Score Trend — 7 days</p>
        <ScoreTrendChart data={trendData} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3 bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-4">Score by Category</p>
          <CategoryBarChart data={categoryStats} />
        </div>
        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Recent Anomalies</p>
            <AnomalyBadge count={anomalies.length} />
          </div>
          {anomalies.length === 0 ? (
            <p className="text-gray-300 text-sm">None detected.</p>
          ) : (
            <ul className="space-y-3">
              {anomalies.slice(0, 5).map((a) => (
                <li key={a.eval_id} className="border-l-2 border-gray-200 pl-3">
                  <p className="text-[13px] text-black truncate">{a.question_text}</p>
                  <p className="text-[11px] text-gray-400 mt-0.5">
                    <span className="text-red-600 font-medium">{a.score_overall.toFixed(1)}</span>
                    <span className="mx-1.5 text-gray-200">|</span>
                    {a.anomaly_reason}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
