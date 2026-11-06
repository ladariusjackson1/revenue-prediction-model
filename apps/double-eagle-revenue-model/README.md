# Double Eagle Financial LLC — Revenue Expansion Model

Next.js dashboard for bookkeeping + AI lead capture economics (Oxford RE / PM / GC).

```bash
npm ci
npm run dev
```

Open http://127.0.0.1:43211

`npm test` checks the finance formulas. `npm run build` is what production runs.

See `docs/DOUBLE_EAGLE_PLAYBOOK.md` for pricing, unit economics, and outbound scripts.

This app lives under `apps/` inside the ML portfolio repo.

## Deploy on Vercel

1. Import the GitHub repository.
2. Set the project **Root Directory** to `apps/double-eagle-revenue-model`. The repo root is the Python portfolio, not this Next.js app.
3. Framework preset: **Next.js**. `vercel.json` sets install to `npm ci` and build to `npm run build`.
4. Do not add environment variables. The model reads `src/data/assumptions.ts` and `src/data/customers.ts`.
5. Deploy with Node.js 20 or newer.

`npm run dev` and `npm start` listen on `127.0.0.1:43211` for local work. Vercel serves `next build` and ignores that host and port.
