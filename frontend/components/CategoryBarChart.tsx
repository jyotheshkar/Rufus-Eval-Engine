// CategoryBarChart — horizontal bar chart of scores by product category
'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { CategoryStat } from '@/lib/types'

interface CategoryBarChartProps {
  data: CategoryStat[]
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

export function CategoryBarChart({ data }: CategoryBarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[140px] text-gray-300 text-sm">
        No data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={140}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
      >
        <XAxis type="number" domain={[0, 10]} tick={{ fontSize: 10, fill: '#aaa' }} axisLine={{ stroke: '#e5e7eb' }} tickLine={false} />
        <YAxis type="category" dataKey="category" tick={{ fontSize: 10, fill: '#666' }} axisLine={false} tickLine={false} width={100} />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f5f5f5' }} />
        <Bar dataKey="avg_overall" fill="#222" name="Avg Overall" radius={[0, 2, 2, 0]} barSize={8} />
      </BarChart>
    </ResponsiveContainer>
  )
}
