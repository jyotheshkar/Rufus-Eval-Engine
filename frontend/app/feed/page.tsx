// Answer feed — all Q+A pairs with per-dimension scores, filterable
'use client'

import { useState, useEffect } from 'react'
import { getEvals } from '@/lib/api'
import type { EvalResult } from '@/lib/types'
import { AnswerTable } from '@/components/AnswerTable'

const CATEGORIES = [
  '', 'headphones', 'laptops', 'smartphones', 'tablets', 'smartwatches',
]

const LIMIT = 20

const selectClass =
  'bg-white border border-gray-200 rounded px-3 py-1.5 text-[13px] text-black focus:outline-none focus:ring-1 focus:ring-gray-300'

export default function FeedPage() {
  const [evals, setEvals] = useState<EvalResult[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [isAdversarial, setIsAdversarial] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      setError(null)
      try {
        const resp = await getEvals({
          page, limit: LIMIT,
          category: category || undefined,
          is_adversarial: isAdversarial,
        })
        setEvals(resp.results)
        setTotal(resp.total)
      } catch {
        setError('Failed to load eval results')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [page, category, isAdversarial])

  function handleCategoryChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setCategory(e.target.value)
    setPage(1)
  }

  function handleAdversarialChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const val = e.target.value
    if (val === '') setIsAdversarial(null)
    else if (val === 'true') setIsAdversarial(true)
    else setIsAdversarial(false)
    setPage(1)
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-sm font-semibold text-black mb-1">Answer Feed</h1>
      <p className="text-[13px] text-gray-400 mb-6">Evaluated Q&amp;A pairs with per-dimension scores</p>

      <div className="flex gap-4 mb-6 flex-wrap">
        <div>
          <label htmlFor="category-filter" className="block text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-1">Category</label>
          <select id="category-filter" value={category} onChange={handleCategoryChange} className={selectClass}>
            <option value="">All</option>
            {CATEGORIES.filter(Boolean).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="adversarial-filter" className="block text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-1">Type</label>
          <select
            id="adversarial-filter"
            value={isAdversarial === null ? '' : String(isAdversarial)}
            onChange={handleAdversarialChange}
            className={selectClass}
          >
            <option value="">All</option>
            <option value="false">Standard</option>
            <option value="true">Adversarial</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-300 text-sm py-8">Loading...</p>
      ) : error ? (
        <p className="text-red-500 text-sm py-8">{error}</p>
      ) : (
        <AnswerTable evals={evals} page={page} total={total} limit={LIMIT} onPageChange={setPage} />
      )}
    </div>
  )
}
