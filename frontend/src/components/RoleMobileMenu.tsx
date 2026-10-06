import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { clearAuth, getStoredUser } from '../lib/auth'

type MenuItem = { label: string; path: string }

export function RoleMobileMenu() {
  const navigate = useNavigate()
  const location = useLocation()
  const user = getStoredUser()
  const [open, setOpen] = useState(false)

  const isAdmin = user?.role === 'ADMIN'
  const items: MenuItem[] = isAdmin
    ? [
        { label: 'Admin workspace', path: '/admin' },
        { label: 'Add business', path: '/admin/businesses/new' },
        { label: 'Subscription & billing', path: '/admin/billing' },
        { label: 'My account', path: '/account' },
      ]
    : [
        { label: 'Owner dashboard', path: '/owner' },
        { label: 'My account', path: '/account' },
      ]

  useEffect(() => {
    setOpen(false)
  }, [location.pathname])

  if (!user) return null

  const logout = () => {
    clearAuth()
    setOpen(false)
    navigate('/login', { replace: true })
  }

  return (
    <div className="role-menu">
      <button
        type="button"
        className="role-menu-button"
        aria-label="Open menu"
        aria-expanded={open}
        onClick={() => setOpen(value => !value)}
      >
        <span />
        <span />
        <span />
      </button>

      {open && (
        <>
          <button className="role-menu-backdrop" aria-label="Close menu" onClick={() => setOpen(false)} />
          <nav className="role-menu-panel" aria-label={isAdmin ? 'Admin menu' : 'Owner menu'}>
            <div className="role-menu-title">
              <div>
                <strong>{isAdmin ? 'Admin menu' : 'Owner menu'}</strong>
                <small>{user.full_name || user.email}</small>
              </div>
              <button type="button" className="role-menu-close" onClick={() => setOpen(false)} aria-label="Close menu">×</button>
            </div>

            <div className="role-menu-links">
              {items.map(item => (
                <button
                  type="button"
                  key={item.path}
                  className={`role-menu-link ${location.pathname === item.path ? 'active' : ''}`}
                  onClick={() => navigate(item.path)}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <button type="button" className="role-menu-logout" onClick={logout}>Log out</button>
          </nav>
        </>
      )}
    </div>
  )
}
