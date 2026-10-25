// AnomalyBadge.test.tsx — unit tests for AnomalyBadge component
import { render, screen } from '@testing-library/react'
import { AnomalyBadge } from '../components/AnomalyBadge'

describe('AnomalyBadge', () => {
  it('shows "All clear" when count is 0', () => {
    render(<AnomalyBadge count={0} />)
    expect(screen.getByText('All clear')).toBeInTheDocument()
  })

  it('shows count when count is positive', () => {
    render(<AnomalyBadge count={5} />)
    expect(screen.getByText('5 anomalies')).toBeInTheDocument()
  })

  it('shows count=1 correctly', () => {
    render(<AnomalyBadge count={1} />)
    expect(screen.getByText('1 anomaly')).toBeInTheDocument()
  })

  it('applies red styling when count > 0', () => {
    render(<AnomalyBadge count={3} />)
    const badge = screen.getByText('3 anomalies')
    expect(badge).toHaveClass('text-red-600')
  })

  it('applies green styling when count = 0', () => {
    render(<AnomalyBadge count={0} />)
    const badge = screen.getByText('All clear')
    expect(badge).toHaveClass('text-green-600')
  })
})
