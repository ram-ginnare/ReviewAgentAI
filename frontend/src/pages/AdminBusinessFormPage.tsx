import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { adminBusinessApi } from '../lib/api'
import type { AdminBusiness, AdminOwnerOption } from '../types/api'

const empty = {slug:'',name:'',description:'',category:'',logo_url:'',google_review_pc_url:'',google_review_mob_url:'',status:'ACTIVE',prefer_ai_comments:true,brand_primary_color:'#2563eb',brand_secondary_color:'#0f172a',welcome_message:'',nfc_enabled:false,qr_enabled:true,customer_settings:{}} 

export function AdminBusinessFormPage(){
  const {id}=useParams(); const editing=Boolean(id); const navigate=useNavigate()
  const [form,setForm]=useState<any>(empty); const [owners,setOwners]=useState<AdminOwnerOption[]>([]); const [ownerId,setOwnerId]=useState(''); const [message,setMessage]=useState(''); const [saving,setSaving]=useState(false)
  useEffect(()=>{(async()=>{try{const list=await adminBusinessApi.list();setOwners(list.owners); if(id){const b=await adminBusinessApi.get(Number(id));setForm({...b,description:b.description||'',category:b.category||'',logo_url:b.logo_url||'',welcome_message:b.welcome_message||''});setOwnerId(b.owner_id?String(b.owner_id):'')}}catch(e){setMessage(e instanceof Error?e.message:'Unable to load business.')}})()},[id])
  const set=(k:string,v:unknown)=>setForm((x:any)=>({...x,[k]:v}))
  const save=async()=>{setSaving(true);setMessage('');try{const body={...form,owner_id:ownerId?Number(ownerId):null,customer_settings:form.customer_settings||{},social_links:form.social_links||[]};delete body.id;delete body.owner_id; // re-add explicitly below
    const payload={...body,owner_id:ownerId?Number(ownerId):null}; const result=editing?await adminBusinessApi.update(Number(id),payload):await adminBusinessApi.create(payload);setMessage('Business saved successfully.');setTimeout(()=>navigate('/admin'),350);return result}catch(e){setMessage(e instanceof Error?e.message:'Unable to save business.')}finally{setSaving(false)}}
  return <main className="page-shell"><section className="page-card"><div className="page-heading"><div><p className="eyebrow">ADMIN WORKSPACE</p><h1>{editing?'Edit business':'Add business'}</h1><p>Manage the business profile and customer-facing configuration.</p></div><button className="secondary-button" onClick={()=>navigate('/admin')}>Back</button></div>{message&&<div className="notice">{message}</div>}
    <div className="admin-form-grid">
      {([['name','Business name'],['slug','Slug'],['category','Category'],['logo_url','Logo URL'],['google_review_pc_url','Google review PC URL'],['google_review_mob_url','Google review mobile URL'],['brand_primary_color','Primary brand color'],['brand_secondary_color','Secondary brand color']] as const).map(([k,l])=><label key={k}>{l}<input value={form[k]??''} onChange={e=>set(k,e.target.value)}/></label>)}
      <label>Owner<select value={ownerId} onChange={e=>setOwnerId(e.target.value)}><option value="">Unassigned</option>{owners.filter(o=>o.is_active).map(o=><option key={o.id} value={o.id}>{o.full_name} — {o.email}</option>)}</select></label>
      <label>Status<select value={form.status} onChange={e=>set('status',e.target.value)}><option value="ACTIVE">ACTIVE</option><option value="INACTIVE">INACTIVE</option></select></label>
      <label className="wide">Description<textarea value={form.description??''} onChange={e=>set('description',e.target.value)}/></label>
      <label className="wide">Welcome message<textarea value={form.welcome_message??''} onChange={e=>set('welcome_message',e.target.value)}/></label>
      <label className="check-label"><input type="checkbox" checked={!!form.prefer_ai_comments} onChange={e=>set('prefer_ai_comments',e.target.checked)}/> Prefer AI comments</label>
      <label className="check-label"><input type="checkbox" checked={!!form.qr_enabled} onChange={e=>set('qr_enabled',e.target.checked)}/> QR enabled</label>
      <label className="check-label"><input type="checkbox" checked={!!form.nfc_enabled} onChange={e=>set('nfc_enabled',e.target.checked)}/> NFC enabled</label>
    </div>
    <div className="form-actions"><button className="primary-button" disabled={saving} onClick={save}>{saving?'Saving…':'Save business'}</button><button className="secondary-button" onClick={()=>navigate('/admin')}>Cancel</button></div>
  </section></main>
}
