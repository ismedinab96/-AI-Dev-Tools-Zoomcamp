import React from 'react'

type Props = {
  disabled?: boolean
  onVote: () => Promise<void>
}

export function VoteButton({ disabled, onVote }: Props) {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  async function handleClick() {
    setError(null)
    setLoading(true)
    try {
      await onVote()
    } catch (e: any) {
      setError(String(e.message ?? e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button disabled={disabled || loading} onClick={handleClick}>
        {loading ? 'Voting...' : 'Vote'}
      </button>
      {error ? <p role="alert">{error}</p> : null}
    </div>
  )
}
