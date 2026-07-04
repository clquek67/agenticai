'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const [ticker, setTicker] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault()
    if (!ticker.trim()) return
    setLoading(true)

    try {
      const res = await fetch('/api/analyses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker: ticker.toUpperCase().trim(),
          company_name: companyName.trim() || null,
        }),
      })
      const data = await res.json()
      if (data.id) {
        router.push(
          `/analysis/${data.id}?ticker=${encodeURIComponent(ticker.toUpperCase().trim())}&company=${encodeURIComponent(companyName.trim())}`
        )
      }
    } catch {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">📈</div>
          <h1 className="text-4xl font-bold text-white mb-2">StockScan</h1>
          <p className="text-blue-300 text-lg">10-minute stock analysis framework</p>
          <p className="text-slate-400 text-sm mt-1">6-stage AI-powered due diligence</p>
        </div>

        <form onSubmit={handleAnalyze} className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-8 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Stock Ticker *
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="e.g. AAPL, RELIANCE, TSLA"
              className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Company Name <span className="text-gray-400">(optional)</span>
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Apple Inc."
              className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !ticker.trim()}
            className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Starting analysis...
              </>
            ) : (
              <>🔍 Analyze Stock</>
            )}
          </button>

          <p className="text-center text-xs text-gray-400">Analysis takes ~2 minutes across 6 stages</p>
        </form>

        <div className="text-center mt-6">
          <a href="/history" className="text-blue-400 hover:text-blue-300 text-sm">
            View past analyses →
          </a>
        </div>

        <div className="mt-8 grid grid-cols-3 gap-3 text-center">
          {[
            { icon: '🏢', label: 'Business' },
            { icon: '💰', label: 'Financials' },
            { icon: '📊', label: 'Valuation' },
            { icon: '👥', label: 'Promoters' },
            { icon: '🌍', label: 'Industry' },
            { icon: '🎯', label: 'Verdict' },
          ].map(({ icon, label }) => (
            <div key={label} className="bg-white/10 rounded-lg p-3">
              <div className="text-2xl">{icon}</div>
              <div className="text-xs text-slate-300 mt-1">{label}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
