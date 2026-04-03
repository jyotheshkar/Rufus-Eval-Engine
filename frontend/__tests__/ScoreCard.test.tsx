// ScoreCard.test.tsx — unit tests for ScoreCard component
import { render, screen } from '@testing-library/react'
import { ScoreCard } from '../components/ScoreCard'

describe('ScoreCard', () => {
  it('renders title and value', () => {
    render(<ScoreCard title="Helpfulness" value={8.5} />)
    expect(screen.getByText('Helpfulness')).toBeInTheDocument()
    expect(screen.getByText('8.5')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(<ScoreCard title="Overall" value={7.2} subtitle="Out of 10" />)
    expect(screen.getByText('Out of 10')).toBeInTheDocument()
  })

  it('applies red color class when accent=true', () => {
    render(<ScoreCard title="Score" value={9} accent={true} />)
    const valueEl = screen.getByText('9')
    expect(valueEl).toHaveClass('text-red-600')
  })

  it('applies gray color class when accent is false', () => {
    render(<ScoreCard title="Score" value={9} accent={false} />)
    const valueEl = screen.getByText('9')
    expect(valueEl).toHaveClass('text-gray-900')
  })
})
