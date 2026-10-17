import type { ModelAssumptions } from "@/lib/finance/types";

/**
 * Double Eagle Financial LLC — assumption registry.
 * Provenance "assumption" = planning input to verify against QBO / bank / CRM.
 *
 * Tier mapping (Grand Slam Offer):
 * - starter  = The Foundation (QBO bookkeeping)
 * - growth   = The Velocity Suite (bookkeeping + Q4 velocity)
 * - premium  = The Enterprise Alpha (full financials + AI lead capture)
 *
 * AI Lead Capture add-on economics (stackable): setup $499–$999, MRR $99–$149
 * are modeled inside Premium setup/MRR and as addonMrr on customers where sold a la carte.
 */
export const assumptions: ModelAssumptions = {
  businessName: "Double Eagle Financial LLC",
  currency: "USD",
  targetGrossMargin: 0.7,
  pricingTiers: [
    {
      id: "starter",
      name: "The Foundation",
      setupFee: 750,
      monthlyRecurring: 350,
      includedVoiceMinutes: 0,
      overagePerMinute: 0,
      includesWebsite: false,
      includesVoiceAgent: false,
      includesBooking: false,
      includesPremiumIntegrations: false,
      estimatedOnboardingHours: 6,
      notes:
        "QuickBooks Online bookkeeping + monthly reconciliations for RE agents, PMs, and GCs. Clean-up billed separately at $75–$125/hr if books are behind.",
    },
    {
      id: "growth",
      name: "The Velocity Suite",
      setupFee: 1250,
      monthlyRecurring: 550,
      includedVoiceMinutes: 0,
      overagePerMinute: 0,
      includesWebsite: false,
      includesVoiceAgent: false,
      includesBooking: false,
      includesPremiumIntegrations: false,
      estimatedOnboardingHours: 10,
      notes:
        "Foundation + Q4 Financial Velocity Package (tax-ready close, P&L/cash dashboards, quarterly CFO-lite review). Optional AI Lead Capture add-on: $499 setup + $99/mo.",
    },
    {
      id: "premium",
      name: "The Enterprise Alpha",
      setupFee: 999,
      monthlyRecurring: 699,
      includedVoiceMinutes: 150,
      overagePerMinute: 0.35,
      includesWebsite: false,
      includesVoiceAgent: true,
      includesBooking: true,
      includesPremiumIntegrations: true,
      estimatedOnboardingHours: 14,
      notes:
        "Full financials + 24/7 AI Lead Capture & Qualifier + CRM workflow integration. AI package component priced $999 setup + $149/mo inside the stack; bookkeeping retainer included in MRR. Overage on AI conversation minutes beyond allowance.",
    },
  ],
  unitCosts: {
    // Chat/SMS lead bots are cheaper than full voice; keep blended planning rate for voice-capable Alpha.
    voiceCostPerMinute: 0.1,
    hostingPerSiteMonthly: 0,
    phoneNumberMonthly: 1.15,
    crmSoftwareAllocatedMonthly: 25,
    paymentProcessingRate: 0.029,
    onboardingLaborHourly: 55,
    supportLaborHourly: 45,
    supportHoursPerCustomerMonthly: 2,
    sharedToolsMonthly: 297,
    provenance: "assumption",
    sources: [
      "QBO Accountant / ProAdvisor tooling — verify seat costs",
      "AI lead bot infra (LLM + messaging) often below full voice; Alpha uses $0.10/min planning blend",
      "GoHighLevel / CRM ~$97–$297/mo shared — allocated per client as crmSoftwareAllocatedMonthly",
    ],
  },
  operatingExpenses: [
    {
      id: "founder_draw",
      name: "Founder labor allocation (Ladarius)",
      monthlyAmount: 3500,
      category: "labor",
      provenance: "assumption",
    },
    {
      id: "ads",
      name: "Outbound + local ads (Oxford / surrounding)",
      monthlyAmount: 600,
      category: "marketing",
      provenance: "assumption",
    },
    {
      id: "tools",
      name: "QBO + CRM + AI stack (shared)",
      monthlyAmount: 297,
      category: "tools",
      provenance: "assumption",
    },
    {
      id: "admin",
      name: "Admin / insurance / misc",
      monthlyAmount: 200,
      category: "admin",
      provenance: "assumption",
    },
  ],
  funnel: {
    conservative: {
      monthlyLeads: 30,
      leadToAppointmentRate: 0.22,
      appointmentShowRate: 0.7,
      showToCloseRate: 0.28,
      avgDaysLeadToClose: 14,
      monthlyLogoChurnRate: 0.04,
      monthlyExpansionRate: 0.03,
      mixStarter: 0.5,
      mixGrowth: 0.35,
      mixPremium: 0.15,
      scenario: "conservative",
      provenance: "assumption",
    },
    base: {
      monthlyLeads: 45,
      leadToAppointmentRate: 0.3,
      appointmentShowRate: 0.75,
      showToCloseRate: 0.35,
      avgDaysLeadToClose: 12,
      monthlyLogoChurnRate: 0.03,
      monthlyExpansionRate: 0.05,
      mixStarter: 0.35,
      mixGrowth: 0.4,
      mixPremium: 0.25,
      scenario: "base",
      provenance: "assumption",
    },
    aggressive: {
      monthlyLeads: 70,
      leadToAppointmentRate: 0.35,
      appointmentShowRate: 0.8,
      showToCloseRate: 0.4,
      avgDaysLeadToClose: 10,
      monthlyLogoChurnRate: 0.025,
      monthlyExpansionRate: 0.07,
      mixStarter: 0.25,
      mixGrowth: 0.4,
      mixPremium: 0.35,
      scenario: "aggressive",
      provenance: "assumption",
    },
  },
  cash: {
    operatingCash: 8500,
    provenance: "assumption",
    asOf: "2026-10-01",
  },
  taxRateAssumption: 0,
  revenueRecognitionNotes: [
    "Bookkeeping retainers: recognize monthly as service is delivered.",
    "Clean-up / catch-up fees: one-time; never in MRR.",
    "AI Lead Capture setup ($499–$999): one-time; never in MRR.",
    "AI Lead Capture MRR ($99–$149) and bookkeeping MRR: included in active MRR when status=active.",
    "Enterprise Alpha MRR ($699) bundles financials + AI component; do not double-count $149 AI if using bundled price.",
    "Contracted vs invoiced vs collected tracked on customer payment fields.",
  ],
};

/** A la carte AI Lead Capture SKUs (stack onto Foundation / Velocity). */
export const aiLeadCaptureSkus = [
  {
    id: "ai_capture_standard",
    name: "AI Lead Capture — Standard",
    setupFee: 499,
    monthlyRecurring: 99,
    target: "Real estate agents & small GCs",
    includes:
      "24/7 website/SMS lead qualifier, appointment booking link, CRM tag + notification, monthly transcript review",
  },
  {
    id: "ai_capture_pro",
    name: "AI Lead Capture — Pro (Property Managers)",
    setupFee: 999,
    monthlyRecurring: 149,
    target: "Property managers & multi-agent teams",
    includes:
      "Inbound lead + maintenance-request triage flows, CRM workflow automation, missed-call text-back, weekly optimization",
  },
] as const;

/** Baseline bookkeeping clean-up fee (one-time, non-MRR). */
export const cleanupFeeAssumptions = {
  hourlyRate: 95,
  typicalHoursBehind: 8,
  typicalCleanupFee: 760,
  note: "Charge $75–$125/hr based on messiness; quote after diagnostic. Never roll into MRR.",
} as const;
