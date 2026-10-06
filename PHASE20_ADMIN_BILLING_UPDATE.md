# Phase 20 - Admin Subscription Management Update

This update adds ADMIN-only subscription management without changing the existing customer review flow.

## Added
- Admin can view all subscription plans.
- Admin can edit plan name, monthly price, monthly review limit, trial days, and active/inactive state.
- Admin can view each business subscription and owner email.
- Admin can assign Starter / Professional / Business to a business.
- Admin can change subscription status: TRIALING, ACTIVE, PAST_DUE, CANCELLED.
- Admin can update trial end, current billing period dates, and cancel-at-period-end.
- Owner billing plan list now reads the database-managed plan details, so admin changes are reflected.
- ADMIN-only API protection is enforced on every admin billing endpoint.
- Added an Admin Subscription Management page at `/admin/billing`.

## API
- `GET /api/v1/admin/billing/plans`
- `PUT /api/v1/admin/billing/plans/{code}`
- `GET /api/v1/admin/billing/subscriptions`
- `PUT /api/v1/admin/billing/subscriptions/{business_id}`

## Database
A new `subscription_plans` table is created by the existing code-first database initialization. Existing databases can be initialized again safely:

```bash
python -m backend.app.db.init_db
python -m backend.app.db.seed
```

The seed only creates missing default plans and does not overwrite admin-customized plan price/limit/name values.
