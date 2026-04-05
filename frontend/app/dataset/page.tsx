// Visualise Dataset — browse products, questions, and adversarial queries from the data layer
'use client'

import { useState, useEffect } from 'react'
import { getDataProducts, getDataQuestions, getDataAdversarial } from '@/lib/api'

type Tab = 'products' | 'questions' | 'adversarial'

interface Product {
  id: string
  name: string
  category: string
  price: number
  currency: string
  rating: number
  review_count: number
  brand: string
  description: string
  specs: Record<string, unknown>
  tags: string[]
  in_stock: boolean
}

interface Question {
  id: string
  question: string
  category: string
  difficulty: string
  intent: string
  expected_product_categories: string[]
  notes: string
}

interface Adversarial {
  id: string
  question: string
  category: string
  target_failure: string
  notes: string
}

const TAB_LABELS: { key: Tab; label: string; desc: string }[] = [
  { key: 'products', label: 'Products', desc: '1,000 synthetic products across 5 categories' },
  { key: 'questions', label: 'Questions', desc: '200 shopping questions at 3 difficulty levels' },
  { key: 'adversarial', label: 'Adversarial', desc: '50 adversarial queries across 5 failure modes' },
]

function difficultyColor(d: string): string {
  if (d === 'easy') return 'text-green-600 bg-green-50'
  if (d === 'medium') return 'text-yellow-600 bg-yellow-50'
  return 'text-red-600 bg-red-50'
}

function categoryColor(c: string): string {
  const colors: Record<string, string> = {
    missing_info_trap: 'text-red-600 bg-red-50',
    contradiction_query: 'text-yellow-600 bg-yellow-50',
    ambiguous_intent: 'text-blue-600 bg-blue-50',
    price_trap: 'text-orange-600 bg-orange-50',
    pressure_scenario: 'text-purple-600 bg-purple-50',
  }
  return colors[c] || 'text-gray-600 bg-gray-50'
}

export default function DatasetPage() {
  const [tab, setTab] = useState<Tab>('products')
  const [products, setProducts] = useState<Product[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [adversarial, setAdversarial] = useState<Adversarial[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')

  useEffect(() => {
    async function loadAll() {
      try {
        const [p, q, a] = await Promise.all([
          getDataProducts(),
          getDataQuestions(),
          getDataAdversarial(),
        ])
        setProducts(p as unknown as Product[])
        setQuestions(q as unknown as Question[])
        setAdversarial(a as unknown as Adversarial[])
      } catch {
        setError('Failed to load dataset')
      } finally {
        setLoading(false)
      }
    }
    loadAll()
  }, [])

  const searchLower = search.toLowerCase()

  const filteredProducts = products.filter((p) => {
    const matchesSearch = !search || p.name.toLowerCase().includes(searchLower) || p.description.toLowerCase().includes(searchLower) || p.brand.toLowerCase().includes(searchLower)
    const matchesCategory = !categoryFilter || p.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const filteredQuestions = questions.filter((q) => {
    const matchesSearch = !search || q.question.toLowerCase().includes(searchLower) || q.category.toLowerCase().includes(searchLower)
    const matchesCategory = !categoryFilter || q.difficulty === categoryFilter
    return matchesSearch && matchesCategory
  })

  const filteredAdversarial = adversarial.filter((a) => {
    const matchesSearch = !search || a.question.toLowerCase().includes(searchLower) || a.notes.toLowerCase().includes(searchLower)
    const matchesCategory = !categoryFilter || a.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const productCategories = [...new Set(products.map((p) => p.category))]
  const adversarialCategories = [...new Set(adversarial.map((a) => a.category))]

  function getFilterOptions(): { value: string; label: string }[] {
    if (tab === 'products') return productCategories.map((c) => ({ value: c, label: c }))
    if (tab === 'questions') return [
      { value: 'easy', label: 'Easy' },
      { value: 'medium', label: 'Medium' },
      { value: 'hard', label: 'Hard' },
    ]
    return adversarialCategories.map((c) => ({ value: c, label: c.replace(/_/g, ' ') }))
  }

  function getFilterLabel(): string {
    if (tab === 'products') return 'Category'
    if (tab === 'questions') return 'Difficulty'
    return 'Failure Mode'
  }

  // Reset filter when switching tabs
  function handleTabChange(t: Tab) {
    setTab(t)
    setCategoryFilter('')
    setSearch('')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-3rem)]">
        <p className="text-gray-300 text-sm">Loading dataset...</p>
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
      <h1 className="text-sm font-semibold text-black mb-1">Visualise Dataset</h1>
      <p className="text-[13px] text-gray-400 mb-6">Browse the products, questions, and adversarial queries powering the evaluation engine</p>

      {/* Tab switcher */}
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {TAB_LABELS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => handleTabChange(key)}
            className={`px-4 py-2 text-[13px] border-b-2 transition-colors ${
              tab === key
                ? 'border-black text-black font-medium'
                : 'border-transparent text-gray-400 hover:text-black'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Description + counts */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-[13px] text-gray-400">
          {TAB_LABELS.find((t) => t.key === tab)?.desc}
        </p>
        <p className="text-[11px] text-gray-400">
          Showing{' '}
          {tab === 'products' ? filteredProducts.length : tab === 'questions' ? filteredQuestions.length : filteredAdversarial.length}
          {' '}of{' '}
          {tab === 'products' ? products.length : tab === 'questions' ? questions.length : adversarial.length}
        </p>
      </div>

      {/* Search + filter */}
      <div className="flex gap-4 mb-5 flex-wrap">
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-white border border-gray-200 rounded px-3 py-1.5 text-[13px] text-black focus:outline-none focus:ring-1 focus:ring-gray-300 w-64"
        />
        <div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-white border border-gray-200 rounded px-3 py-1.5 text-[13px] text-black focus:outline-none focus:ring-1 focus:ring-gray-300"
          >
            <option value="">All {getFilterLabel()}s</option>
            {getFilterOptions().map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Products table */}
      {tab === 'products' && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Product</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Category</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Brand</th>
                <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Price</th>
                <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Rating</th>
                <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Reviews</th>
                <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Stock</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredProducts.slice(0, 50).map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-2.5 text-black max-w-xs">
                    <p className="font-medium">{p.name}</p>
                    <p className="text-[11px] text-gray-400 mt-0.5 line-clamp-1">{p.description}</p>
                  </td>
                  <td className="px-3 py-2.5 text-gray-500">{p.category}</td>
                  <td className="px-3 py-2.5 text-gray-500">{p.brand}</td>
                  <td className="px-3 py-2.5 text-center text-black font-medium">{p.currency === 'GBP' ? '\u00a3' : '$'}{p.price}</td>
                  <td className="px-3 py-2.5 text-center">
                    <span className={p.rating >= 4.5 ? 'text-green-600' : p.rating >= 3.5 ? 'text-yellow-600' : 'text-red-600'}>{p.rating}</span>
                  </td>
                  <td className="px-3 py-2.5 text-center text-gray-400">{p.review_count.toLocaleString()}</td>
                  <td className="px-3 py-2.5 text-center">
                    {p.in_stock ? (
                      <span className="text-green-600 text-[11px] font-medium">In Stock</span>
                    ) : (
                      <span className="text-red-600 text-[11px] font-medium">Out</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredProducts.length > 50 && (
            <p className="px-4 py-3 text-[11px] text-gray-400 border-t border-gray-100">
              Showing first 50 of {filteredProducts.length} products. Use search or filters to narrow down.
            </p>
          )}
        </div>
      )}

      {/* Questions table */}
      {tab === 'questions' && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider w-8">ID</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Question</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Category</th>
                <th className="text-center px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Difficulty</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Intent</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredQuestions.map((q) => (
                <tr key={q.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-2.5 text-gray-400 text-[11px]">{q.id}</td>
                  <td className="px-3 py-2.5 text-black">{q.question}</td>
                  <td className="px-3 py-2.5 text-gray-500">{q.category}</td>
                  <td className="px-3 py-2.5 text-center">
                    <span className={`text-[11px] font-medium px-2 py-0.5 rounded ${difficultyColor(q.difficulty)}`}>
                      {q.difficulty}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-gray-500">{q.intent}</td>
                  <td className="px-3 py-2.5 text-gray-400 text-[12px] max-w-[200px]">{q.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Adversarial table */}
      {tab === 'adversarial' && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead className="border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider w-8">ID</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Question</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Failure Mode</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Target</th>
                <th className="text-left px-3 py-2.5 text-[11px] font-medium text-gray-400 uppercase tracking-wider">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredAdversarial.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-2.5 text-gray-400 text-[11px]">{a.id}</td>
                  <td className="px-3 py-2.5 text-black">{a.question}</td>
                  <td className="px-3 py-2.5">
                    <span className={`text-[11px] font-medium px-2 py-0.5 rounded ${categoryColor(a.category)}`}>
                      {a.category.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`text-[11px] font-medium ${
                      a.target_failure === 'hallucination' ? 'text-red-600' :
                      a.target_failure === 'accuracy' ? 'text-yellow-600' :
                      a.target_failure === 'safety' ? 'text-orange-600' :
                      'text-blue-600'
                    }`}>
                      {a.target_failure}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-gray-400 text-[12px]">{a.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
