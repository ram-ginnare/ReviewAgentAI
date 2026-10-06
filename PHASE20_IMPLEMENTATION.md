# Phase 20 - Admin Business Management

Implemented on top of the Phase 17-19 package.

## Backend
- Admin-only `/api/v1/admin/businesses` dashboard API.
- Search, active/inactive filtering and owner filtering.
- Business owner options for assignment.
- Create business with profile, branding, Google review URLs, AI preference, QR/NFC settings, customer settings and social links.
- Edit all business configuration fields and reassign/unassign an owner.
- Activate/deactivate business.
- Business detail includes subscription/trial state, review count, complaint count and average rating.
- Existing Phase 19 authorization, security headers, rate limiting and audit logging remain active.

## Frontend
- New protected `/admin` dashboard.
- Admin account page links to the admin dashboard.
- Business table with search/filter, owner, plan, usage summary and status.
- Add/edit form for business profile, branding, Google URLs, owner, AI, QR/NFC, customer JSON and social links JSON.
- No customer review-flow behavior was changed.

## Database
No new database tables were required. Phase 20 uses the existing Business, User, SocialLink, Subscription, ReviewEvent, GeneratedPositiveReview and LocalComplaint models.
