// Adversarial report — failure mode breakdown, failure rate by type, export
'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
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

  const totalQueries = summary?.total ?? 0
  const byCategory = summary?.by_category ?? []
  const totalTriggered = byCategory.reduce((acc, c) => acc + c.triggered, 0)
  const overallFailureRate = totalQueries > 0 ? totalTriggered / totalQueries : 0
  const worstMode = byCategory.length > 0
    ? byCategory.reduce((best, c) => c.failure_rate > best.failure_rate ? c : best).category
    : 'N/A'

  const chartData = toFailureCategoryData(byCategory)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Adversarial Report</h1>
          <div className="h-1 w-16 bg-red-600 mt-2 rounded" />
        </div>
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Export JSON
        </button>
      </div>

      {/* Nav */}
      <nav className="flex gap-4 mb-8">
        <Link href="/" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Overview
        </Link>
        <Link href="/feed" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Answer Feed
        </Link>
        <Link href="/analysis" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Weak Spot Analysis
        </Link>
        <Link href="/adversarial" className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium">
          Adversarial Report
        </Link>
      </nav>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <ScoreCard
          title="Total Adversarial Queries"
          value={totalQueries}
          subtitle="Across all failure modes"
        />
        <ScoreCard
          title="Overall Failure Rate"
          value={`${(overallFailureRate * 100).toFixed(1)}%`}
          subtitle={`${totalTriggered} failures detected`}
          accent={overallFailureRate > 0.3}
        />
        <ScoreCard
          title="Worst Failure Mode"
          value={worstMode}
          subtitle="Highest failure rate category"
          accent
        />
      </div>

      {/* Failure Rate Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Failure Rate by Category
          <span className="text-sm font-normal text-gray-500 ml-2">(scaled to 0–10)</span>
        </h2>
        <CategoryBarChart data={chartData} />
      </div>

      {/* Breakdown Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-x-auto">
        <div className="p-6 pb-2">
          <h2 className="text-lg font-semibold text-gray-900">Results by Failure Mode</h2>
        </div>
        {byCategory.length === 0 ? (
          <p className="px-6 py-4 text-gray-400 text-sm">No adversarial data available.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-gray-600 font-medium">Failure Mode</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Queries</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Triggered</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Failure Rate</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Avg Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {byCategory.map((c) => (
                <tr key={c.category} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-gray-900 font-medium">{c.category}</td>
                  <td className="px-4 py-3 text-center text-gray-500">{c.count}</td>
                  <td className="px-4 py-3 text-center text-gray-500">{c.triggered}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`font-medium ${c.failure_rate > 0.5 ? 'text-red-600' : c.failure_rate > 0.25 ? 'text-yellow-600' : 'text-green-600'}`}>
                      {(c.failure_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-700">
                    {c.avg_overall.toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
