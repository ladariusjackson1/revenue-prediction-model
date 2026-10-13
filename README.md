# Contractor AI Agency — Revenue Model

Professional recurring-revenue model for an agency selling **websites + AI voice agents** to contractors (inbound calls, lead capture, appointment booking).

## Run

```bash
npm install
npm run dev
```

Open [http://127.0.0.1:43211](http://127.0.0.1:43211).

```bash
npm test
```

## What’s included

- **Executive dashboard** — MRR, ARR run-rate, gross margin, OpEx, CAC/LTV estimates, churn, NRR, break-even, runway
- **Pricing tiers** — Starter / Growth / Premium with unit economics and target-margin floors
- **Cost to serve** — per-customer contribution (voice, hosting, support, processing)
- **12-month driver-based forecast** — conservative / base / aggressive funnels
- **CRM pipeline stub** — opportunities separate from booked MRR
- **Docs** — `docs/AUDIT_REPORT.md`, `docs/FORMULAS.md`, `docs/ASSUMPTIONS.md`, `docs/SCORES.md`

## Important

Customer rows are **planning illustrations**, not live CRM data. Early-stage metrics are labeled. Edit assumptions in `src/data/assumptions.ts`.

## Google Sheet

See `spreadsheet.json` for the operating workbook URL (created alongside this app). The prior Fortune 500 sheet is an archive only — it is **not** the agency model.
