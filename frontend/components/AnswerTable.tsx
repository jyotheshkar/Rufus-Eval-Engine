// AnswerTable — tabular view of Q+A eval results with sortable columns
'use client'

import { useState } from 'react'
import type { EvalResult } from '@/lib/types'

interface AnswerTableProps {
  evals: EvalResult[]
  page: number
  total: number
  limit: number
  onPageChange: (p: number) => void
}

function truncate(text: string, max: number): string {
  return text.length > max ? text.slice(0, max) + '…' : text
}

function scoreColor(score: number): string {
  if (score >= 8) return 'text-green-600'
  if (score >= 6) return 'text-yellow-600'
  return 'text-red-600'
}

export function AnswerTable({ evals, page, total, limit, onPageChange }: AnswerTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const totalPages = Math.ceil(total / limit)

  if (!evals || evals.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No eval results found.
      </div>
    )
  }

  return (
    <div>
      <div className="text-sm text-gray-500 mb-2">
        Showing {evals.length} of {total} results
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-gray-600 font-medium">Question</th>
              <th className="text-left px-4 py-3 text-gray-600 font-medium">Category</th>
              <th className="text-center px-4 py-3 text-gray-600 font-medium">Overall</th>
              <th className="text-center px-4 py-3 text-gray-600 font-medium">H</th>
              <th className="text-center px-4 py-3 text-gray-600 font-medium">A</th>
              <th className="text-center px-4 py-3 text-gray-600 font-medium">Ha</th>
              <th className="text-center px-4 py-3 text-gray-600 font-medium">S</th>
              <th className="text-center px-4 py-3 text-gray-600 font-medium">Anomaly</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {evals.map((ev) => (
              <>
                <tr
                  key={ev.id}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setExpandedId(expandedId === ev.id ? null : ev.id)}
                >
                  <td className="px-4 py-3 text-gray-900 max-w-xs">
                    {truncate(ev.question_text, 60)}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{ev.category}</td>
                  <td className={`px-4 py-3 text-center font-medium ${scoreColor(ev.score_overall)}`}>
                    {ev.score_overall.toFixed(1)}
                  </td>
                  <td className={`px-4 py-3 text-center ${scoreColor(ev.score_helpfulness)}`}>
                    {ev.score_helpfulness.toFixed(1)}
                  </td>
                  <td className={`px-4 py-3 text-center ${scoreColor(ev.score_accuracy)}`}>
                    {ev.score_accuracy.toFixed(1)}
                  </td>
                  <td className={`px-4 py-3 text-center ${scoreColor(ev.score_hallucination)}`}>
                    {ev.score_hallucination.toFixed(1)}
                  </td>
                  <td className={`px-4 py-3 text-center ${scoreColor(ev.score_safety)}`}>
                    {ev.score_safety.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {ev.anomaly_flagged ? (
                      <span className="inline-block px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
                        Yes
                      </span>
                    ) : (
                      <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs">
                        No
                      </span>
                    )}
                  </td>
                </tr>
                {expandedId === ev.id && (
                  <tr key={`${ev.id}-expanded`} className="bg-gray-50">
                    <td colSpan={8} className="px-4 py-4">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-gray-700">Rufus Answer:</span>
                          <p className="text-gray-600 mt-1 whitespace-pre-wrap">{ev.rufus_answer}</p>
                        </div>
                        {ev.anomaly_reason && (
                          <div>
                            <span className="font-medium text-red-600">Anomaly Reason:</span>
                            <p className="text-gray-600 mt-1">{ev.anomaly_reason}</p>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        <span className="text-sm text-gray-500">
          Page {page} of {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  )
}
