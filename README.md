# reviewagentai

ReviewAgentAI is a review-gating and customer-feedback platform for business-specific NFC/QR entry points.

## Current implementation

- SQLite + SQLAlchemy database foundation
- Business and social-link management
- Review session creation
- 1–5 star rating flow
- 1–3 star private feedback flow
- Groq-powered positive review suggestions with safe fallback text
- Google review selection/handoff
- Social-link click tracking
- Review/customer journey event tracking
- NFC/QR customer access validation and session creation
- Automatic database table creation with `Base.metadata.create_all()`
- **Alembic is not used**

## Customer access flow

A business-specific NFC/QR entry point uses the business slug:

```text
POST /api/v1/access/{business_slug}
```

Request:

```json
{
  "source": "nfc"
}
```

Supported `source` values:

- `nfc`
- `qr`
- `direct`

The endpoint:

1. Validates that the business exists.
2. Validates that the business is active.
3. Creates a new review session.
4. Records a `LANDING_PAGE_VIEW` event in the existing `review_events` table.
5. Stores the access channel and `session_id` in event metadata.
6. Returns the session information required by the customer review flow.

Example:

```text
POST /api/v1/access/reviewagentai
```

```json
{
  "source": "qr"
}
```

The endpoint does **not** submit a Google review automatically. Google review submission remains a manual customer action.

## Run locally

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run tests:

```powershell
pytest -q
```

Run the API:

```powershell
uvicorn backend.app.main:app --reload
```

Default API documentation:

```text
http://127.0.0.1:8000/docs
```

## Demo seed and SQLite reset

The demo seed is idempotent. On application startup it keeps the canonical five demo social links for `reviewagentai` and `abc-restaurant`, repairs their URL/order/enabled values, and removes obsolete or duplicate demo social-link records.

During development, if an older database contains stale test data, stop the API and delete the SQLite database file configured by `DATABASE_URL` (normally `reviewagentai.db`). Restarting the API recreates the tables and seeds clean demo data automatically.

No Alembic migration workflow is required for this development setup.

## AI vs database fallback review comments

Each business has a Boolean database column named `PreferAIComments` (exposed by the API as `prefer_ai_comments`). It controls the positive-review generation strategy:

- `true`: call Groq first. If Groq succeeds, the response has `generation_source: "groq"`.
- `false`: do not call Groq; use the business's database fallback comments and return `generation_source: "fallback"`.
- If `PreferAIComments=true` but Groq fails for any reason (API key, quota, network, model error, invalid response, etc.), the backend automatically uses the database fallback comments and still returns a successful response with `generation_source: "fallback"`.

Fallback comments are stored in the `fallback_review_comments` table. The table supports business-specific comments, 4/5-star variants, display order, and enabled/disabled status. The fallback comments are therefore configurable database data rather than hard-coded response strings.

The positive-review response now includes:

```json
{
  "session_id": "...",
  "business_id": "1",
  "rating": 5,
  "generation_source": "groq",
  "reviews": []
}
```

When AI is unavailable:

```json
{
  "session_id": "...",
  "business_id": "1",
  "rating": 5,
  "generation_source": "fallback",
  "reviews": []
}
```

The fallback templates can contain `{customer_input}`. At runtime that placeholder is replaced with the customer's own comments, without asking AI to generate the fallback text.

### Database reset after this schema change

Because this development project intentionally does not use Alembic, recreate the SQLite database after applying this change:

```powershell
# Stop the API first with CTRL+C
Remove-Item .\reviewagentai.db -ErrorAction SilentlyContinue
uvicorn backend.app.main:app --reload
```

Startup will recreate the `PreferAIComments` column and `fallback_review_comments` table and seed the demo fallback comments.

### Verification

Run:

```powershell
pytest -q
```

Then test:

```text
POST /api/v1/reviews/session
POST /api/v1/reviews/session/{session_id}/rating
POST /api/v1/reviews/session/{session_id}/positive-reviews
```

For `reviewagentai`, `prefer_ai_comments=true`, so a successful Groq request should return `generation_source="groq"`. To test the fallback path, temporarily set the business's `PreferAIComments` value to false or simulate a Groq failure; the frontend must still receive three review comments with `generation_source="fallback"`.


## Google Review PC/Mobile URL Routing

The `businesses` table stores two Google review URLs:

- `google_review_pc_url` — desktop/laptop browser URL.
- `google_review_mob_url` — mobile phone/tablet browser URL.

The Google review selection endpoint detects the request `User-Agent`. Desktop/laptop browsers receive the PC URL. Mobile phones and tablets receive the mobile URL. Unknown or missing User-Agent values default to the mobile URL. The response also includes `google_review_url` as the selected URL and `device_type` as `desktop` or `mobile`.

The seeded `reviewagentai` mobile review URL is `https://g.page/r/CQXyLImX75mfEBM/review`.

## Phase 3.12 Backend Hardening

The backend now includes a small pre-frontend hardening pass:

- Generated positive reviews are linked to their `review_session`, preventing cross-session review selection.
- Google handoff keeps the PC/mobile/tablet URL routing already implemented. Only one generated review can be selected per session.
- Review session statuses are centralized in `backend/app/core/statuses.py`.
- API errors include both the existing `detail` field and a stable `code` field. Validation errors use `VALIDATION_ERROR`.
- Positive-review generation has an in-memory MVP rate limit. Configure `AI_RATE_LIMIT_REQUESTS` and `AI_RATE_LIMIT_WINDOW_SECONDS`.
- Requests receive an `X-Request-ID` and safe request logging records method/path/status/duration without request bodies or secrets.
- CORS credentials are disabled automatically when wildcard origins are configured.
- Database check constraints/indexes protect ratings and speed session review lookups.

### Important after this schema change

Because this project intentionally does not use Alembic, delete `reviewagentai.db` once after installing this version and restart the backend so SQLite is recreated with the new `session_id` column and constraints.

## Phase 4.3-4.13 Customer Frontend

The React frontend now implements the customer-facing review journey through Phase 4.13. It includes the business landing page, NFC/QR/direct entry handling, business branding and social links, 1-5 star rating, positive-review preference checkboxes and optional comment, generated review cards with customer editing/selection, private feedback for 1-3 stars, loading/error/empty/retry/expired states, clipboard fallback, Copy & Open Google, and mobile-first responsive behavior.

Run the frontend from the `frontend` directory:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173/r/reviewagentai` after the FastAPI backend is running on `http://127.0.0.1:8000`.

Frontend validation commands:

```powershell
npm test
npm run build
```

Google review text is never submitted automatically. The selected final text is copied first, then the device-appropriate Google review URL returned by the backend is opened.

## Frontend Design System — Option 1

The customer-facing frontend follows the selected **Modern SaaS / Premium** design direction. Future UI changes should preserve this design system unless explicitly changed by the product owner.

- Mobile-first responsive layout
- Soft gray/white page surfaces
- Deep navy/indigo primary actions
- Blue/purple accent treatments
- Green success, amber warning, and soft red error states
- White cards with 16–20px rounded corners
- Large rounded touch-friendly buttons
- Prominent star rating controls
- Modern sans-serif typography
- Subtle gradients, blur, and shadows
- Accessible keyboard focus states and reduced-motion support
- Business-brand-friendly presentation

The design tokens and reusable classes live primarily in `frontend/src/index.css`, with shared presentation components in `frontend/src/components/`.

## Phase 12 - Authentication

Phase 12 adds the authentication foundation without changing the public customer review flow.

- Roles: `ADMIN` and `BUSINESS_OWNER`
- Secure PBKDF2 password hashing with per-user salts
- Short-lived signed bearer access tokens
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`
- Admin-only `GET /api/v1/auth/users`
- Admin-only `POST /api/v1/auth/users`
- Admin-only `POST /api/v1/auth/users/{user_id}/deactivate`
- Business-owner users are linked to exactly one business in the current MVP model
- Demo authentication users are seeded only when `DEMO_AUTH_SEED=true`

### Local demo credentials

Admin: `admin@reviewagentai.local` / `Admin@12345`
Business owner: `owner@reviewagentai.local` / `Owner@12345`

Change these immediately if this environment is exposed beyond local development. Set a long random `AUTH_SECRET` in any shared or production environment and set `DEMO_AUTH_SEED=false`.

## Phases 13–16
The consolidated owner dashboard, notification center, billing/subscriptions, and business settings/branding are implemented. See `PHASE13_16_IMPLEMENTATION.md`.
