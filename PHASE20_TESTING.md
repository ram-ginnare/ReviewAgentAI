# Phase 20 Testing Steps

## 1. Start from the Phase 20 ZIP
Extract the ZIP and open the project root.

## 2. Reset the local database when upgrading an older local database
Because this project uses code-first `Base.metadata.create_all()` and no Alembic, the safest clean upgrade is:

```bash
python -m backend.app.db.init_db
python -m backend.app.db.seed
```

If your local database contains important data, back it up before recreating it.

## 3. Backend regression tests
From the project root:

```bash
pytest -q
```

Expected result for this package:

```text
69 passed
```

The Phase 20-specific tests are in `backend/tests/test_phase_20_admin_businesses.py`.

## 4. Start backend

```bash
uvicorn backend.app.main:app --reload
```

## 5. Start frontend
In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

## 6. Admin login
Use the seeded demo administrator:

- Email: `admin@reviewagentai.local`
- Password: `Admin@12345`

Open `/account` and click **Open admin dashboard**, or open `/admin` directly.

## 7. Test business dashboard
Verify:
- All seeded businesses appear.
- Name, slug, owner, status, plan, review count, complaint count and rating are shown.
- Search by business name works.
- Search by slug/category works.
- Active and inactive filters work.

## 8. Test business details
Select **Edit** on a business and verify the form loads:
- Name / slug
- Description / category
- Logo URL
- Welcome message
- Google desktop/mobile URLs
- Primary/secondary brand colors
- AI preference
- QR enabled
- NFC enabled
- Customer settings JSON
- Social links JSON
- Owner assignment
- Status

Change several values, save, refresh the page and verify the saved values remain.

## 9. Test adding a business
Click **+ Add business**.
Use a unique slug, for example `test-business-20`, and valid Google URLs. Leave owner unassigned if you do not already have a free business-owner account.

Verify:
- Business is created.
- It appears in the business list.
- Starter/trial subscription is created automatically.
- The new settings are returned in the detail panel.

## 10. Test owner assignment
Create or use an existing BUSINESS_OWNER account from the admin user-management endpoint/page, then assign that owner to the new business.

Verify:
- Owner name/email appears in the business table.
- The owner can access only the business linked to that account.
- An owner already assigned to another business cannot be assigned again.

## 11. Test activation/deactivation
Click **Deactivate** for a business and confirm it becomes `INACTIVE`.
Click **Activate** and confirm it returns to `ACTIVE`.

Also verify the existing public customer business endpoint does not expose an inactive business.

## 12. Test authorization
Log in as the business owner:

- `/admin` must not expose admin business management.
- `GET /api/v1/admin/businesses` must return HTTP 403.
- `GET /api/v1/admin/businesses/owners` must return HTTP 403.
- POST/PUT/PATCH admin business endpoints must also reject the owner with HTTP 403.

Log out and verify `/admin` redirects to login.

## 13. Test audit/security behavior
For admin business create/update/status requests, verify the existing Phase 19 audit logging records the API requests.
Also verify security headers such as `X-Content-Type-Options` and `X-Frame-Options` remain present.

## 14. Regression test existing functionality
As the business owner, verify:
- Owner dashboard still loads.
- Notifications still load.
- Billing still loads.
- Advanced analytics and CSV/XLSX/PDF exports still work.
- Business settings still work.
- Customer review flow still works for an active business.
- QR/NFC/direct access behavior is unchanged.

## 15. Responsive testing
Check the admin dashboard at desktop and mobile widths.
Confirm the business table scrolls horizontally on small screens and the edit form remains usable.

## 16. Frontend dependency/build note
If `npx tsc -b` or `npm run build` reports missing React/Vite/Node type packages before `npm install`, run:

```bash
cd frontend
npm install
npm run build
```

In the development environment used to prepare this ZIP, `node_modules` was not installed, so frontend type-checking could not be completed there. The backend regression suite completed successfully with 69 tests passing.
