# ReviewAgentAI Phase 4 TypeScript Fix

Replace:
`frontend/src/pages/CustomerLandingPage.tsx`

The fix makes `normalizeSource()` explicitly return the API's allowed source union:
`'nfc' | 'qr' | 'direct'`.

After copying the file into your project, run:

```bash
cd frontend
npm install
npm run build
npm test
```

If your existing `node_modules` came from another OS/environment, delete `frontend/node_modules` and run `npm install` first.
