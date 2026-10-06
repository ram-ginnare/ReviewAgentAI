# Phase 12 — Authentication & User Management

Implemented on top of the latest ReviewAgentAI customer-flow code. Customer review routes remain public and unchanged.

## Included
- ADMIN and BUSINESS_OWNER roles
- User/business ownership relationship
- PBKDF2-HMAC-SHA256 password hashing with random salts
- 8-hour signed bearer access tokens
- Login/current-user/change-password APIs
- Admin-only user list/create/deactivate APIs
- Protected `/account` frontend route and login page
- Demo users for local development only
- `AUTH_SECRET` and `DEMO_AUTH_SEED` configuration
- Phase 12 tests
- Phases 13–19 added to `Phases.txt`

## Demo credentials (local only)
- Admin: admin@reviewagentai.local / Admin@12345
- Business owner: owner@reviewagentai.local / Owner@12345

For production/shared environments, set a long random AUTH_SECRET and `DEMO_AUTH_SEED=false`.

## Validation
- Backend: 56 tests passed
- Frontend TypeScript: passed
- Frontend build/test could not be executed in the packaging environment because the supplied environment was missing Rollup's Linux optional native dependency. Run `npm install` locally before `npm run build`.
