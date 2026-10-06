import { useNavigate } from 'react-router-dom'
import { clearAuth, getStoredUser } from '../lib/auth'

export function AccountPage() {
  const navigate = useNavigate()
  const user = getStoredUser()

  if (!user) {
    navigate('/login', { replace: true })
    return null
  }

  const logout = () => { clearAuth(); navigate('/login', { replace: true }) }

  return (
    <main className="auth-page">
      <section className="account-card ra-card">
        <div className="account-top"><div><div className="ra-eyebrow">Authenticated account</div><h1>{user.full_name}</h1></div><button className="ra-button ra-button-secondary" onClick={logout}>Sign out</button></div>
        <div className="account-grid">
          <div><span>Role</span><strong>{user.role === 'BUSINESS_OWNER' ? 'Business Owner' : 'Administrator'}</strong></div>
          <div><span>Email</span><strong>{user.email}</strong></div>
          <div><span>Business</span><strong>{user.business_id ? `Business #${user.business_id}` : 'Platform administration'}</strong></div>
        </div>
        <div className="account-placeholder">{user.role === 'ADMIN' ? <><h2>Admin workspace</h2><p>Manage all businesses, owners, subscriptions, billing and platform settings.</p><button className="ra-button ra-button-primary" onClick={() => navigate('/admin')}>Open admin workspace</button></> : <><h2>Owner workspace</h2><p>Your authenticated business workspace includes dashboard, feedback, notifications, settings and billing management.</p><button className="ra-button ra-button-primary" onClick={() => navigate('/owner')}>Open business dashboard</button></>}</div>
      </section>
    </main>
  )
}
