// AnswerTable.test.tsx — unit tests for AnswerTable component
import { render, screen } from '@testing-library/react'
import { AnswerTable } from '../components/AnswerTable'
import type { EvalResult } from '../lib/types'

const mockEval: EvalResult = {
  id: 'eval_001',
  timestamp: '2024-01-15T10:00:00Z',
  question_id: 'q_001',
  question_text: 'What is the best laptop for video editing?',
  category: 'Electronics',
  difficulty: 'medium',
  is_adversarial: false,
  adversarial_category: null,
  rufus_answer: 'I recommend the MacBook Pro...',
  score_helpfulness: 8.0,
  score_accuracy: 8.5,
  score_hallucination: 9.0,
  score_safety: 10.0,
  score_overall: 8.9,
  anomaly_flagged: false,
  anomaly_reason: null,
}

describe('AnswerTable', () => {
  it('renders table headers', () => {
    render(
      <AnswerTable
        evals={[mockEval]}
        page={1}
        total={1}
        limit={20}
        onPageChange={() => {}}
      />
    )
    expect(screen.getByText('Question')).toBeInTheDocument()
    expect(screen.getByText('Category')).toBeInTheDocument()
    expect(screen.getByText('Overall')).toBeInTheDocument()
  })

  it('shows "no data" message when evals is empty', () => {
    render(
      <AnswerTable
        evals={[]}
        page={1}
        total={0}
        limit={20}
        onPageChange={() => {}}
      />
    )
    expect(screen.getByText('No eval results found.')).toBeInTheDocument()
  })

  it('renders eval data in the table', () => {
    render(
      <AnswerTable
        evals={[mockEval]}
        page={1}
        total={1}
        limit={20}
        onPageChange={() => {}}
      />
    )
    expect(screen.getByText('Electronics')).toBeInTheDocument()
    expect(screen.getByText('8.9')).toBeInTheDocument()
  })

  it('renders pagination controls', () => {
    render(
      <AnswerTable
        evals={[mockEval]}
        page={1}
        total={50}
        limit={20}
        onPageChange={() => {}}
      />
    )
    expect(screen.getByText('Previous')).toBeInTheDocument()
    expect(screen.getByText('Next')).toBeInTheDocument()
  })
})
