// ScoreTrendChart.test.tsx — unit tests for ScoreTrendChart component

jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => <div data-testid="recharts-line" />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  ReferenceLine: () => <div />,
}))

import React from 'react'
import { render, screen } from '@testing-library/react'
import { ScoreTrendChart } from '../components/ScoreTrendChart'
import type { TrendPoint } from '../lib/types'

describe('ScoreTrendChart', () => {
  it('renders "No trend data yet" when data is empty', () => {
    render(<ScoreTrendChart data={[]} />)
    expect(screen.getByText('No trend data yet')).toBeInTheDocument()
  })

  it('renders without crashing with sample data', () => {
    const data: TrendPoint[] = [
      { date: '2024-01-01', avg_overall: 7.5 },
      { date: '2024-01-02', avg_overall: 8.0 },
    ]
    render(<ScoreTrendChart data={data} />)
    expect(screen.getByTestId('recharts-line')).toBeInTheDocument()
  })
})
