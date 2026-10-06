# ReviewAgentAI — Simple Project Guide

## 1. What is ReviewAgentAI?

ReviewAgentAI is a customer review and private-feedback system for businesses.

A customer can enter a business page using an NFC tag, QR code, or normal link. The customer gives a 1–5 star rating:

- **1–3 stars:** private feedback is collected.
- **4–5 stars:** the system can suggest positive review text using AI or safe database fallback text.
- The customer chooses the final text and then copies it before opening Google. The application does not automatically submit a Google review.

The system also has separate workspaces for **Business Owners** and **Administrators**.

---

## 2. Main parts of the application

### Backend

- Python + FastAPI
- SQLAlchemy
- SQLite for the current development setup
- Authentication and role-based access
- Review, feedback, analytics, notification and billing APIs

### Frontend

- React + Vite
- Customer review pages
- Business Owner dashboard
- Admin dashboard
- Billing and settings pages
- Responsive UI for desktop and mobile

### Database

The project currently uses code-first table creation with `Base.metadata.create_all()`.

**Alembic is not used.**

---

# 3. How to run the project

## Backend

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
uvicorn backend.app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Customer example:

```text
http://localhost:5173/r/reviewagentai
```

NFC example:

```text
http://localhost:5173/r/reviewagentai?source=nfc
```

QR example:

```text
http://localhost:5173/r/reviewagentai?source=qr
```

---

# 4. Demo accounts

These accounts are for local development only.

### Admin

```text
Email: admin@reviewagentai.local
Password: Admin@12345
```

### Business Owner

```text
Email: owner@reviewagentai.local
Password: Owner@12345
```

If the application is shared or deployed publicly:

- Change the demo passwords.
- Use a long random `AUTH_SECRET`.
- Set `DEMO_AUTH_SEED=false`.

---

# 5. Customer review flow

The customer access API is:

```text
POST /api/v1/access/{business_slug}
```

The supported sources are:

- `nfc`
- `qr`
- `direct`

The system checks that the business exists and is active, creates a review session, records the landing-page event, and returns the session information needed by the frontend.

The customer then:

1. Opens the business page.
2. Selects 1–5 stars.
3. Sees the matching mood face below the stars.
4. For 1–3 stars, enters private feedback.
5. For 4–5 stars, receives positive review suggestions.
6. Selects/edits the review text.
7. Copies the final text.
8. Opens the correct Google review page after the customer's action.

Google review submission is **never automatic**.

---

# 6. AI review generation and fallback

Each business has a `prefer_ai_comments` setting.

### When it is enabled

The system tries Groq first.

If Groq works:

```text
generation_source = groq
```

If Groq fails because of an API key, quota, network problem, model problem, or another error, the system automatically uses database fallback comments:

```text
generation_source = fallback
```

### When AI is disabled

The system directly uses the database fallback comments.

Fallback comments are stored in the `fallback_review_comments` table and can be business-specific, rating-specific, ordered, and enabled/disabled.

Fallback text can contain `{customer_input}`. The customer's own comment is inserted into that placeholder without sending the fallback request to AI.

---

# 7. Google review URL handling

Each business can have two Google URLs:

- Desktop/laptop URL
- Mobile/tablet URL

The backend checks the browser User-Agent and chooses the appropriate URL.

Unknown or missing User-Agent values use the mobile URL.

The response also provides:

- `google_review_url`
- `device_type`

---

# 8. Authentication and users — Phase 12

The application has two main roles:

- **ADMIN**
- **BUSINESS_OWNER**

Authentication uses secure password hashing and signed access tokens.

Main authentication APIs include:

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/change-password
```

Admin-only user APIs include:

```text
GET  /api/v1/auth/users
POST /api/v1/auth/users
POST /api/v1/auth/users/{user_id}/deactivate
```

Business owners are linked to a business in the current MVP model.

The public customer review flow remains separate from authenticated owner/admin access.

---

# 9. Business Owner workspace — Phases 13–16

Business owners have an authenticated workspace.

## Dashboard

Owners can see:

- Review totals
- Rating information
- Rating distribution
- Date ranges such as 7, 30, 90 and 365 days
- Positive review information
- Private feedback
- Complaint status
- Review/feedback filtering

## Notifications

The notification system includes:

- In-app notifications
- Unread counts
- Read/unread status
- Complaint notification details
- Filtering
- Notification status lifecycle
- Retry/error visibility
- Optional SMTP email delivery

## Billing

The original billing system supports:

- Starter
- Professional
- Business
- 14-day trial
- Subscription records
- Payment history
- Renewal-period information
- Cancellation-at-period-end
- Usage limits
- Receipt/payment references

The development payment provider is `MOCK`, so real payment credentials are not required for local testing.

Before charging real customers, configure and verify Razorpay or Stripe, including webhooks.

## Business settings

Owners can manage:

- Business profile
- Logo
- Welcome message
- Brand colors
- Google review URLs
- AI preference
- NFC enabled/disabled
- QR enabled/disabled
- Customer settings
- Social links

---

# 10. Advanced analytics — Phase 17

The owner dashboard includes advanced analytics for:

- Positive/negative review ratio
- Rating trends
- Complaint trends
- Google handoff rate
- AI vs fallback usage
- NFC vs QR vs direct access
- Monthly trends
- Date-based analysis

Owners can export analytics as:

- CSV
- Excel
- PDF

Main analytics API:

```text
GET /api/v1/owner/analytics?days=30
```

Exports:

```text
GET /api/v1/owner/analytics/export.csv?days=30
GET /api/v1/owner/analytics/export.xlsx?days=30
GET /api/v1/owner/analytics/export.pdf?days=30
```

These endpoints require owner authentication.

---

# 11. Security and production hardening — Phase 19

The application includes:

- API audit logs
- Request ID tracking
- Configurable API rate limiting
- Security response headers
- `Cache-Control: no-store` for API responses
- Database indexes for common analytics queries
- Health monitoring endpoint
- Production configuration controls

Important configuration values include:

```text
RATE_LIMIT_REQUESTS
RATE_LIMIT_WINDOW_SECONDS
AUDIT_LOG_ENABLED
```

The health endpoint is:

```text
GET /api/v1/health
```

A healthy response is normally:

```json
{"status":"UP","database":"UP"}
```

Phase 19 is application-level security hardening. For production, it should still be combined with a reverse proxy/WAF, HTTPS, centralized logs, backups, monitoring, secret management and a real payment provider.

---

# 12. Admin workspace — Phase 20

The Admin workspace is separate from the Business Owner workspace.

Open:

```text
http://localhost:5173/admin
```

Admin can manage businesses and subscriptions.

## Business management

Admin can:

- View all businesses
- Search businesses
- Filter businesses by status
- See business owner
- See subscription plan
- See review count
- See complaint count
- See rating
- Open business details
- Add a business
- Edit a business
- Activate a business
- Deactivate a business
- Assign or change a business owner
- Update business profile details
- Update branding
- Update Google review URLs
- Update social links
- Enable/disable NFC
- Enable/disable QR
- Update customer settings
- Update AI preference

Admin business APIs include:

```text
GET    /api/v1/admin/businesses
GET    /api/v1/admin/businesses/{id}
POST   /api/v1/admin/businesses
PUT    /api/v1/admin/businesses/{id}
PATCH  /api/v1/admin/businesses/{id}/status
```

Only an ADMIN can use these endpoints.

A Business Owner attempting to use them should receive HTTP 403.

---

# 13. Admin subscription management — Phase 20 update

Admin can also control subscription plan details.

Admin can:

- View all plans
- Change plan name
- Change monthly price
- Change monthly review limit
- Change trial days
- Activate/deactivate a plan
- View each business subscription
- Change a business between Starter, Professional and Business
- Change subscription status
- Update trial end date
- Update billing-period dates
- Enable/disable cancel-at-period-end

Subscription statuses include:

- `TRIALING`
- `ACTIVE`
- `PAST_DUE`
- `CANCELLED`

Admin subscription APIs:

```text
GET /api/v1/admin/billing/plans
PUT /api/v1/admin/billing/plans/{code}
GET /api/v1/admin/billing/subscriptions
PUT /api/v1/admin/billing/subscriptions/{business_id}
```

Only ADMIN users can use these endpoints.

When an admin changes plan details, the Business Owner's available billing information uses the database-managed values.

An inactive plan cannot be assigned to a business.

A plan that is currently being used by an active/trialing/past-due subscription cannot simply be deactivated.

The database has a `subscription_plans` table. Run database initialization and seeding when required:

```powershell
python -m backend.app.db.init_db
python -m backend.app.db.seed
```

The seed creates missing default plans without overwriting admin-customized plan values.

---

# 14. Important API security rules

### Public customer APIs

Customer review and business access APIs remain public where required by the customer journey.

### Business Owner APIs

Owner dashboard, analytics, billing and owner settings require Business Owner authentication.

### Admin APIs

Admin business and admin billing APIs require the ADMIN role.

A normal Business Owner must not be able to access another business's admin controls.

---

# 15. Database reset and schema changes

This project intentionally does not use Alembic.

For a clean local development database:

1. Stop the backend with `CTRL+C`.
2. Delete the SQLite database if necessary.
3. Restart the application or run database initialization.

PowerShell example:

```powershell
Remove-Item .\reviewagentai.db -ErrorAction SilentlyContinue
python -m backend.app.db.init_db
python -m backend.app.db.seed
```

The development seed is designed to be repeatable.

If old test data is causing a problem during development, resetting the local SQLite database is the simplest solution.

---

# 16. Testing

## Backend automated tests

Run:

```powershell
pytest -q
```

The latest Phase 20 test package has **73 backend tests**.

Run the command again after changes to confirm that all tests still pass.

### What the tests cover

- Authentication
- Customer review flow
- Business access
- Owner dashboard
- Notifications
- Billing
- Business settings
- Analytics
- Security hardening
- Admin business management
- Admin subscription management
- Authorization rules

## Frontend tests

From `frontend`:

```powershell
npm install
npm test
npm run build
```

If `node_modules` came from another operating system, delete it and reinstall:

```powershell
Remove-Item -Recurse -Force node_modules
npm install
```

The ZIP does not include `node_modules`.

---

# 17. Useful manual tests

## Admin

1. Login as Admin.
2. Open `/admin`.
3. Confirm businesses are displayed.
4. Search for a business.
5. Edit a business.
6. Change its status.
7. Add a new business.
8. Open Admin Subscription & Billing.
9. Change a plan's price or review limit.
10. Change a business subscription.
11. Refresh the page and confirm the values remain.

## Business Owner

1. Login as Business Owner.
2. Open `/owner`.
3. Check dashboard statistics.
4. Open analytics.
5. Test CSV, Excel and PDF exports.
6. Check private feedback.
7. Check notifications.
8. Check billing.
9. Check business settings.

## Customer

1. Open a QR/NFC/direct customer URL.
2. Test 1–3 stars and private feedback.
3. Test 4–5 stars and positive review suggestions.
4. Select/edit the final review.
5. Copy the review.
6. Confirm Google opens only after customer action.

---

# 18. Phase 19 security checks

Check that API responses include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy
Cache-Control: no-store
```

For rate-limit testing, temporarily use:

```env
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=60
```

Send more than five requests to the same API path from the same client. The excess request should return HTTP 429 and include `Retry-After`.

Restore the normal production values afterward.

Audit logs should contain useful request information such as:

- User ID when authenticated
- Business ID when applicable
- HTTP method/path
- Status code
- Request ID
- IP address
- Timestamp

Health checks are intentionally excluded from normal audit logging.

---

# 19. Production checklist

Before public launch:

- Set `APP_ENV=production`.
- Use a persistent production database. PostgreSQL is recommended for multi-instance production.
- Set a long random `AUTH_SECRET`.
- Set `DEMO_AUTH_SEED=false`.
- Configure the real `GROQ_API_KEY` securely if AI is used.
- Configure production CORS origins.
- Use HTTPS/TLS.
- Put the API behind a reverse proxy/WAF.
- Use centralized logs and monitoring.
- Configure alerts.
- Use managed database backups.
- Test restoring a backup.
- Configure real SMTP if email notifications are required.
- Replace `BILLING_PROVIDER=MOCK` with a verified real payment provider before charging customers.
- Keep API keys, passwords and customer secrets out of logs.
- Test NFC and QR links on a real phone before printing them.

---

# 20. NFC and QR links

Business-specific links use the business slug.

Example NFC:

```text
https://<frontend-host>/r/<business-slug>?source=nfc
```

Example QR:

```text
https://<frontend-host>/r/<business-slug>?source=qr
```

Test both links on an actual phone before using them in production.

---

# 21. UI notes

The customer UI includes:

- 1–5 star rating
- Mood faces directly below the stars:
  - 1 star: 😞
  - 2 stars: 😕
  - 3 stars: 😐
  - 4 stars: 🙂
  - 5 stars: 🤩
- Primary `Start a new review` button
- Responsive customer layout
- Business branding and social links
- Accessible focus states
- Mobile-friendly controls

The Admin and Business Owner workspaces use a separate authenticated dashboard style.

Future UI changes should not remove existing customer functionality unless explicitly requested.

---

# 22. Troubleshooting

## Uvicorn shows `KeyboardInterrupt` / `CancelledError`

If you see messages such as:

```text
KeyboardInterrupt
asyncio.exceptions.CancelledError
Stopping reloader process
```

after pressing `CTRL+C`, this normally means the server was stopped manually. It is not an application error.

Start it again:

```powershell
uvicorn backend.app.main:app --reload
```

## API returns 404

Check:

1. Backend is running.
2. The URL is correct.
3. The correct frontend/backend version is installed.
4. Open `/docs` and confirm the endpoint exists.

## Frontend looks unstyled

Try:

```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

Then hard-refresh the browser with `CTRL+F5`.

## Duplicate test business/slug

If an old local test record remains, reset the SQLite database or remove the test record and run:

```powershell
pytest -q
```

The Phase 20 tests are designed to clean up their own test business/owner data so the suite can be run repeatedly.

## Database looks old after a code update

Because there is no Alembic migration system, initialize the database again or perform a clean local database reset.

---

# 23. Main development rule

When adding a new phase:

1. Keep the existing customer review flow working.
2. Keep Admin and Business Owner permissions separate.
3. Protect new authenticated APIs with the correct role.
4. Add automated tests.
5. Test the frontend after installing dependencies.
6. Update this single guide instead of creating another separate Markdown file.

---

# 24. Quick command reference

### Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Test backend

```powershell
pytest -q
```

### Start backend

```powershell
uvicorn backend.app.main:app --reload
```

### Initialize database

```powershell
python -m backend.app.db.init_db
python -m backend.app.db.seed
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Frontend build

```powershell
npm run build
```

### API docs

```text
http://127.0.0.1:8000/docs
```

### Customer page

```text
http://localhost:5173/r/reviewagentai
```

### Business Owner workspace

```text
http://localhost:5173/owner
```

### Admin workspace

```text
http://localhost:5173/admin
```

### Admin billing

```text
http://localhost:5173/admin/billing
```

---

## Final note

This file is now the single simple documentation file for ReviewAgentAI. Keep technical source code comments where they are useful, but add future project-level instructions and phase notes here instead of creating many separate `.md` files.
