// ScoreCard — KPI card for eval dimension scores

interface ScoreCardProps {
  title: string
  value: number | string
  subtitle?: string
  accent?: boolean
}

export function ScoreCard({ title, value, subtitle, accent = false }: ScoreCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-3">{title}</p>
      <p className={`text-2xl font-semibold tracking-tight ${accent ? 'text-red-600' : 'text-black'}`}>
        {value}
      </p>
      {subtitle && (
        <p className="text-[11px] text-gray-400 mt-1.5">{subtitle}</p>
      )}
    </div>
  )
}
