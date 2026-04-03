// AnomalyBadge — visual indicator shown when an eval result is flagged as anomalous

interface AnomalyBadgeProps {
  count: number
}

export function AnomalyBadge({ count }: AnomalyBadgeProps) {
  if (count === 0) {
    return (
      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700">
        No anomalies
      </span>
    )
  }
  return (
    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-700">
      {count} anomalies detected
    </span>
  )
}
