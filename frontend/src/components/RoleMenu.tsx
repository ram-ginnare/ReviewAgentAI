import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { clearAuth, getStoredUser } from '../lib/auth'
import styles from './RoleMenu.module.css'

export function RoleMenu() {
  const navigate = useNavigate()
  const location = useLocation()
  const user = getStoredUser()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false)
    }
    const escape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('keydown', escape)
    }
  }, [])

  if (!user) return null

  const isAdmin = user.role === 'ADMIN'
  const items = isAdmin
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

  const logout = () => {
    clearAuth()
    setOpen(false)
    navigate('/login', { replace: true })
  }

  return (
    <div className={styles.menu} ref={ref}>
      <button
        type="button"
        className={styles.trigger}
        aria-label="Open menu"
        aria-expanded={open}
        aria-haspopup="dialog"
        onClick={() => setOpen((value) => !value)}
      >
        <span className={styles.lines} aria-hidden="true"><i /><i /><i /></span>
        <span className={styles.label}>Menu</span>
      </button>

      {open && (
        <>
          <button
            type="button"
            className={styles.backdrop}
            aria-label="Close menu"
            onClick={() => setOpen(false)}
          />
          <aside className={styles.panel} aria-label={isAdmin ? 'Admin menu' : 'Business owner menu'}>
            <div className={styles.panelHeader}>
              <div className={styles.user}>
                <strong>{isAdmin ? 'Administrator' : 'Business Owner'}</strong>
                <span>{user.email}</span>
              </div>
              <button
                type="button"
                className={styles.close}
                aria-label="Close menu"
                onClick={() => setOpen(false)}
              >
                ×
              </button>
            </div>

            <nav className={styles.nav} aria-label="Navigation">
              {items.map((item) => {
                const active = location.pathname === item.path || (item.path === '/admin' && location.pathname.startsWith('/admin/businesses/'))
                return (
                  <button
                    key={item.path}
                    type="button"
                    className={`${styles.item}${active ? ` ${styles.active}` : ''}`}
                    onClick={() => { setOpen(false); navigate(item.path) }}
                  >
                    {item.label}
                  </button>
                )
              })}
            </nav>

            <div className={styles.divider} />
            <button type="button" className={`${styles.item} ${styles.danger}`} onClick={logout}>
              Log out
            </button>
          </aside>
        </>
      )}
    </div>
  )
}
