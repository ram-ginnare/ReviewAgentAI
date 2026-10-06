# Phases 13–16 consolidated implementation

Implemented together on the Phase 12 baseline:

- **Phase 13:** authenticated owner dashboard, KPI cards, rating distribution, date ranges, private-feedback inbox, complaint status management, owner isolation, responsive layout.
- **Phase 14:** in-app notification center with unread counts, filtering/status visibility, retry lifecycle from the existing notification service, and optional SMTP email delivery endpoint/configuration.
- **Phase 15:** Starter / Professional / Business plans, 14-day trial, subscription records, checkout/confirmation flow with a safe local MOCK provider, renewal-period metadata, cancellation-at-period-end, payment/receipt history, and monthly AI-review usage enforcement.
- **Phase 16:** business profile, logo/welcome message, brand colors, Google PC/mobile URLs, AI preference, NFC/QR enablement, customer settings JSON, and social-link CRUD.

### Important billing note
The bundled provider is `MOCK` so the project is testable without real payment credentials. Production payment gateway integration should set up and verify Razorpay or Stripe credentials and webhooks before taking real money.

### Database note
The project intentionally uses code-first `create_all()` as established in earlier phases. For a local schema update, recreate the SQLite database and run `python -m backend.app.db.init_db` followed by `python -m backend.app.db.seed`.
