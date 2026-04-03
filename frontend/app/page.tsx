// Overview screen — KPI cards, score trend chart, anomaly count
'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
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
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-500">Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Rufus Eval Engine</h1>
        <div className="h-1 w-16 bg-red-600 mt-2 rounded" />
        <p className="text-gray-500 mt-3">LLM quality evaluation dashboard for the Rufus shopping assistant</p>
      </div>

      {/* Nav */}
      <nav className="flex gap-4 mb-8">
        <Link href="/" className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium">
          Overview
        </Link>
        <Link href="/feed" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Answer Feed
        </Link>
        <Link href="/analysis" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Weak Spot Analysis
        </Link>
        <Link href="/adversarial" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Adversarial Report
        </Link>
      </nav>

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <ScoreCard
            title="Avg Overall Score"
            value={stats.avg_overall.toFixed(1)}
            subtitle={`${stats.total_evals} total evals`}
            accent
          />
          <ScoreCard
            title="Avg Helpfulness"
            value={stats.avg_helpfulness.toFixed(1)}
            subtitle="Out of 10"
          />
          <ScoreCard
            title="Avg Hallucination"
            value={stats.avg_hallucination.toFixed(1)}
            subtitle="10 = no hallucination"
          />
          <ScoreCard
            title="Anomalies"
            value={stats.anomaly_count}
            subtitle={`Worst: ${stats.worst_category}`}
            accent={stats.anomaly_count > 0}
          />
        </div>
      )}

      {/* Score Trend */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Score Trend (7 days)</h2>
        <ScoreTrendChart data={trendData} />
      </div>

      {/* Category Chart + Anomaly List */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Score by Category</h2>
          <CategoryBarChart data={categoryStats} />
        </div>
        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Anomalies</h2>
            <AnomalyBadge count={anomalies.length} />
          </div>
          {anomalies.length === 0 ? (
            <p className="text-gray-400 text-sm">No anomalies detected recently.</p>
          ) : (
            <ul className="space-y-3">
              {anomalies.slice(0, 5).map((a) => (
                <li key={a.eval_id} className="border-l-2 border-red-300 pl-3">
                  <p className="text-sm text-gray-800 font-medium truncate">{a.question_text}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Score: <span className="text-red-600 font-medium">{a.score_overall.toFixed(1)}</span>
                    {' · '}{a.anomaly_reason}
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
