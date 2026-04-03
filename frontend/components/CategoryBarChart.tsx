// CategoryBarChart — Recharts bar chart of scores broken down by product category
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

export function CategoryBarChart({ data }: CategoryBarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-400">
        No data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 5, right: 20, left: 100, bottom: 5 }}
      >
        <XAxis type="number" domain={[0, 10]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
        <YAxis type="category" dataKey="category" tick={{ fontSize: 12 }} stroke="#9ca3af" width={90} />
        <Tooltip />
        <Bar dataKey="avg_overall" fill="#DC2626" name="Avg Overall" />
      </BarChart>
    </ResponsiveContainer>
  )
}
