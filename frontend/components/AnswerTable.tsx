// AnswerTable — tabular view of Q+A eval results
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
      <div className="text-center py-12 text-gray-300 text-sm">
        No eval results found.
      </div>
    )
  }

  return (
    <div>
      <p className="text-[11px] text-gray-400 mb-2">
        {evals.length} of {total} results
      </p>
      <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
        <table className="w-full text-[13px]">
          <thead className="border-b border-gray-100">
            <tr>
              <th className="text-left px-4 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Question</th>
              <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Category</th>
              <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Overall</th>
              <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider" title="Helpfulness">H</th>
              <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider" title="Accuracy">A</th>
              <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider" title="Hallucination">Ha</th>
              <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider" title="Safety">S</th>
              <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Anomaly</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {evals.map((ev) => (
              <>
                <tr
                  key={ev.id}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setExpandedId(expandedId === ev.id ? null : ev.id)}
                >
                  <td className="px-4 py-2.5 text-black max-w-md whitespace-normal">{ev.question_text}</td>
                  <td className="px-3 py-2.5 text-gray-400">{ev.category}</td>
                  <td className={`px-3 py-2.5 text-center font-medium ${scoreColor(ev.score_overall)}`}>{ev.score_overall.toFixed(1)}</td>
                  <td className={`px-3 py-2.5 text-center ${scoreColor(ev.score_helpfulness)}`}>{ev.score_helpfulness.toFixed(1)}</td>
                  <td className={`px-3 py-2.5 text-center ${scoreColor(ev.score_accuracy)}`}>{ev.score_accuracy.toFixed(1)}</td>
                  <td className={`px-3 py-2.5 text-center ${scoreColor(ev.score_hallucination)}`}>{ev.score_hallucination.toFixed(1)}</td>
                  <td className={`px-3 py-2.5 text-center ${scoreColor(ev.score_safety)}`}>{ev.score_safety.toFixed(1)}</td>
                  <td className="px-3 py-2.5 text-center">
                    {ev.anomaly_flagged ? (
                      <span className="text-red-600 text-[11px] font-medium">Yes</span>
                    ) : (
                      <span className="text-gray-300 text-[11px]">No</span>
                    )}
                  </td>
                </tr>
                {expandedId === ev.id && (
                  <tr key={`${ev.id}-expanded`} className="bg-gray-50">
                    <td colSpan={8} className="px-4 py-4">
                      <div className="space-y-2">
                        <div>
                          <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-1">Rufus Answer</p>
                          <p className="text-[13px] text-gray-600 whitespace-pre-wrap leading-relaxed">{ev.rufus_answer}</p>
                        </div>
                        {ev.anomaly_reason && (
                          <div className="pt-1">
                            <p className="text-[11px] font-medium text-red-500 uppercase tracking-wider mb-1">Anomaly Reason</p>
                            <p className="text-[13px] text-gray-500">{ev.anomaly_reason}</p>
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
          className="px-3 py-1.5 text-[13px] text-gray-400 hover:text-black disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        <span className="text-[11px] text-gray-400">
          {page} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-3 py-1.5 text-[13px] text-gray-400 hover:text-black disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  )
}
