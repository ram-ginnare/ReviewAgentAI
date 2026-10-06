# ReviewAgentAI — Phase 17 & 19

Implemented on top of the Phase 13–16 package.

## Phase 17
- Advanced owner analytics endpoint with positive/negative ratios, complaint counts, Google handoff rate, AI/fallback usage, QR/NFC/direct source counts and monthly trend.
- Owner dashboard now shows advanced metrics and authenticated CSV, Excel and PDF download buttons.
- Excel uses `openpyxl`; PDF uses `reportlab`.

## Phase 19
- Audit log table for API activity with request ID, user/business, path, status and IP.
- Global sliding-window API rate limiting (configurable).
- Security response headers and API `no-store` cache policy.
- Added composite analytics index for common business/event/date queries.
- Health endpoint remains available for monitoring.
- Production configuration controls: `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`, `AUDIT_LOG_ENABLED`.

## Production note
This is application-level hardening, not a replacement for an external WAF/reverse proxy, centralized logs, managed database backups, TLS termination, monitoring/alerting, secret management and a real payment provider.
