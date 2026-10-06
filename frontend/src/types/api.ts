export type SocialLink = {
  id: number
  platform: string
  url: string
  display_order: number
  enabled: boolean
}

export type Business = {
  id: number
  slug: string
  name: string
  logo_url: string | null
  description: string | null
  category: string | null
  google_review_pc_url: string
  google_review_mob_url: string
  status: string
  prefer_ai_comments: boolean
  created_at: string
  updated_at: string
  social_links: SocialLink[]
}

export type CustomerAccess = {
  session_id: string
  business_id: string
  business_slug: string
  business_name: string
  source: 'nfc' | 'qr' | 'direct'
  status: string
  created_at: string
}

export type RatingResponse = {
  session_id: string
  business_id: string
  rating: number
  status: string
  next_step: string
  updated_at: string
}

export type GeneratedReview = {
  id: number
  generated_review: string
  selected: boolean
  created_at: string
}

export type PositiveReviewResponse = {
  session_id: string
  business_id: number
  rating: number
  generation_source: 'groq' | 'fallback' | string
  selected_preferences: string[]
  customer_comment: string | null
  reviews: GeneratedReview[]
}

export type PrivateFeedbackResponse = {
  session_id: string
  business_id: string
  complaint_id: number
  rating: number
  status: string
  acknowledgement: string
  created_at: string
}

export type GoogleSelectionResponse = {
  session_id: string
  business_id: number
  rating: number
  selected_review_id: number
  review_text: string
  google_review_pc_url: string
  google_review_mob_url: string
  google_review_url: string
  device_type: 'desktop' | 'mobile' | string
  status: string
  updated_at: string
}

export type ReviewFlowResponse = {
  session_id: string
  business_id: string
  business_slug: string
  business_name: string
  status: string
  rating: number | null
  next_step: string
  expires_at: string
  expired: boolean
}

export type ApiError = {
  detail?: string | { msg?: string }[]
  code?: string
}


// Backward-compatible alias for the customer landing page API contract.
export type CustomerAccessResponse = CustomerAccess


export type User = {
  id: number
  email: string
  full_name: string
  role: 'ADMIN' | 'BUSINESS_OWNER' | string
  business_id: number | null
  is_active: boolean
  created_at: string
}

export type LoginResponse = {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export type Analytics = {
  business_id:number; business_slug:string; period_days:number|null; total_events:number; event_counts:Record<string,number>; rating_counts:Record<string,number>;
  landing_page_views:number; rating_selections:number; ai_reviews_generated:number; reviews_selected:number; google_handoffs:number; private_feedback_submitted:number; social_link_clicks:number; google_handoff_rate:number;
}
export type OwnerDashboard = { business_id:number; business_slug:string; business_name:string; category:string|null; logo_url:string|null; analytics:Analytics; complaint_counts:Record<string,number>; recent_complaints:Array<{id:number;rating:number;comments:string;status:string;notification_status:string;created_at:string}>; plan:string; subscription_status:string; unread_notifications:number }
export type OwnerNotification = {id:number;complaint_id:number|null;type:string;status:string;message:string;created_at:string;sent_at:string|null;complaint_status:string|null}
export type OwnerNotificationList = {items:OwnerNotification[];total:number;unread:number}
export type BusinessSettings = {id:number;slug:string;name:string;description:string|null;category:string|null;logo_url:string|null;welcome_message:string|null;brand_primary_color:string;brand_secondary_color:string;prefer_ai_comments:boolean;google_review_pc_url:string;google_review_mob_url:string;nfc_enabled:boolean;qr_enabled:boolean;customer_settings:Record<string,unknown>;updated_at:string}
export type Plan = {code:string;name:string;price_paise:number;monthly_review_limit:number}
export type Subscription = {plan:string;status:string;provider:string;trial_ends_at:string|null;current_period_start:string|null;current_period_end:string|null;cancel_at_period_end:boolean}
export type BillingHistoryItem = {id:number;plan:string;amount_paise:number;currency:string;status:string;provider:string;receipt_reference:string;created_at:string}
export type AdvancedAnalytics = {business_id:number;business_slug:string;period_days:number;total_events:number;event_counts:Record<string,number>;rating_counts:Record<string,number>;positive_reviews:number;negative_reviews:number;positive_ratio:number;negative_ratio:number;complaints:number;google_handoffs:number;google_handoff_rate:number;source_counts:Record<string,number>;ai_usage:number;fallback_usage:number;monthly_trend:Array<{period:string;events:number}>}

export type AdminPlan = { id:number; code:string; name:string; price_paise:number; monthly_review_limit:number; trial_days:number; is_active:boolean; updated_at:string }
export type AdminSubscription = { business_id:number; business_name:string; business_slug:string; owner_email:string|null; plan:string; plan_name:string; status:string; provider:string; trial_ends_at:string|null; current_period_start:string|null; current_period_end:string|null; cancel_at_period_end:boolean; plan_price_paise:number; monthly_review_limit:number }

export type AdminOwnerOption = { id:number; email:string; full_name:string; business_id:number|null; is_active:boolean }
export type AdminSocialLink = { id:number|null; platform:string; url:string; display_order:number; enabled:boolean }
export type AdminBusiness = { id:number; slug:string; name:string; description:string|null; category:string|null; logo_url:string|null; google_review_pc_url:string; google_review_mob_url:string; status:string; prefer_ai_comments:boolean; brand_primary_color:string; brand_secondary_color:string; welcome_message:string|null; nfc_enabled:boolean; qr_enabled:boolean; customer_settings:Record<string,unknown>; owner_id:number|null; owner_email:string|null; owner_name:string|null; plan:string; plan_name:string; subscription_status:string; review_count:number; complaint_count:number; average_rating:number|null; social_links:AdminSocialLink[]; created_at:string; updated_at:string }
