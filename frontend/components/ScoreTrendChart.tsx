// ScoreTrendChart — line chart showing score trends over time
'use client'

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import type { TrendPoint } from '@/lib/types'

interface ScoreTrendChartProps {
  data: TrendPoint[]
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: { value: number }[]; label?: string }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded px-3 py-2 shadow-sm text-xs">
        <p className="text-gray-400 mb-0.5">{label}</p>
        <p className="font-semibold text-black">{payload[0].value.toFixed(2)} / 10</p>
      </div>
    )
  }
  return null
}

export function ScoreTrendChart({ data }: ScoreTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[240px] text-gray-300 text-sm">
        No trend data yet
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eee" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: '#aaa' }}
          axisLine={{ stroke: '#e5e7eb' }}
          tickLine={false}
        />
        <YAxis
          domain={[0, 10]}
          tick={{ fontSize: 11, fill: '#aaa' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine y={7} stroke="#e5e7eb" strokeDasharray="6 3" />
        <Line
          type="monotone"
          dataKey="avg_overall"
          stroke="#111"
          strokeWidth={1.5}
          dot={{ r: 2.5, fill: '#111', strokeWidth: 0 }}
          activeDot={{ r: 4, fill: '#111', stroke: '#ddd', strokeWidth: 2 }}
          name="Avg Overall"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
