export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type TokenResponse = { access_token: string; token_type: string }
export type MeResponse = { id: string; email: string; role: 'ADMIN' | 'VOTER'; voter_type: 'STUDENT' | 'FACULTY'; is_eligible: boolean }
export type Election = { id: string; name: string; starts_at: string; ends_at: string; status: 'DRAFT' | 'OPEN' | 'CLOSED' }
export type Candidate = { id: string; election_id: string; full_name: string; manifesto: string; photo_url?: string | null }
export type MyVote = { election_id: string; candidate_id: string; created_at: string }
export type ResultsLine = { candidate_id: string; full_name: string; votes: number }
export type Results = { election_id: string; status: string; totals: ResultsLine[] }

async function api<T>(path: string, opts: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_URL}${path}`, { ...opts, headers: { ...headers, ...(opts.headers as any) } })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${text}`)
  }
  return (await res.json()) as T
}

export const AuthApi = {
  login: (email: string, password: string) => api<TokenResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  me: (token: string) => api<MeResponse>('/me', { method: 'GET' }, token),
}

export const ElectionsApi = {
  list: (token: string) => api<Election[]>('/elections', { method: 'GET' }, token),
  get: (token: string, electionId: string) => api<Election>(`/elections/${electionId}`, { method: 'GET' }, token),
  candidates: (token: string, electionId: string) => api<Candidate[]>(`/elections/${electionId}/candidates`, { method: 'GET' }, token),
  myVote: (token: string, electionId: string) => api<MyVote>(`/elections/${electionId}/my-vote`, { method: 'GET' }, token),
  vote: (token: string, electionId: string, candidateId: string) => api<{ ok: boolean }>(`/elections/${electionId}/vote`, { method: 'POST', body: JSON.stringify({ candidate_id: candidateId }) }, token),
  results: (token: string, electionId: string) => api<Results>(`/elections/${electionId}/results`, { method: 'GET' }, token),
}
