# Phase 1 Audit Report — Revenue Model

**Business context:** AI automation agency selling websites + AI voice agents to contractors (inbound call answering, lead capture, appointment booking).

**Audited artifacts:** Next.js app (`src/`), Google Sheet `Top 500 Companies Revenue Model` (`1y1etk77QLopdToYomWSkjGGYxyCjy9WyvJtb26_r3NM`), `README.md`, `spreadsheet.json`.

**Audit date:** 2026-10-13

---

## Executive finding

The existing “revenue model” is a **Fortune 500 market research workbook**, not a business revenue model for this agency. It cannot produce MRR, CAC, churn, unit economics, or forecasts for contractor customers. Severity: **Critical**.

---

## Prioritized issues

| ID | Severity | Issue | Why it matters | Business impact | Proposed fix |
|---|---|---|---|---|---|
| A1 | Critical | Wrong domain: F500 company revenues instead of agency SaaS/retainer economics | Decisions based on Walmart/Amazon data cannot price voice agents or websites | Zero decision utility for pricing, hiring, or cash planning | Replace with agency revenue architecture (streams, customers, costs, forecast) |
| A2 | Critical | No MRR/ARR definitions or calculations | Recurring business cannot be managed without normalized recurring revenue | Blind to runway and growth | Implement MRR (active recurring contracts) and ARR = MRR × 12 as run-rate |
| A3 | Critical | No separation of setup vs recurring vs usage revenue | One-time fees inflate “recurring” if mixed | Overstated retention and LTV | Explicit revenue stream types; never include setup in MRR |
| A4 | Critical | No cost-to-serve (voice mins, telephony, hosting, labor) | Pricing without delivery cost destroys margin | Unprofitable tiers possible | Per-tier and per-customer contribution model with editable unit costs |
| A5 | Critical | No CRM / pipeline / activation / churn events | Cannot reconcile active customers or NRR | Duplicate counting and fake growth | Customer + opportunity schema with activation/cancellation rules |
| A6 | High | “Scenarios” tab uses arbitrary portfolio growth % | Not tied to leads, close rates, or churn | Misleading fundraising/planning | Driver-based 12-month cohort forecast (base/conserv/aggress) |
| A7 | High | No pricing tiers or package economics | Cannot standardize offers for contractors | Inconsistent deals, margin leakage | Starter / Growth / Premium with cost, margin, overage triggers |
| A8 | High | No CAC, LTV, payback, NRR, break-even, runway | Missing operator KPIs | Cannot judge sales efficiency | Documented formulas + dashboard with early-stage labels |
| A9 | High | Dashboard charts are market concentration, not financial health | Wrong visualizations for operators | Wasted attention | Executive financial dashboard |
| A10 | Medium | F500 dataset quality issues (sub-threshold companies in lower ranks) | Even as market data, unreliable | N/A for agency ops | Retire F500 sheet from primary path; keep link only as archive |
| A11 | Medium | No tests for financial formulas | Silent calculation bugs | Bad decisions | Vitest suite for MRR, churn, NRR, LTV, forecast |
| A12 | Medium | No assumption registry (taxes, payment timing, recognition) | Ambiguous cash vs revenue | Accounting confusion | Document contracted / invoiced / collected / recognized |
| A13 | Low | No date filters or forecast-vs-actual | Hard to manage month-to-month | Slow ops | Period selector + actual vs plan when data exists |

---

## What does not exist (gaps)

- Customer records, invoices, payments, refunds, failed payments
- Lead → opportunity → won pipeline
- Expense ledger (tools, ads, labor)
- Usage metering (voice minutes)
- Real historical retention (LTV/NRR must be labeled **early-stage estimates**)

---

## Original model score (out of 10)

| Dimension | Score | Evidence |
|---|---|---|
| Financial accuracy | 1/10 | No agency P&L metrics; F500 totals only |
| Usability for this business | 1/10 | UI answers “who is biggest in America?”, not “can I afford ads?” |
| Completeness | 2/10 | Nice charts/table, zero SaaS/agency constructs |
| Scalability | 2/10 | Static JSON dump; not configurable for customers/costs |
| **Overall** | **1.5/10** | Wrong product for the stated business |

---

## Implementation decision

Proceed to rebuild in place on the existing Next.js app and create a new Google Sheet for the agency model. No irreversible deletion of the F500 sheet (it remains as an archive link). No external financial commitments.
