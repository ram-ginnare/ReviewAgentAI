import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminBusinessApi } from '../lib/api'
import type { AdminBusiness, AdminOwnerOption } from '../types/api'

export function AdminDashboardPage() {
  const navigate = useNavigate()
  const [businesses, setBusinesses] = useState<AdminBusiness[]>([])
  const [owners, setOwners] = useState<AdminOwnerOption[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('ALL')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const result = await adminBusinessApi.list()
      setBusinesses(result.businesses)
      setOwners(result.owners)
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Unable to load businesses.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const filtered = useMemo(() => businesses.filter((b) => {
    const q = search.trim().toLowerCase()
    const matchesSearch = !q || [b.name, b.slug, b.owner_email || '', b.owner_name || ''].some(v => v.toLowerCase().includes(q))
    const matchesStatus = status === 'ALL' || b.status === status
    return matchesSearch && matchesStatus
  }), [businesses, search, status])

  const toggle = async (business: AdminBusiness) => {
    try {
      const updated = await adminBusinessApi.toggleStatus(business.id, business.status !== 'ACTIVE')
      setBusinesses(items => items.map(item => item.id === updated.id ? updated : item))
      setMessage(`${updated.name} is now ${updated.status.toLowerCase()}.`)
    } catch (e) { setMessage(e instanceof Error ? e.message : 'Unable to update business status.') }
  }

  return <main className="page-shell">
    <section className="page-card">
      <div className="page-heading admin-heading">
        <div><p className="eyebrow">ADMIN WORKSPACE</p><h1>Business administration</h1><p>Manage all businesses, owners, subscriptions and customer-facing settings.</p></div>
        <div className="admin-actions">
          <button className="secondary-button" onClick={() => navigate('/admin/billing')}>Subscription & billing</button>
          <button className="primary-button" onClick={() => navigate('/admin/businesses/new')}>Add business</button>
        </div>
      </div>
      {message && <div className="notice">{message}</div>}

      <div className="admin-filters">
        <input aria-label="Search businesses" placeholder="Search business or owner" value={search} onChange={e => setSearch(e.target.value)} />
        <select aria-label="Filter business status" value={status} onChange={e => setStatus(e.target.value)}>
          <option value="ALL">All statuses</option><option value="ACTIVE">Active</option><option value="INACTIVE">Inactive</option>
        </select>
        <span>{filtered.length} of {businesses.length} businesses</span>
      </div>

      {loading ? <p>Loading businesses…</p> : <div className="table-wrap"><table className="data-table admin-business-table"><thead><tr><th>Business</th><th>Owner</th><th>Plan</th><th>Status</th><th>Reviews</th><th>Complaints</th><th>Rating</th><th>Actions</th></tr></thead>
        <tbody>{filtered.map(b => <tr key={b.id}>
          <td><strong>{b.name}</strong><small>{b.slug}</small></td>
          <td>{b.owner_name || 'Unassigned'}<small>{b.owner_email || ''}</small></td>
          <td>{b.plan_name}<small>{b.subscription_status}</small></td>
          <td><span className={`status-pill ${b.status === 'ACTIVE' ? 'status-active' : 'status-inactive'}`}>{b.status}</span></td>
          <td>{b.review_count}</td><td>{b.complaint_count}</td><td>{b.average_rating ?? '—'}</td>
          <td><div className="row-actions"><button className="secondary-button" onClick={() => navigate(`/admin/businesses/${b.id}`)}>Edit</button><button className="secondary-button" onClick={() => toggle(b)}>{b.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}</button></div></td>
        </tr>)}
        {!filtered.length && <tr><td colSpan={8}>No businesses match the current filters.</td></tr>}
        </tbody></table></div>}

      <div className="admin-summary"><div><strong>{businesses.length}</strong><span>Total businesses</span></div><div><strong>{businesses.filter(b=>b.status==='ACTIVE').length}</strong><span>Active businesses</span></div><div><strong>{owners.filter(o=>o.is_active).length}</strong><span>Active owners</span></div></div>
    </section>
  </main>
}
