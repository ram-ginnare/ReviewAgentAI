# Phase 20 Admin Subscription Management - Testing

## 1. Initialize database
```bash
python -m backend.app.db.init_db
python -m backend.app.db.seed
```

## 2. Run automated tests
```bash
pytest -q
```
Expected in this build: **70 passed**.

## 3. Start backend
```bash
uvicorn backend.app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

## 4. Test Admin UI
1. Start the frontend with `npm install` then `npm run dev`.
2. Login using:
   - Email: `admin@reviewagentai.local`
   - Password: `Admin@12345`
3. Open `/admin/billing`.
4. Under **Plan details**, change Starter price, monthly review limit, or trial days and click Save.
5. Confirm the saved values remain after refreshing the page.
6. Under **Business subscriptions**, change a business plan and status and click Update.
7. Confirm the updated subscription is shown after refresh.

## 5. Test owner visibility
1. Login as `owner@reviewagentai.local` / `Owner@12345`.
2. Open the existing billing/subscription area.
3. Confirm admin-edited plan price and review limit are reflected in the available plans.

## 6. Security tests
- A BUSINESS_OWNER calling `/api/v1/admin/billing/plans` must receive HTTP 403.
- A BUSINESS_OWNER calling `/api/v1/admin/billing/subscriptions` must receive HTTP 403.
- Unauthenticated requests to admin billing endpoints must receive HTTP 401.

## 7. Important behavior
- Deactivating a plan that is currently assigned to an active/trialing/past-due subscription is rejected.
- Admin cannot assign an inactive plan to a business.
- Billing usage limits use the database-managed monthly review limit.
