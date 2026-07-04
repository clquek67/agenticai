type StepStatus = 'complete' | 'active' | 'pending'

interface StepperProps {
  currentStage: number
  totalStages?: number
}

const stages = [
  'Business',
  'Financials',
  'Valuation',
  'Promoter',
  'Industry',
  'Verdict',
]

export function Stepper({ currentStage }: StepperProps) {
  return (
    <div className="flex items-center justify-center gap-1 flex-wrap">
      {stages.map((label, i) => {
        const stage = i + 1
        const status: StepStatus =
          stage < currentStage ? 'complete' : stage === currentStage ? 'active' : 'pending'

        return (
          <div key={stage} className="flex items-center gap-1">
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
                status === 'complete'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : status === 'active'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
              }`}
            >
              <span
                className={`w-4 h-4 rounded-full flex items-center justify-center text-xs ${
                  status === 'complete'
                    ? 'bg-green-500 text-white'
                    : status === 'active'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-500'
                }`}
              >
                {status === 'complete' ? '✓' : stage}
              </span>
              {label}
            </div>
            {i < stages.length - 1 && (
              <div className={`w-4 h-px ${stage < currentStage ? 'bg-green-400' : 'bg-gray-200 dark:bg-gray-600'}`} />
            )}
          </div>
        )
      })}
    </div>
  )
}
