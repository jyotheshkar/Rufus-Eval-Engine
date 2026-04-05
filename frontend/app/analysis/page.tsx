// Weak spot analysis — category breakdown charts, worst-performing queries
'use client'

import { useState, useEffect } from 'react'
import { getCategoryStats, getEvals } from '@/lib/api'
import type { CategoryStat, EvalResult } from '@/lib/types'
import { CategoryBarChart } from '@/components/CategoryBarChart'

function scoreColor(score: number): string {
  if (score >= 8) return 'text-green-600'
  if (score >= 6) return 'text-yellow-600'
  return 'text-red-600'
}

export default function AnalysisPage() {
  const [categoryStats, setCategoryStats] = useState<CategoryStat[]>([])
  const [worstEvals, setWorstEvals] = useState<EvalResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        const [cats, evalsResp] = await Promise.all([
          getCategoryStats(),
          getEvals({ page: 1, limit: 100 }),
        ])
        setCategoryStats(cats)
        const sorted = [...evalsResp.results].sort((a, b) => a.score_overall - b.score_overall)
        setWorstEvals(sorted.slice(0, 10))
      } catch {
        setError('Failed to load analysis data')
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
      <h1 className="text-sm font-semibold text-black mb-1">Weak Spot Analysis</h1>
      <p className="text-[13px] text-gray-400 mb-8">Category breakdowns and lowest-scoring answers</p>

      <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
        <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-4">Average Score by Category</p>
        <CategoryBarChart data={categoryStats} />
      </div>

      {categoryStats.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto mb-6">
          <div className="px-5 pt-4 pb-2">
            <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Category Breakdown</p>
          </div>
          <table className="w-full text-[13px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left px-5 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Category</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Evals</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Avg Overall</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {categoryStats.map((c) => (
                <tr key={c.category} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-2.5 text-black">{c.category}</td>
                  <td className="px-4 py-2.5 text-center text-gray-400">{c.count}</td>
                  <td className="px-4 py-2.5 text-center">
                    <span className={`font-medium ${scoreColor(c.avg_overall)}`}>{c.avg_overall.toFixed(1)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
        <div className="px-5 pt-4 pb-1">
          <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">10 Worst Answers</p>
          <p className="text-[11px] text-gray-300 mt-0.5">Lowest overall scores</p>
        </div>
        {worstEvals.length === 0 ? (
          <p className="px-5 py-4 text-gray-300 text-sm">No data available.</p>
        ) : (
          <table className="w-full text-[13px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left px-5 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Question</th>
                <th className="text-left px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Category</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Overall</th>
                <th className="text-center px-4 py-2 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Anomaly</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {worstEvals.map((ev) => (
                <tr key={ev.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-2.5 text-black max-w-sm truncate">{ev.question_text}</td>
                  <td className="px-4 py-2.5 text-gray-400">{ev.category}</td>
                  <td className="px-4 py-2.5 text-center text-red-600 font-medium">{ev.score_overall.toFixed(1)}</td>
                  <td className="px-4 py-2.5 text-center">
                    {ev.anomaly_flagged ? (
                      <span className="text-red-600 text-[11px] font-medium">Yes</span>
                    ) : (
                      <span className="text-gray-300 text-[11px]">No</span>
                    )}
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
