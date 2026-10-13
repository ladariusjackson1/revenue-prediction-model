# Assumption registry

All planning inputs live in `src/data/assumptions.ts` and illustrative CRM rows in `src/data/customers.ts`.

## Provenance legend

| Tag | Meaning |
|---|---|
| `actual` | From real invoices/CRM (none yet) |
| `planning_illustration` | Demo rows so dashboards render |
| `assumption` | Editable planning input — verify |

## Cost assumptions to verify against invoices

- Voice all-in $/min (default 0.13)
- Hosting per site
- Phone number
- CRM allocation
- Support hours × rate
- Payment processing rate (2.9%)
- Shared tools & OpEx lines
- Operating cash balance

## Unresolved dependencies / risks

1. No live CRM or billing system connected — metrics use illustrative customers.
2. LTV/NRR/churn lack statistical history — labeled early-stage.
3. Forecast ≠ actual until monthly close process exists.
4. Tax treatment defaulted to 0.
5. Annual billing cash timing (up-front cash vs monthly recognition) needs accounting policy confirmation.
6. Overage billing not yet invoiced automatically — calculated from minutes × rate for contribution view.
