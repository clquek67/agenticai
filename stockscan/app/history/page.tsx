'use client'

import { useEffect, useState } from 'react'

interface Analysis {
  id: string
  ticker: string
  company_name: string | null
  created_at: string
  final_verdict: string | null
  final_summary: string | null
}

const verdictConfig = {
  invest: { label: 'INVEST', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
  watchlist: { label: 'WATCHLIST', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' },
  pass: { label: 'PASS', className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' },
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const url = filter ? `/api/analyses?verdict=${filter}` : '/api/analyses'
    fetch(url)
      .then((r) => r.json())
      .then((data) => setAnalyses(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false))
  }, [filter])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <a href="/" className="text-blue-600 dark:text-blue-400 text-sm hover:underline">← New Analysis</a>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Analysis History</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          {['', 'invest', 'watchlist', 'pass'].map((v) => (
            <button
              key={v}
              onClick={() => setFilter(v)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                filter === v
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-slate-800 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-slate-600 hover:border-blue-400'
              }`}
            >
              {v === '' ? 'All' : v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>

        {loading && (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && analyses.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-3">📭</div>
            <p>No analyses yet. <a href="/" className="text-blue-500 hover:underline">Analyze a stock →</a></p>
          </div>
        )}

        <div className="space-y-3">
          {analyses.map((a) => {
            const vc = a.final_verdict ? verdictConfig[a.final_verdict as keyof typeof verdictConfig] : null
            return (
              <div key={a.id} className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-5 flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-gray-900 dark:text-white">{a.ticker}</span>
                    {a.company_name && (
                      <span className="text-gray-500 dark:text-gray-400 text-sm">{a.company_name}</span>
                    )}
                    {vc && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${vc.className}`}>
                        {vc.label}
                      </span>
                    )}
                  </div>
                  {a.final_summary && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{a.final_summary}</p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(a.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </p>
                </div>
                <a
                  href={`/analysis/${a.id}?ticker=${encodeURIComponent(a.ticker)}&company=${encodeURIComponent(a.company_name || '')}`}
                  className="flex-shrink-0 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View →
                </a>
              </div>
            )
          })}
        </div>
      </main>
    </div>
  )
}
