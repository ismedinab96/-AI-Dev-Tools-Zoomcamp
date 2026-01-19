import React from 'react'
import { AuthApi, ElectionsApi, Election, Candidate, Results } from '../api/client'
import { VoteButton } from '../components/VoteButton'

function useLocalStorage(key: string) {
  const [value, setValue] = React.useState<string | null>(() => localStorage.getItem(key))
  React.useEffect(() => {
    if (value === null) localStorage.removeItem(key)
    else localStorage.setItem(key, value)
  }, [key, value])
  return [value, setValue] as const
}

export function App() {
  const [token, setToken] = useLocalStorage('token')
  const [email, setEmail] = React.useState('admin@example.com')
  const [password, setPassword] = React.useState('admin123')
  const [me, setMe] = React.useState<any>(null)
  const [elections, setElections] = React.useState<Election[]>([])
  const [selected, setSelected] = React.useState<string | null>(null)
  const [candidates, setCandidates] = React.useState<Candidate[]>([])
  const [results, setResults] = React.useState<Results | null>(null)
  const [myVoteCandidateId, setMyVoteCandidateId] = React.useState<string | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    if (!token) return
    AuthApi.me(token)
      .then(setMe)
      .catch((e) => setError(String(e)))
  }, [token])

  async function refreshElections() {
    if (!token) return
    const rows = await ElectionsApi.list(token)
    setElections(rows)
    if (!selected && rows.length) setSelected(rows[0].id)
  }

  React.useEffect(() => {
    if (!token) return
    refreshElections().catch((e) => setError(String(e)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  React.useEffect(() => {
    if (!token || !selected) return
    Promise.all([
      ElectionsApi.candidates(token, selected),
      ElectionsApi.results(token, selected).catch(() => null),
      ElectionsApi.myVote(token, selected).catch(() => null),
    ])
      .then(([cands, res, myVote]) => {
        setCandidates(cands)
        setResults(res)
        setMyVoteCandidateId(myVote ? myVote.candidate_id : null)
      })
      .catch((e) => setError(String(e)))
  }, [token, selected])

  async function doLogin(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    const t = await AuthApi.login(email, password)
    setToken(t.access_token)
  }

  function logout() {
    setToken(null)
    setMe(null)
    setElections([])
    setSelected(null)
    setCandidates([])
    setResults(null)
    setMyVoteCandidateId(null)
  }

  if (!token) {
    return (
      <div style={{ padding: 16, maxWidth: 420 }}>
        <h1>College Mayor Elections</h1>
        <p>Login (dev accounts seeded on first run)</p>
        <ul>
          <li>Admin: admin@example.com / admin123</li>
          <li>Voter: voter@example.com / voter123</li>
        </ul>
        <form onSubmit={doLogin}>
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <br />
          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <br />
          <button type="submit">Login</button>
        </form>
        {error ? <pre>{error}</pre> : null}
      </div>
    )
  }

  return (
    <div style={{ padding: 16 }}>
      <header style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>College Mayor Elections</h1>
        <button onClick={() => refreshElections()}>Refresh</button>
        <button onClick={logout}>Logout</button>
      </header>
      <p>
        Signed in as <b>{me?.email}</b> ({me?.role})
      </p>

      {error ? <pre>{error}</pre> : null}

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 24 }}>
        <section>
          <h2>Elections</h2>
          <ul>
            {elections.map((e) => (
              <li key={e.id}>
                <button onClick={() => setSelected(e.id)} style={{ fontWeight: selected === e.id ? 'bold' : 'normal' }}>
                  {e.name} ({e.status})
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2>Election details</h2>
          {!selected ? <p>Select an election.</p> : null}

          {selected ? (
            <>
              <h3>Candidates</h3>
              <ul>
                {candidates.map((c) => (
                  <li key={c.id}>
                    <b>{c.full_name}</b>
                    <p>{c.manifesto}</p>
                    {myVoteCandidateId ? (
                      <p>Your vote: {myVoteCandidateId === c.id ? '✅ This candidate' : '—'}</p>
                    ) : (
                      <VoteButton
                        disabled={false}
                        onVote={async () => {
                          await ElectionsApi.vote(token, selected, c.id)
                          const myVote = await ElectionsApi.myVote(token, selected)
                          setMyVoteCandidateId(myVote.candidate_id)
                          const res = await ElectionsApi.results(token, selected)
                          setResults(res)
                        }}
                      />
                    )}
                  </li>
                ))}
              </ul>

              <h3>Results</h3>
              {results ? (
                <ol>
                  {results.totals.map((r) => (
                    <li key={r.candidate_id}>
                      {r.full_name}: {r.votes}
                    </li>
                  ))}
                </ol>
              ) : (
                <p>No results available (or you are not authorized).</p>
              )}
            </>
          ) : null}
        </section>
      </div>
    </div>
  )
}
