// Adversarial report — failure mode breakdown, failure rate by type, export
'use client'

import { useState, useEffect } from 'react'
import { getAdversarialSummary } from '@/lib/api'
import type { AdversarialSummary, AdversarialCategoryStat } from '@/lib/types'
import { ScoreCard } from '@/components/ScoreCard'
import { CategoryBarChart } from '@/components/CategoryBarChart'
import type { CategoryStat } from '@/lib/types'

function toFailureCategoryData(stats: AdversarialCategoryStat[]): CategoryStat[] {
  return stats.map((s) => ({
    category: s.category,
    avg_overall: parseFloat((s.failure_rate * 10).toFixed(2)),
    count: s.count,
  }))
}

function failureColor(rate: number): string {
  if (rate > 0.5) return 'text-red-600'
  if (rate > 0.25) return 'text-yellow-600'
  return 'text-green-600'
}

export default function AdversarialPage() {
  const [summary, setSummary] = useState<AdversarialSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getAdversarialSummary()
        setSummary(data)
      } catch {
        setError('Failed to load adversarial data')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  function handleExport() {
    if (!summary) return
    const blob = new Blob([JSON.stringify(summary, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'adversarial-summary.json'
    a.click()
    URL.revokeObjectURL(url)
  }

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

  const totalQueries = summary?.total ?? 0
  const byCategory = summary?.by_category ?? []
  const totalTriggered = byCategory.reduce((acc, c) => acc + c.triggered, 0)
  const overallFailureRate = totalQueries > 0 ? totalTriggered / totalQueries : 0
  const worstMode = byCategory.length > 0
    ? byCategory.reduce((best, c) => c.failure_rate > best.failure_rate ? c : best).category
    : 'N/A'

  const chartData = toFailureCategoryData(byCategory)

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-sm font-semibold text-black mb-1">Adversarial Report</h1>
          <p className="text-[13px] text-gray-400">Failure mode analysis across adversarial query types</p>
        </div>
        <button
          onClick={handleExport}
          className="px-3 py-1.5 text-[13px] text-gray-400 hover:text-black border border-gray-200 rounded hover:border-gray-300 transition-colors"
        >
          Export JSON
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-8">
        <ScoreCard title="Total Queries" value={totalQueries} subtitle="All failure modes" />
        <ScoreCard
          title="Failure Rate"
          value={`${(overallFailureRate * 100).toFixed(1)}%`}
          subtitle={`${totalTriggered} failures`}
          accent={overallFailureRate > 0.3}
        />
        <ScoreCard title="Worst Mode" value={worstMode} subtitle="Highest failure rate" accent />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
        <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-0.5">Failure Rate by Category</p>
        <p className="text-[11px] text-gray-300 mb-4">Scaled 0-10</p>
        <CategoryBarChart data={chartData} />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
        <div className="px-5 pt-4 pb-2">
          <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Results by Failure Mode</p>
        </div>
        {byCategory.length === 0 ? (
          <p className="px-5 py-4 text-gray-300 text-sm">No data available.</p>
        ) : (
          <table className="w-full text-[13px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left px-5 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Failure Mode</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Queries</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Triggered</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Failure Rate</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Avg Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {byCategory.map((c) => (
                <tr key={c.category} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-2.5 text-black">{c.category}</td>
                  <td className="px-4 py-2.5 text-center text-gray-400">{c.count}</td>
                  <td className="px-4 py-2.5 text-center text-gray-400">{c.triggered}</td>
                  <td className="px-4 py-2.5 text-center">
                    <span className={`font-medium ${failureColor(c.failure_rate)}`}>
                      {(c.failure_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center text-gray-600">{c.avg_overall.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
