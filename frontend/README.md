# reviewagentai frontend

Phase 4.2 implements the customer landing page and connects it to the existing FastAPI backend.

## Run

From this folder:

```powershell
npm install
npm run dev
```

The Vite app runs at `http://localhost:5173`.

## API configuration

Copy `.env.example` to `.env` if you need to change the backend URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Customer URL

Open:

```text
http://localhost:5173/r/reviewagentai
```

Optional NFC/QR source examples:

```text
http://localhost:5173/r/reviewagentai?source=nfc
http://localhost:5173/r/reviewagentai?source=qr
```

The page creates a customer access session through `POST /api/v1/access/{slug}` and loads the full business profile through `GET /api/v1/businesses/{slug}`.

## Phase 4.2 scope

Included:

- Business name
- Logo or initials fallback
- Category
- Description
- Customer feedback CTA
- Social links
- Social click tracking
- Loading state
- Error state with retry
- Responsive mobile/desktop layout

The actual star-rating experience is intentionally left for Phase 4.3.
