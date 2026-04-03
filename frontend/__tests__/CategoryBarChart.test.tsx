// CategoryBarChart.test.tsx — unit tests for CategoryBarChart component

jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Bar: () => <div data-testid="recharts-bar" />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
}))

import React from 'react'
import { render, screen } from '@testing-library/react'
import { CategoryBarChart } from '../components/CategoryBarChart'
import type { CategoryStat } from '../lib/types'

describe('CategoryBarChart', () => {
  it('renders "No data available" when data is empty', () => {
    render(<CategoryBarChart data={[]} />)
    expect(screen.getByText('No data available')).toBeInTheDocument()
  })

  it('renders without crashing with sample data', () => {
    const data: CategoryStat[] = [
      { category: 'Electronics', avg_overall: 8.2, count: 30 },
      { category: 'Books', avg_overall: 7.5, count: 20 },
    ]
    render(<CategoryBarChart data={data} />)
    expect(screen.getByTestId('recharts-bar')).toBeInTheDocument()
  })
})
