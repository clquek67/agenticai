interface MetricRowProps {
  label: string
  value: string | number | null | undefined
  good?: boolean | null
}

export function MetricRow({ label, value, good }: MetricRowProps) {
  const displayValue = value === null || value === undefined ? 'N/A' : String(value)
  return (
    <div className="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-700 last:border-0">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <div className="flex items-center gap-1">
        <span className="text-sm font-medium text-gray-900 dark:text-white">{displayValue}</span>
        {good === true && <span className="text-green-500 text-xs">✓</span>}
        {good === false && <span className="text-red-500 text-xs">✗</span>}
      </div>
    </div>
  )
}
