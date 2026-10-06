# ReviewAgentAI MVP production checklist

This project is code-complete for the remaining MVP application phases, but deployment itself must be performed in your chosen hosting environment.

## 1. Backend
- Set `APP_ENV=production`.
- Use a persistent production database. SQLite is acceptable only for a small single-instance MVP; use PostgreSQL for multi-instance production.
- Store `GROQ_API_KEY` and `BUSINESS_API_KEY` in the hosting provider's secret manager.
- Set `CORS_ORIGINS` to the exact HTTPS frontend origin(s).
- Run with a production ASGI server, for example `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` behind a reverse proxy.

## 2. Frontend
- Set `VITE_API_BASE_URL` to the HTTPS backend `/api/v1` URL.
- Run `npm ci` and `npm run build`.
- Serve the generated `frontend/dist` directory from a static host/CDN.

## 3. HTTPS and operations
- Put TLS/HTTPS in front of both applications.
- Configure health monitoring against `/api/v1/health`.
- Rotate `BUSINESS_API_KEY` and Groq credentials if exposed.
- Back up the production database and test restoring a backup before launch.
- Keep application logs free of API keys and customer secrets.

## 4. NFC / QR
Create business-specific access links in the form:
`https://<frontend-host>/r/<business-slug>?source=nfc`
or
`https://<frontend-host>/r/<business-slug>?source=qr`

Validate both flows on an actual phone before printing tags/QR codes.

## 5. Smoke test
1. Open a valid QR/NFC link.
2. Confirm landing event and session creation.
3. Submit a 1–3 star rating and private feedback; verify no Google handoff occurs.
4. Submit a 4–5 star rating; generate/select a review.
5. Confirm the review is copied and Google opens only after customer action.
6. Check analytics/dashboard and notification lifecycle.
7. Test expired sessions and invalid/inactive business links.
