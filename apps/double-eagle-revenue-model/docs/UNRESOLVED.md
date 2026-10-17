# Unresolved dependencies, missing data, and risks

1. **No live CRM/billing** — customers and opportunities are planning illustrations.
2. **No invoice ledger** for refunds, failed payments, overdue AR aging.
3. **LTV / NRR / churn** lack multi-year history → labeled early-stage estimates.
4. **Forecast vs actual** requires a monthly close process (not automated yet).
5. **Assumption edits** are code-based (`src/data/assumptions.ts`), not end-user forms.
6. **Taxes** default to 0 pending jurisdiction setup.
7. **Annual prepay cash vs monthly recognition** needs accountant confirmation.
8. **Voice $/min** is a published-stack planning rate — replace with blended invoice actuals.
9. **Google Sheet** is a snapshot export; the Next.js app is the source of calculation truth unless you later sync both ways.
10. **Risk:** Treating illustrative MRR as real books will overstate readiness for fundraising or debt.
