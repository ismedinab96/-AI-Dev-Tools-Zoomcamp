import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { VoteButton } from '../src/components/VoteButton'

it('disables button while voting', async () => {
  let resolveFn: (() => void) | null = null
  const promise = new Promise<void>((resolve) => {
    resolveFn = resolve
  })

  render(<VoteButton onVote={() => promise} />)
  const btn = screen.getByRole('button', { name: 'Vote' })
  fireEvent.click(btn)
  expect(screen.getByRole('button', { name: 'Voting...' })).toBeDisabled()
  resolveFn!()
})
