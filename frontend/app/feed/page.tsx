// Answer feed — all Q+A pairs with per-dimension scores, filterable
'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getEvals } from '@/lib/api'
import type { EvalResult } from '@/lib/types'
import { AnswerTable } from '@/components/AnswerTable'

const CATEGORIES = [
  '',
  'Electronics',
  'Books',
  'Clothing',
  'Home & Kitchen',
  'Sports',
  'Beauty',
  'Toys',
  'Automotive',
  'Food',
  'Health',
]

const LIMIT = 20

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
          page,
          limit: LIMIT,
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
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Answer Feed</h1>
        <div className="h-1 w-16 bg-red-600 mt-2 rounded" />
      </div>

      {/* Nav */}
      <nav className="flex gap-4 mb-8">
        <Link href="/" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Overview
        </Link>
        <Link href="/feed" className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium">
          Answer Feed
        </Link>
        <Link href="/analysis" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Weak Spot Analysis
        </Link>
        <Link href="/adversarial" className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Adversarial Report
        </Link>
      </nav>

      {/* Filters */}
      <div className="flex gap-4 mb-6 flex-wrap">
        <div>
          <label htmlFor="category-filter" className="block text-sm text-gray-500 mb-1">Category</label>
          <select
            id="category-filter"
            value={category}
            onChange={handleCategoryChange}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-red-400"
          >
            <option value="">All categories</option>
            {CATEGORIES.filter(Boolean).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="adversarial-filter" className="block text-sm text-gray-500 mb-1">Type</label>
          <select
            id="adversarial-filter"
            value={isAdversarial === null ? '' : String(isAdversarial)}
            onChange={handleAdversarialChange}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-red-400"
          >
            <option value="">All types</option>
            <option value="false">Standard</option>
            <option value="true">Adversarial</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <p className="text-gray-500 py-8">Loading...</p>
      ) : error ? (
        <p className="text-red-600 py-8">{error}</p>
      ) : (
        <AnswerTable
          evals={evals}
          page={page}
          total={total}
          limit={LIMIT}
          onPageChange={setPage}
        />
      )}
    </div>
  )
}
