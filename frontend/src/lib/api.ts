import { getAuthToken } from './auth'
import type {
  ApiError,
  Business,
  CustomerAccess,
  GoogleSelectionResponse,
  PositiveReviewResponse,
  PrivateFeedbackResponse,
  RatingResponse,
  ReviewFlowResponse,
} from '../types/api'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')

export class ApiClientError extends Error {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.code = code
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {}),
        ...(options.headers || {}),
      },
    })
  } catch {
    throw new ApiClientError('We could not connect to the review service. Please check your connection and try again.', 0, 'NETWORK_ERROR')
  }

  if (!response.ok) {
    let payload: ApiError = {}
    try {
      payload = (await response.json()) as ApiError
    } catch {
      // Keep a friendly fallback when the server did not return JSON.
    }
    let message = 'Something went wrong. Please try again.'
    if (typeof payload.detail === 'string') message = payload.detail
    if (Array.isArray(payload.detail) && payload.detail[0]?.msg) message = payload.detail[0].msg
    throw new ApiClientError(message, response.status, payload.code)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export const api = {
  login: (email: string, password: string) =>
    request<import('../types/api').LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  getMe: () => request<import('../types/api').User>('/auth/me'),

  changePassword: (currentPassword: string, newPassword: string) =>
    request<void>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }),

  getBusiness: (slug: string) => request<Business>(`/businesses/${encodeURIComponent(slug)}`),

  createAccess: (slug: string, source: 'nfc' | 'qr' | 'direct') =>
    request<CustomerAccess>(`/access/${encodeURIComponent(slug)}`, {
      method: 'POST',
      body: JSON.stringify({ source }),
    }),

  getFlow: (sessionId: string) =>
    request<ReviewFlowResponse>(`/reviews/session/${encodeURIComponent(sessionId)}/flow`),

  rateSession: (sessionId: string, rating: number) =>
    request<RatingResponse>(`/reviews/session/${encodeURIComponent(sessionId)}/rating`, {
      method: 'POST',
      body: JSON.stringify({ rating }),
    }),

  generatePositiveReviews: (
    sessionId: string,
    input: {
      professional_staff: boolean
      reliable_service: boolean
      good_ambiance: boolean
      affordable_pricing: boolean
      customer_comment?: string
    },
  ) =>
    request<PositiveReviewResponse>(`/reviews/session/${encodeURIComponent(sessionId)}/positive-reviews`, {
      method: 'POST',
      body: JSON.stringify(input),
    }),

  selectGoogleReview: (sessionId: string, reviewId: number, finalReviewText?: string) =>
    request<GoogleSelectionResponse>(`/reviews/session/${encodeURIComponent(sessionId)}/google-review/select`, {
      method: 'POST',
      body: JSON.stringify({ review_id: reviewId, ...(finalReviewText ? { final_review_text: finalReviewText } : {}) }),
    }),

  submitPrivateFeedback: (sessionId: string, comments: string) =>
    request<PrivateFeedbackResponse>(`/reviews/session/${encodeURIComponent(sessionId)}/private-feedback`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    }),

  recordEvent: (
    slug: string,
    eventType: string,
    rating?: number,
    eventMetadata?: Record<string, unknown>,
  ) =>
    request(`/events/business/${encodeURIComponent(slug)}`, {
      method: 'POST',
      body: JSON.stringify({ event_type: eventType, rating, event_metadata: eventMetadata }),
    }).catch(() => undefined),

  trackSocialClick: (slug: string, socialLinkId: number, sessionId?: string) =>
    request(`/businesses/${encodeURIComponent(slug)}/social-links/${socialLinkId}/click`, {
      method: 'POST',
      body: JSON.stringify({}),
      headers: sessionId ? { 'X-Review-Session-ID': sessionId } : undefined,
    }).catch(() => undefined),
}


// Backward-compatible named exports used by the customer landing page.
export const createCustomerAccess = (slug: string, source: 'nfc' | 'qr' | 'direct') =>
  api.createAccess(slug, source)

export const getBusiness = (slug: string) => api.getBusiness(slug)

export const recordSocialClick = (slug: string, socialLinkId: number, sessionId?: string) =>
  api.trackSocialClick(slug, socialLinkId, sessionId)

export const ownerApi = {
  dashboard:(days:number)=>request<import('../types/api').OwnerDashboard>(`/owner/dashboard?days=${days}`),
  notifications:(status?:string)=>request<import('../types/api').OwnerNotificationList>(`/owner/notifications${status?`?status=${status}`:''}`),
  complaintStatus:(id:number,status:string)=>request(`/owner/complaints/${id}?new_status=${status}`,{method:'PATCH'}),
  settings:()=>request<import('../types/api').BusinessSettings>('/owner/settings'),
  profile:(body:object)=>request<import('../types/api').BusinessSettings>('/owner/settings/profile',{method:'PUT',body:JSON.stringify(body)}),
  branding:(body:object)=>request<import('../types/api').BusinessSettings>('/owner/settings/branding',{method:'PUT',body:JSON.stringify(body)}),
  reviews:(body:object)=>request<import('../types/api').BusinessSettings>('/owner/settings/reviews',{method:'PUT',body:JSON.stringify(body)}),
  socialLinks:()=>request<import('../types/api').SocialLink[]>('/owner/social-links'),
  createSocial:(body:object)=>request<import('../types/api').SocialLink>('/owner/social-links',{method:'POST',body:JSON.stringify(body)}),
  updateSocial:(id:number,body:object)=>request<import('../types/api').SocialLink>(`/owner/social-links/${id}`,{method:'PUT',body:JSON.stringify(body)}),
  deleteSocial:(id:number)=>request<void>(`/owner/social-links/${id}`,{method:'DELETE'}),
  plans:()=>request<import('../types/api').Plan[]>('/billing/plans'),
  subscription:()=>request<import('../types/api').Subscription>('/billing/subscription'),
  checkout:(plan:string)=>request<any>('/billing/checkout',{method:'POST',body:JSON.stringify({plan})}),
  confirm:(paymentId:number,success=true)=>request<any>('/billing/confirm',{method:'POST',body:JSON.stringify({payment_id:paymentId,success})}),
  cancel:()=>request('/billing/cancel',{method:'POST'}),
  history:()=>request<import('../types/api').BillingHistoryItem[]>('/billing/history'),
  advancedAnalytics:(days:number)=>request<import('../types/api').AdvancedAnalytics>(`/owner/analytics?days=${days}`),
  exportUrl:(format:'csv'|'xlsx'|'pdf',days:number)=>`${API_BASE_URL}/owner/analytics/export.${format}?days=${days}`,
}

export const adminBillingApi = {
  plans: () => request<import('../types/api').AdminPlan[]>('/admin/billing/plans'),
  updatePlan: (code: string, body: object) => request<import('../types/api').AdminPlan>(`/admin/billing/plans/${encodeURIComponent(code)}`, { method: 'PUT', body: JSON.stringify(body) }),
  subscriptions: () => request<import('../types/api').AdminSubscription[]>('/admin/billing/subscriptions'),
  updateSubscription: (businessId: number, body: object) => request<import('../types/api').AdminSubscription>(`/admin/billing/subscriptions/${businessId}`, { method: 'PUT', body: JSON.stringify(body) }),
}

export const adminBusinessApi = {
  list: () => request<{businesses: import('../types/api').AdminBusiness[]; owners: import('../types/api').AdminOwnerOption[]}>('/admin/businesses'),
  get: (id:number) => request<import('../types/api').AdminBusiness>(`/admin/businesses/${id}`),
  create: (body:object) => request<import('../types/api').AdminBusiness>('/admin/businesses',{method:'POST',body:JSON.stringify(body)}),
  update: (id:number, body:object) => request<import('../types/api').AdminBusiness>(`/admin/businesses/${id}`,{method:'PUT',body:JSON.stringify(body)}),
  toggleStatus: (id:number, active:boolean) => request<import('../types/api').AdminBusiness>(`/admin/businesses/${id}/status?active=${active}`,{method:'PATCH'}),
}
