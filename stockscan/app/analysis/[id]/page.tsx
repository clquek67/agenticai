'use client'

import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import { Stepper } from '@/components/Stepper'
import { StageCard } from '@/components/StageCard'
import { MetricRow } from '@/components/MetricRow'

type Status = 'green' | 'yellow' | 'red' | 'loading' | 'pending'

interface StageState<T> {
  data: T | null
  status: Status
}

const STAGE_META = [
  {
    title: 'Business Understanding',
    icon: '🏢',
    questions: [
      'What does the company do?',
      'How does it make money?',
      'Does it have a moat?',
      'What industry is it in?',
      'Who runs it?',
    ],
  },
  {
    title: 'Basic Financials',
    icon: '💰',
    questions: [
      'Revenue/profit growing? ROE > 15%?',
      'Debt-to-Equity < 1?',
      'Net Profit Margin > 15%?',
      'Liquidity / Quick Ratio',
      'Interest Coverage Ratio',
    ],
  },
  {
    title: 'Quick Valuation',
    icon: '📊',
    questions: [
      'P/E vs industry average',
      'PEG ratio < 2?',
      'EV/EBITDA vs industry',
      'Price/Book ratio',
      'Dividend Yield',
    ],
  },
  {
    title: 'Promoter & Management',
    icon: '👥',
    questions: [
      'Promoter holding %',
      'Promoter pledging (high = risk)',
      'Institutional holding',
      'Insider buying/selling trend',
    ],
  },
  {
    title: 'Industry & Risk',
    icon: '🌍',
    questions: [
      'Is the industry cyclical?',
      'Demand growing, flat, or shrinking?',
      'Fragmented vs monopoly/oligopoly?',
      'Exposure to global macro factors?',
    ],
  },
]

const verdictConfig = {
  invest: { label: 'INVEST', color: 'bg-green-500', emoji: '✅' },
  watchlist: { label: 'WATCHLIST', color: 'bg-yellow-500', emoji: '👀' },
  pass: { label: 'PASS', color: 'bg-red-500', emoji: '❌' },
}

export default function AnalysisPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const id = params.id as string
  const ticker = searchParams.get('ticker') || ''
  const company = searchParams.get('company') || ''

  const [currentStage, setCurrentStage] = useState(1)
  const [stage1, setStage1] = useState<StageState<any>>({ data: null, status: 'loading' })
  const [stage2, setStage2] = useState<StageState<any>>({ data: null, status: 'pending' })
  const [stage3, setStage3] = useState<StageState<any>>({ data: null, status: 'pending' })
  const [stage4, setStage4] = useState<StageState<any>>({ data: null, status: 'pending' })
  const [stage5, setStage5] = useState<StageState<any>>({ data: null, status: 'pending' })
  const [verdict, setVerdict] = useState<{ verdict: string; final_summary: string } | null>(null)
  const [verdictLoading, setVerdictLoading] = useState(false)

  const body = { ticker, company_name: company }

  async function runStage(endpoint: string, setState: (s: StageState<any>) => void, nextFn?: () => void) {
    try {
      const res = await fetch(`/api/analyze/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setState({ data, status: data.status || 'green' })
      nextFn?.()
    } catch (err: any) {
      setState({ data: { error: err.message }, status: 'red' })
      nextFn?.()
    }
  }

  useEffect(() => {
    runStage('business', setStage1, () => {
      setCurrentStage(2)
      setStage2((s) => ({ ...s, status: 'loading' }))
      runStage('financials', setStage2, () => {
        setCurrentStage(3)
        setStage3((s) => ({ ...s, status: 'loading' }))
        runStage('valuation', setStage3, () => {
          setCurrentStage(4)
          setStage4((s) => ({ ...s, status: 'loading' }))
          runStage('promoter', setStage4, () => {
            setCurrentStage(5)
            setStage5((s) => ({ ...s, status: 'loading' }))
            runStage('industry', setStage5, () => {
              setCurrentStage(6)
            })
          })
        })
      })
    })
  }, [])

  // Trigger verdict after stage5 completes
  useEffect(() => {
    if (currentStage === 6 && stage5.data && !verdict && !verdictLoading) {
      setVerdictLoading(true)
      fetch('/api/analyze/verdict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker,
          company_name: company,
          stage1: stage1.data,
          stage2: stage2.data,
          stage3: stage3.data,
          stage4: stage4.data,
          stage5: stage5.data,
        }),
      })
        .then((r) => r.json())
        .then((verdictData) => {
          setVerdict(verdictData)
          // Update the existing record with all stage data and verdict
          return fetch(`/api/analyses/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              company_name: company || null,
              stage1: stage1.data,
              stage2: stage2.data,
              stage3: stage3.data,
              stage4: stage4.data,
              stage5: stage5.data,
              verdict: verdictData.verdict,
              final_summary: verdictData.final_summary,
            }),
          })
        })
        .catch(() => setVerdict({ verdict: 'watchlist', final_summary: 'Analysis complete.' }))
        .finally(() => setVerdictLoading(false))
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStage, stage5.data])

  function renderBusiness(data: any) {
    if (data.error) return <p className="text-red-500 text-sm">{data.error}</p>
    return (
      <div className="space-y-2">
        {data.answers && Object.entries(data.answers).map(([key, val]: [string, any]) => (
          <div key={key} className="text-sm">
            <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">{key.replace(/_/g, ' ')}: </span>
            <span className="text-gray-600 dark:text-gray-400">{val}</span>
          </div>
        ))}
        {data.notes && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">{data.notes}</p>}
      </div>
    )
  }

  function renderFinancials(data: any) {
    if (data.error) return <p className="text-red-500 text-sm">{data.error}</p>
    return (
      <div>
        <MetricRow label="ROE" value={data.roe_percent != null ? `${data.roe_percent}%` : null} good={data.roe_percent > 15} />
        <MetricRow label="Debt/Equity" value={data.debt_to_equity} good={data.debt_to_equity < 1} />
        <MetricRow label="Net Profit Margin" value={data.net_profit_margin_percent != null ? `${data.net_profit_margin_percent}%` : null} good={data.net_profit_margin_percent > 15} />
        <MetricRow label="Quick Ratio" value={data.quick_ratio} good={data.quick_ratio >= 1} />
        <MetricRow label="Interest Coverage" value={data.interest_coverage_ratio} good={data.interest_coverage_ratio > 3} />
        <MetricRow label="Revenue Trend" value={data.revenue_trend} />
        {data.notes && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">{data.notes}</p>}
      </div>
    )
  }

  function renderValuation(data: any) {
    if (data.error) return <p className="text-red-500 text-sm">{data.error}</p>
    return (
      <div>
        <MetricRow label="P/E Ratio" value={data.pe_ratio} good={data.pe_ratio != null && data.pe_ratio <= (data.industry_pe_avg || 20)} />
        <MetricRow label="Industry P/E Avg" value={data.industry_pe_avg} />
        <MetricRow label="PEG Ratio" value={data.peg_ratio} good={data.peg_ratio < 2} />
        <MetricRow label="EV/EBITDA" value={data.ev_ebitda} good={data.ev_ebitda != null && data.ev_ebitda <= (data.industry_ev_ebitda_avg || 15)} />
        <MetricRow label="Price/Book" value={data.price_to_book} />
        <MetricRow label="Dividend Yield" value={data.dividend_yield_percent != null ? `${data.dividend_yield_percent}%` : null} />
        {data.notes && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">{data.notes}</p>}
      </div>
    )
  }

  function renderPromoter(data: any) {
    if (data.error) return <p className="text-red-500 text-sm">{data.error}</p>
    return (
      <div>
        <MetricRow label="Promoter Holding" value={data.promoter_holding_pct != null ? `${data.promoter_holding_pct}%` : null} good={data.promoter_holding_pct > 50} />
        <MetricRow label="Pledging %" value={data.pledging_pct != null ? `${data.pledging_pct}%` : null} good={data.pledging_pct < 5} />
        <MetricRow label="Institutional Holding" value={data.institutional_holding_pct != null ? `${data.institutional_holding_pct}%` : null} />
        <MetricRow label="Insider Trend" value={data.insider_trend} good={data.insider_trend === 'buying'} />
        {data.notes && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">{data.notes}</p>}
      </div>
    )
  }

  function renderIndustry(data: any) {
    if (data.error) return <p className="text-red-500 text-sm">{data.error}</p>
    return (
      <div>
        <MetricRow label="Cyclical" value={data.cyclical == null ? 'Unknown' : data.cyclical ? `Yes — ${data.cyclical_type || ''}` : 'No'} good={!data.cyclical} />
        <MetricRow label="Demand Trend" value={data.demand_trend} good={data.demand_trend === 'growing'} />
        <MetricRow label="Market Structure" value={data.market_structure} good={['monopoly', 'oligopoly'].includes(data.market_structure)} />
        <MetricRow label="Macro Exposure" value={data.macro_exposure} />
        {data.notes && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">{data.notes}</p>}
      </div>
    )
  }

  const stageRenderers = [renderBusiness, renderFinancials, renderValuation, renderPromoter, renderIndustry]
  const stages = [stage1, stage2, stage3, stage4, stage5]

  const vc = verdict ? verdictConfig[verdict.verdict as keyof typeof verdictConfig] : null

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <a href="/" className="text-blue-600 dark:text-blue-400 text-sm hover:underline">
                ← New Analysis
              </a>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                {ticker} {company && <span className="text-gray-500 font-normal text-base">— {company}</span>}
              </h1>
            </div>
            <a href="/history" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              History
            </a>
          </div>
          <Stepper currentStage={currentStage} />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-4">
        {STAGE_META.map((meta, i) => (
          <StageCard
            key={i}
            stageNumber={i + 1}
            title={meta.title}
            icon={meta.icon}
            questions={meta.questions}
            data={stages[i].data}
            status={stages[i].status}
            renderData={stageRenderers[i]}
          />
        ))}

        {/* Stage 6: Verdict */}
        <div className="border-l-4 rounded-lg shadow-sm overflow-hidden bg-white dark:bg-slate-800 border-purple-500">
          <div className="px-6 py-4 flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Stage 6</span>
              <h3 className="font-semibold text-gray-900 dark:text-white">Final Decision</h3>
            </div>
          </div>

          <div className="px-6 pb-6">
            {verdictLoading && (
              <div className="flex items-center gap-3 text-purple-600 dark:text-purple-400">
                <div className="w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm">Synthesizing all stages...</span>
              </div>
            )}
            {currentStage < 6 && !verdictLoading && (
              <p className="text-sm text-gray-400 italic">Waiting for all stages to complete...</p>
            )}
            {verdict && vc && (
              <div className="space-y-4">
                <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-full text-white font-bold text-xl ${vc.color}`}>
                  <span>{vc.emoji}</span>
                  <span>{vc.label}</span>
                </div>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{verdict.final_summary}</p>
                <div className="grid grid-cols-4 gap-2 pt-2">
                  {[stage2, stage3, stage4, stage5].map((s, i) => (
                    <div key={i} className={`text-center py-2 px-1 rounded text-xs font-medium ${
                      s.status === 'green' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' :
                      s.status === 'red' ? 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300' :
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
                    }`}>
                      {['Financials', 'Valuation', 'Promoter', 'Industry'][i]}: {s.status}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
