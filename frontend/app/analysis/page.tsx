// Weak spot analysis — category breakdown charts, worst-performing queries
'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getCategoryStats, getEvals } from '@/lib/api'
import type { CategoryStat, EvalResult } from '@/lib/types'
import { CategoryBarChart } from '@/components/CategoryBarChart'

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
          getEvals({ page: 1, limit: 200 }),
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
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Weak Spot Analysis</h1>
        <div className="h-1 w-16 bg-red-600 mt-2 rounded" />
      </div>

      {/* Nav */}
      <nav className="flex gap-4 mb-8">
        <Link href="/" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Overview
        </Link>
        <Link href="/feed" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Answer Feed
        </Link>
        <Link href="/analysis" className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium">
          Weak Spot Analysis
        </Link>
        <Link href="/adversarial" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Adversarial Report
        </Link>
      </nav>

      {/* Category Bar Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Average Score by Category</h2>
        <CategoryBarChart data={categoryStats} />
      </div>

      {/* Per-category breakdown table */}
      {categoryStats.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm mb-8 overflow-x-auto">
          <div className="p-6 pb-2">
            <h2 className="text-lg font-semibold text-gray-900">Category Breakdown</h2>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-gray-600 font-medium">Category</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Evals</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Avg Overall</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {categoryStats.map((c) => (
                <tr key={c.category} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-gray-900 font-medium">{c.category}</td>
                  <td className="px-4 py-3 text-center text-gray-500">{c.count}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`font-medium ${c.avg_overall >= 8 ? 'text-green-600' : c.avg_overall >= 6 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {c.avg_overall.toFixed(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 10 worst answers */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-x-auto">
        <div className="p-6 pb-2">
          <h2 className="text-lg font-semibold text-gray-900">10 Worst Answers</h2>
          <p className="text-sm text-gray-500 mt-1">Lowest overall scores in the dataset</p>
        </div>
        {worstEvals.length === 0 ? (
          <p className="px-6 py-4 text-gray-400 text-sm">No data available.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-gray-600 font-medium">Question</th>
                <th className="text-left px-4 py-3 text-gray-600 font-medium">Category</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Overall</th>
                <th className="text-center px-4 py-3 text-gray-600 font-medium">Anomaly</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {worstEvals.map((ev) => (
                <tr key={ev.id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-gray-800 max-w-sm truncate">{ev.question_text}</td>
                  <td className="px-4 py-3 text-gray-500">{ev.category}</td>
                  <td className="px-4 py-3 text-center text-red-600 font-medium">
                    {ev.score_overall.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {ev.anomaly_flagged ? (
                      <span className="inline-block px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">Yes</span>
                    ) : (
                      <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs">No</span>
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
