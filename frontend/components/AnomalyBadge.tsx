// AnomalyBadge — indicator for flagged anomalous eval results

interface AnomalyBadgeProps {
  count: number
}

export function AnomalyBadge({ count }: AnomalyBadgeProps) {
  if (count === 0) {
    return (
      <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-green-600">
        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
        All clear
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-red-600">
      <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
      {count} {count === 1 ? 'anomaly' : 'anomalies'}
    </span>
  )
}
