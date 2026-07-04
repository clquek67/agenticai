'use client'

import { useState } from 'react'

type Status = 'green' | 'yellow' | 'red' | 'loading' | 'pending'

interface StageCardProps {
  stageNumber: number
  title: string
  icon: string
  questions: string[]
  data: Record<string, any> | null
  status: Status
  renderData?: (data: Record<string, any>) => React.ReactNode
}

const statusColors: Record<Status, string> = {
  green: 'border-green-500 bg-green-50 dark:bg-green-950/20',
  yellow: 'border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20',
  red: 'border-red-500 bg-red-50 dark:bg-red-950/20',
  loading: 'border-blue-400 bg-blue-50 dark:bg-blue-950/20',
  pending: 'border-gray-200 bg-gray-50 dark:bg-gray-800/20',
}

const statusBadge: Record<Status, string> = {
  green: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  yellow: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  red: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  loading: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  pending: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
}

export function StageCard({ stageNumber, title, icon, questions, data, status, renderData }: StageCardProps) {
  const [expanded, setExpanded] = useState(true)

  return (
    <div className={`border-l-4 rounded-lg shadow-sm overflow-hidden ${statusColors[status]}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-6 py-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Stage {stageNumber}</span>
            <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {status === 'loading' && (
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          )}
          {status !== 'loading' && status !== 'pending' && (
            <span className={`text-xs px-2 py-1 rounded-full font-medium uppercase ${statusBadge[status]}`}>
              {status}
            </span>
          )}
          <span className="text-gray-400">{expanded ? '▲' : '▼'}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-6 pb-6 grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">
              Framework Questions
            </h4>
            <ul className="space-y-1">
              {questions.map((q, i) => (
                <li key={i} className="text-sm text-gray-700 dark:text-gray-300 flex gap-2">
                  <span className="text-gray-400 flex-shrink-0">•</span>
                  {q}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">
              Analysis
            </h4>
            {status === 'loading' && (
              <div className="space-y-2 animate-pulse">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
              </div>
            )}
            {status === 'pending' && (
              <p className="text-sm text-gray-400 italic">Waiting for previous stages...</p>
            )}
            {data && renderData && renderData(data)}
            {data && !renderData && (
              <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {JSON.stringify(data, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
