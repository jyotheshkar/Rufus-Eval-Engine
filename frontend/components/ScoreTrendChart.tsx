// ScoreTrendChart — Recharts line chart showing score trends over time
'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { TrendPoint } from '@/lib/types'

interface ScoreTrendChartProps {
  data: TrendPoint[]
}

export function ScoreTrendChart({ data }: ScoreTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-400">
        No data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#9ca3af" />
        <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="avg_overall"
          stroke="#DC2626"
          strokeWidth={2}
          dot={false}
          name="Avg Overall"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
