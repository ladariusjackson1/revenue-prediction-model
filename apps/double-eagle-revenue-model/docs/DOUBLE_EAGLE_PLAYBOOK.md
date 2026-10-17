# Double Eagle Financial LLC — Revenue Expansion Playbook

**Founder:** Ladarius Shuntez Jackson  
**Market:** Oxford, MS and surrounding (real estate agents, property managers, general contractors)  
**Core assets:** QuickBooks ProAdvisor · Python/automation · AI workflow integration  
**Operating model:** Next.js dashboard at http://127.0.0.1:43211 · assumptions in `src/data/assumptions.ts`

---

## 1. Scratchpad — Revenue stream audit and unit economics

### Baseline bookkeeping (what you sell today)

| Stream | Type | Planning price | In MRR? | Notes |
|---|---|---|---|---|
| Monthly QBO bookkeeping + reconciliations | Recurring | $350/mo (Foundation) | Yes | Core cash engine |
| Velocity Suite retainer | Recurring | $550/mo | Yes | Adds Q4 velocity / CFO-lite |
| Catch-up / clean-up | One-time | $75–$125/hr (typ. $760 for ~8 hrs) | **No** | Quote after diagnostic |
| Onboarding / chart-of-accounts setup | One-time | $750–$1,250 | **No** | Tier setup fee |

**Weakness of bookkeeping-only:** labor-bound, hard to scale past founder hours, low perceived urgency until tax season, weak differentiation vs other ProAdvisors.

### High-margin tech stack (what you add)

| SKU | Setup (cash) | MRR | Direct delivery cost (planning) | Gross margin on MRR |
|---|---|---|---|---|
| AI Lead Capture — Standard | $499 | $99 | ~$25–$40/mo (CRM alloc + LLM/SMS + 0.5 support hr) | ~60–75% |
| AI Lead Capture — Pro (PMs) | $999 | $149 | ~$35–$55/mo | ~63–77% |
| Bundled in Enterprise Alpha | $999 | part of $699 | voice/chat blend + support | See dashboard |

**Why this stacks:** setup fees fund acquisition and onboarding labor; MRR compounds; AI delivery is mostly productized (scripts + CRM workflows), not custom bookkeeping hours.

### Unit economics targets (planning)

- Target gross margin on delivery: **70%+**
- CAC payback on blended deal: **under 2 months** when setup fee is collected up front
- AI add-on alone: setup usually covers onboarding labor; MRR is mostly contribution
- Never put clean-up or setup into MRR

### Cash vs recognition (operator rules)

1. Collect setup before build week when possible (or 50% deposit).
2. Activate recurring on the 1st billing cycle after go-live.
3. Pipeline MRR is not booked MRR until status = active.

---

## 2. Grand Slam Offer — tiered packaging

### Tier 1 — The Foundation ($750 setup + $350/mo)

**For:** Solo agents, small GCs who need clean books.  
**Includes:**
- QuickBooks Online setup or takeover
- Monthly categorization and bank/credit reconciliations
- Monthly P&L + balance sheet PDF
- Email support (48-hour SLA)

**Does not include:** AI bots, CRM automation, quarterly strategy.  
**Upsell path:** Clean-up if behind → Velocity at tax season → AI Capture when they complain about missed leads.

### Tier 2 — The Velocity Suite ($1,250 setup + $550/mo)

**For:** Growing agents/teams and PMs who need tax-ready speed.  
**Includes everything in Foundation, plus:**
- Q4 Financial Velocity Package (tax-ready close checklist, year-end cleanup sprint)
- Cash and job/property P&L dashboards (monthly)
- Quarterly 45-minute CFO-lite review
- Priority support

**Optional stack:** AI Lead Capture Standard — **+$499 setup + $99/mo**

### Tier 3 — The Enterprise Alpha ($999 setup + $699/mo)

**For:** Property managers and multi-agent teams who lose revenue to missed calls/leads.  
**Includes:**
- Full financial package (Velocity-level books)
- 24/7 AI Lead Capture and Qualifier (web/SMS; voice-capable where configured)
- Appointment booking + CRM workflow integration
- Missed-call text-back
- Monthly optimization of bot scripts from real transcripts
- 150 included AI conversation minutes; overage $0.35/min

**Value architecture (Hormozi-style):**  
Dream outcome: never lose another after-hours lead + books always tax-ready.  
Perceived value anchors: one saved rental/deal often exceeds annual Alpha fee.  
Risk reversal: 30-day bot performance guarantee (if not booking qualified appointments from inbound volume, pause AI MRR or rework flows at no setup charge).  
Urgency: Oxford seasonal leasing / spring GC bid season — install before peak.

### A la carte AI (if they already have a bookkeeper)

| Package | Setup | MRR |
|---|---|---|
| Standard (agents / GCs) | $499 | $99 |
| Pro (property managers) | $999 | $149 |

Sell a la carte, then pull books onto Foundation/Velocity within 60 days.

---

## 3. Offer math examples (do not treat as books)

**Example A — Velocity + Standard AI**  
Setup cash: 1,250 + 499 = **$1,749**  
MRR: 550 + 99 = **$649**  
Year-1 cash if retained 12 months: 1,749 + 649×12 = **$9,537** (before costs)

**Example B — Enterprise Alpha alone**  
Setup: **$999** · MRR: **$699** · Year-1 cash if retained: 999 + 699×12 = **$9,387**

**Example C — Foundation only**  
Setup: **$750** · MRR: **$350** · Year-1 cash: 750 + 350×12 = **$4,950**

Dashboard computes live contribution and scenario forecasts from these prices.

---

## 4. 14-day client acquisition engine (Oxford)

### Ideal customer profile (ICP)

1. Real estate agents with active buyer/seller lead flow and messy or no QBO  
2. Property managers with after-hours maintenance/leasing inquiries  
3. GCs bidding jobs who lose calls during the day  

### Channel mix (weekly)

| Channel | Cadence | Offer |
|---|---|---|
| Warm network (Ole Miss, Chamber, referrals) | 10 personal asks/week | Velocity or Alpha intro |
| LinkedIn outbound | 25 connection notes + 15 DMs/week | AI Lead Capture hook |
| Cold email | 40/week to agents/PMs/GCs | Problem-led (missed leads / tax scramble) |
| SMS (compliant lists only) | 20/week | Short booking link |
| Local FB groups / GBP posts | 3/week | Case-style value |

### KPI targets (base scenario drivers)

- 45 leads/month → ~30% to appointment → 75% show → 35% close ≈ **~3.5 new logos/month**
- Close cycle: **14 days or less** from first touch to paid setup
- Expansion: attach AI to 40%+ of Foundation/Velocity within 90 days

### 14-day close calendar

| Day | Action |
|---|---|
| 0 | First touch (script below) + calendar link |
| 1 | Soft bump if no reply |
| 2–3 | Discovery call (20 min): books pain + lead leakage |
| 3 | Same-day proposal PDF + Stripe invoice for setup |
| 4–5 | Follow-up: ROI one-pager (missed leads math) |
| 7 | Breakup email / SMS |
| 8–10 | Live mini-demo of bot on their sample FAQ |
| 11–13 | Close for setup deposit; schedule build week |
| 14 | Go-live checklist; first MRR billed next cycle |

---

## 5. Scripts — cold outreach and upsells

### 5.1 Cold email — real estate agent (AI + books)

**Subject:** Missed leads after 6pm in Oxford?

Hey {{FirstName}},

Quick question — when a buyer inquiry hits your site or Facebook after hours, who answers it?

I run **Double Eagle Financial** here in Oxford. Besides keeping agents’ QuickBooks clean, we install a **24/7 AI lead qualifier** that texts back, asks the 4 buyer questions you care about, and books the appointment on your calendar.

Most agents start with either:
- Books only: $350/mo  
- Books + AI: typically $499–$999 setup + $99–$149/mo for the bot stack  

If you want, I can show you a 12-minute demo on a fake lead this week.

Calendar: {{CalendlyLink}}  
— Ladarius Jackson | Double Eagle Financial LLC | QuickBooks ProAdvisor

### 5.2 Cold email — property manager

**Subject:** After-hours maintenance texts without hiring a night desk

{{FirstName}} — property managers in Lafayette County tell me the same thing: leasing and maintenance messages pile up overnight, and Monday is chaos.

We set up an AI intake that:
1) Triages maintenance vs leasing  
2) Captures unit + urgency  
3) Pushes into your CRM / email  
4) Books showings when it’s a lead  

**Pro package:** $999 setup + $149/mo.  
We also run your books in QBO if you want one vendor for money + ops.

Open to a 15-min walkthrough Thu or Fri?

### 5.3 Cold SMS (opt-in / compliant use only)

{{FirstName}} — Ladarius with Double Eagle Financial in Oxford. We help agents/PMs stop losing after-hours leads with a simple AI text-back + keep QBO clean. Worth a 12-min demo? Reply YES and I’ll send times.

### 5.4 LinkedIn connection note

Oxford / RE ops question: are after-hours leads going to voicemail or getting an instant text-back? I build that + QBO for local agents/PMs. Open to a short demo?

### 5.5 Discovery call framework (20 minutes)

1. **Books:** Who does books now? How many months behind? Tax stress 1–10?  
2. **Leads:** Where do leads come from? What happens after 6pm / weekends?  
3. **Cost of inaction:** “If you miss 2 qualified leads a month at even $2k gross commission each, that’s $4k — our AI stack is a fraction of that.”  
4. **Demo:** Live script on their FAQ.  
5. **Close:** Recommend tier. Collect setup same day.

### 5.6 Upsell — existing bookkeeping client → AI

**Subject:** Add 24/7 lead capture to your Double Eagle stack

{{FirstName}} — your books are current. Next unlock: stop leaking after-hours inquiries.

Because you’re already a client, I can add **AI Lead Capture Standard** for **$499 setup + $99/mo** (Pro for PMs: $999 + $149).

I’ll reuse your brand voice and push appointments to the calendar you already use.  
Reply **DEMO** and I’ll schedule a 10-minute screen share.

### 5.7 In-call close (Enterprise Alpha)

“Here’s the offer: we keep your financials tax-ready every month, and we install the AI lead system so nights and weekends still convert.  
Setup is $999. Monthly is $699 — that replaces juggling a bookkeeper plus a marketing gadget.  
If the bot isn’t creating qualified appointments from real inbound volume in 30 days, we pause the AI portion of the retainer and rebuild the flows at no extra setup.  
I can send the invoice now and start build on Monday — sound fair?”

### 5.8 Breakup message (Day 7)

{{FirstName}} — I’ll close your file Friday so I’m not cluttering your inbox. If catching missed leads or getting QBO tax-ready still matters this quarter, grab a slot here: {{CalendlyLink}}. Either way, appreciate your time. — Ladarius

---

## 6. Delivery checklist (so margins stay real)

**Books (Foundation / Velocity)**
- [ ] QBO access + bank feeds  
- [ ] Chart of accounts for RE/PM/GC  
- [ ] Monthly close checklist by day 10  
- [ ] Clean-up scoped in writing before work starts  

**AI Lead Capture**
- [ ] Script approved by client (qualifying questions)  
- [ ] Calendar + CRM/webhook connected  
- [ ] Missed-call text-back tested  
- [ ] Weekly transcript review first 30 days  
- [ ] Minute usage logged for overage  

---

## 7. Execution prompts (use weekly)

1. **Pipeline scrub:** List every open opp; next action within 24 hours or kill.  
2. **Attach rate:** Of Foundation/Velocity clients without AI, book 3 upsell demos this week.  
3. **Oxford list build:** 50 new ICP contacts (agents/PMs/GCs) into CRM every Monday.  
4. **Cash:** Invoice all setup before build week; chase AR >7 days every Friday.  
5. **Model update:** Replace illustrative customers in `src/data/customers.ts` with real QBO client names/MRR monthly.

---

## 8. Risks and constraints

- Illustrative dashboard data is not live books.  
- SMS/cold outreach must follow TCPA / consent rules.  
- Do not promise specific lead volumes — promise speed-to-lead and qualification.  
- If books are 6+ months behind, sell clean-up before Velocity/Alpha.  
- Bundled Alpha MRR already includes AI — do not also bill $149 AI on the same account unless a la carte.

---

## 9. Where to operate this in software

| Artifact | Location |
|---|---|
| Live dashboard | http://127.0.0.1:43211 |
| Pricing / costs / funnel drivers | `src/data/assumptions.ts` |
| AI SKU constants | `aiLeadCaptureSkus` in assumptions file |
| Illustrative CRM | `src/data/customers.ts` |
| Formulas | `docs/FORMULAS.md` |
| Google Sheet | see `spreadsheet.json` |
