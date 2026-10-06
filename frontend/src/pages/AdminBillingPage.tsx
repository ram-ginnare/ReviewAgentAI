import { useEffect, useState } from 'react'
import { adminBillingApi } from '../lib/api'
import type { AdminPlan, AdminSubscription } from '../types/api'

const money = (paise: number) => `₹${(paise / 100).toLocaleString('en-IN')}`

export function AdminBillingPage() {
  const [plans, setPlans] = useState<AdminPlan[]>([])
  const [subs, setSubs] = useState<AdminSubscription[]>([])
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState<number | string | null>(null)

  const load = async () => {
    const [p, s] = await Promise.all([adminBillingApi.plans(), adminBillingApi.subscriptions()])
    setPlans(p)
    setSubs(s)
  }
  useEffect(() => { load().catch((e) => setMessage(e.message)) }, [])

  const savePlan = async (plan: AdminPlan) => {
    setSaving(`plan-${plan.code}`); setMessage('')
    try { await adminBillingApi.updatePlan(plan.code, plan); setMessage(`${plan.name} plan updated.`); await load() }
    catch (e) { setMessage(e instanceof Error ? e.message : 'Unable to update plan.') }
    finally { setSaving(null) }
  }

  const saveSub = async (sub: AdminSubscription) => {
    setSaving(sub.business_id); setMessage('')
    try {
      await adminBillingApi.updateSubscription(sub.business_id, {
        plan: sub.plan,
        status: sub.status,
        trial_ends_at: sub.trial_ends_at || null,
        current_period_start: sub.current_period_start || null,
        current_period_end: sub.current_period_end || null,
        cancel_at_period_end: sub.cancel_at_period_end,
      })
      setMessage(`${sub.business_name} subscription updated.`); await load()
    } catch (e) { setMessage(e instanceof Error ? e.message : 'Unable to update subscription.') }
    finally { setSaving(null) }
  }

  return <main className="page-shell">
    <section className="page-card">
      <div className="page-heading"><div><p className="eyebrow">ADMIN</p><h1>Subscription management</h1><p>Update plan pricing/limits and assign subscription details to businesses.</p></div></div>
      {message && <div className="notice">{message}</div>}

      <h2>Plan details</h2>
      <div className="table-wrap"><table className="data-table"><thead><tr><th>Plan</th><th>Price / month</th><th>Monthly reviews</th><th>Trial days</th><th>Active</th><th></th></tr></thead>
        <tbody>{plans.map((p, i) => <tr key={p.code}>
          <td><input value={p.name} onChange={e => setPlans(x => x.map((v,j)=>j===i?{...v,name:e.target.value}:v))} /></td>
          <td><input type="number" min="0" value={Math.round(p.price_paise/100)} onChange={e => setPlans(x => x.map((v,j)=>j===i?{...v,price_paise:Number(e.target.value)*100}:v))} /></td>
          <td><input type="number" min="1" value={p.monthly_review_limit} onChange={e => setPlans(x => x.map((v,j)=>j===i?{...v,monthly_review_limit:Number(e.target.value)}:v))} /></td>
          <td><input type="number" min="0" value={p.trial_days} onChange={e => setPlans(x => x.map((v,j)=>j===i?{...v,trial_days:Number(e.target.value)}:v))} /></td>
          <td><input type="checkbox" checked={p.is_active} onChange={e => setPlans(x => x.map((v,j)=>j===i?{...v,is_active:e.target.checked}:v))} /></td>
          <td><button className="primary-button" disabled={saving===`plan-${p.code}`} onClick={() => savePlan(p)}>{saving===`plan-${p.code}`?'Saving…':'Save'}</button></td>
        </tr>)}</tbody></table></div>

      <h2>Business subscriptions</h2>
      <div className="table-wrap"><table className="data-table"><thead><tr><th>Business</th><th>Owner</th><th>Plan</th><th>Status</th><th>Trial ends</th><th>Period ends</th><th>Cancel at period end</th><th></th></tr></thead>
        <tbody>{subs.map((s, i) => <tr key={s.business_id}>
          <td><strong>{s.business_name}</strong><small>{s.business_slug}</small></td><td>{s.owner_email || '—'}</td>
          <td><select value={s.plan} onChange={e => setSubs(x=>x.map((v,j)=>j===i?{...v,plan:e.target.value}:v))}>{plans.filter(p=>p.is_active).map(p=><option key={p.code} value={p.code}>{p.name}</option>)}</select></td>
          <td><select value={s.status} onChange={e => setSubs(x=>x.map((v,j)=>j===i?{...v,status:e.target.value}:v))}><option>TRIALING</option><option>ACTIVE</option><option>PAST_DUE</option><option>CANCELLED</option></select></td>
          <td><input type="datetime-local" value={s.trial_ends_at ? s.trial_ends_at.slice(0,16) : ''} onChange={e=>setSubs(x=>x.map((v,j)=>j===i?{...v,trial_ends_at:e.target.value?new Date(e.target.value).toISOString():null}:v))} /></td>
          <td><input type="datetime-local" value={s.current_period_end ? s.current_period_end.slice(0,16) : ''} onChange={e=>setSubs(x=>x.map((v,j)=>j===i?{...v,current_period_end:e.target.value?new Date(e.target.value).toISOString():null}:v))} /></td>
          <td><input type="checkbox" checked={s.cancel_at_period_end} onChange={e=>setSubs(x=>x.map((v,j)=>j===i?{...v,cancel_at_period_end:e.target.checked}:v))} /></td>
          <td><button className="primary-button" disabled={saving===s.business_id} onClick={()=>saveSub(s)}>{saving===s.business_id?'Saving…':'Update'}</button></td>
        </tr>)}</tbody></table></div>
    </section>
  </main>
}
