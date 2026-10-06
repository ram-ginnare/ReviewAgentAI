# Complete Testing — Phase 17 & 19

## 1. Fresh database
From the project root:
```bash
python -m backend.app.db.init_db
python -m backend.app.db.seed
```
For a clean local test, delete the existing `reviewagentai.db` first if one exists.

## 2. Backend automated tests
```bash
pytest -q
```
Expected in this package: **66 passed**.

## 3. Start the API
```bash
uvicorn backend.app.main:app --reload
```
Open the API docs at `http://127.0.0.1:8000/docs`.

## 4. Login as owner
Use the existing demo owner account:
- Email: `owner@reviewagentai.local`
- Password: `Owner@12345`

## 5. Phase 17 — Analytics
Open `/owner` and verify:
- Change 7 / 30 / 90 / 365 day range.
- Advanced analytics cards update.
- Positive and negative ratios appear.
- Complaint count appears.
- Google handoff rate appears.
- AI and fallback usage appear.
- QR/NFC/direct source counts are available through the analytics API.

API check:
```text
GET /api/v1/owner/analytics?days=30
```
Must return **200** for the owner.

## 6. Phase 17 — Exports
From the owner dashboard download:
- CSV
- Excel
- PDF

Verify each file opens and contains summary metrics, ratings, sources and trend data.

Direct API checks:
```text
GET /api/v1/owner/analytics/export.csv?days=30
GET /api/v1/owner/analytics/export.xlsx?days=30
GET /api/v1/owner/analytics/export.pdf?days=30
```
All should return **200** with non-empty files when authenticated.

## 7. Authorization test
Without a bearer token, these must return **401**:
```text
GET /api/v1/owner/analytics
GET /api/v1/owner/analytics/export.csv
```
An admin account should not be able to use business-owner-only endpoints; it should receive **403**.

## 8. Phase 19 — Security headers
Open any API response and verify:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` is present
- API responses use `Cache-Control: no-store`

## 9. Phase 19 — Rate limiting
Temporarily set:
```env
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=60
```
Restart the API and send more than 5 requests to the same API path from the same client IP.
The excess request should return **429** and include `Retry-After`.
Restore production values afterward.

## 10. Phase 19 — Audit logs
Make authenticated API calls, then inspect the `audit_logs` table.
Each API request should record:
- user ID when authenticated
- business ID when applicable
- action/method/path
- status code
- request ID
- IP address
- timestamp

The health endpoint is intentionally excluded from audit logging.

## 11. Health / monitoring
```text
GET /api/v1/health
```
Expected:
```json
{"status":"UP","database":"UP"}
```
Stop the database temporarily and verify the health response changes to `DEGRADED` where applicable.

## 12. Regression testing
Run:
```bash
pytest -q
```
Again after all manual tests. Expected: **66 passed**.

## 13. Frontend dependencies
The ZIP intentionally does not include `node_modules`.
Run:
```bash
cd frontend
npm install
npm run build
npm test -- --run
```
If `npm install` fails or times out, retry with a normal network connection. Do not treat missing React/TypeScript modules as application source failures.

## 14. Production checklist
Before public launch:
- Set a long random `AUTH_SECRET`.
- Set `DEMO_AUTH_SEED=false`.
- Set production CORS origins.
- Configure HTTPS/TLS.
- Put the API behind a reverse proxy/WAF.
- Use managed database backups.
- Configure centralized logs and alerts.
- Configure real SMTP if email notifications are required.
- Replace `BILLING_PROVIDER=MOCK` with a verified real payment provider before charging customers.
- Test restore from a real backup.
