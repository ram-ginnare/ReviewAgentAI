import { FormEvent, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api, ApiClientError } from '../lib/api'
import { storeAuth } from '../lib/auth'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const session = await api.login(email, password)
      storeAuth(session)
      const target = (location.state as { from?: string } | null)?.from || '/account'
      navigate(target, { replace: true })
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Unable to sign in. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card ra-card">
        <div className="auth-mark">R</div>
        <div className="ra-eyebrow">ReviewAgentAI</div>
        <h1>Welcome back</h1>
        <p className="auth-subtitle">Sign in to manage your ReviewAgentAI account.</p>
        <form onSubmit={submit} className="auth-form">
          <label>Email<input className="ra-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required /></label>
          <label>Password<input className="ra-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" minLength={8} required /></label>
          {error && <div className="auth-error" role="alert">{error}</div>}
          <button className="ra-button ra-button-primary auth-submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
        </form>
        <p className="auth-note">Customer review links continue to work without an account.</p>
      </section>
    </main>
  )
}
