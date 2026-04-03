// AnomalyBadge.test.tsx — unit tests for AnomalyBadge component
import { render, screen } from '@testing-library/react'
import { AnomalyBadge } from '../components/AnomalyBadge'

describe('AnomalyBadge', () => {
  it('shows "No anomalies" when count is 0', () => {
    render(<AnomalyBadge count={0} />)
    expect(screen.getByText('No anomalies')).toBeInTheDocument()
  })

  it('shows count when count is positive', () => {
    render(<AnomalyBadge count={5} />)
    expect(screen.getByText('5 anomalies detected')).toBeInTheDocument()
  })

  it('shows count=1 correctly', () => {
    render(<AnomalyBadge count={1} />)
    expect(screen.getByText('1 anomalies detected')).toBeInTheDocument()
  })

  it('applies red styling when count > 0', () => {
    render(<AnomalyBadge count={3} />)
    const badge = screen.getByText('3 anomalies detected')
    expect(badge).toHaveClass('text-red-700')
  })

  it('applies gray styling when count = 0', () => {
    render(<AnomalyBadge count={0} />)
    const badge = screen.getByText('No anomalies')
    expect(badge).toHaveClass('text-gray-700')
  })
})
