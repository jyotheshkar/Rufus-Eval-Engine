// ScoreCard — displays a single eval dimension score with label

interface ScoreCardProps {
  title: string
  value: number | string
  subtitle?: string
  accent?: boolean
}

export function ScoreCard({ title, value, subtitle, accent = false }: ScoreCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <p className="text-sm text-gray-500 uppercase tracking-wide">{title}</p>
      <p className={`text-3xl font-bold mt-2 ${accent ? 'text-red-600' : 'text-gray-900'}`}>
        {value}
      </p>
      {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
    </div>
  )
}
