export type RevenueStream =
  | "setup"
  | "recurring"
  | "usage_overage"
  | "addon"
  | "one_time_service";

export type TierId = "starter" | "growth" | "premium" | "custom";

export type DataProvenance = "actual" | "planning_illustration" | "assumption";

export type CustomerStatus = "lead" | "opportunity" | "signed" | "active" | "churned" | "paused";

export interface PricingTier {
  id: TierId;
  name: string;
  setupFee: number;
  monthlyRecurring: number;
  includedVoiceMinutes: number;
  overagePerMinute: number;
  includesWebsite: boolean;
  includesVoiceAgent: boolean;
  includesBooking: boolean;
  includesPremiumIntegrations: boolean;
  estimatedOnboardingHours: number;
  notes: string;
}

export interface UnitCostAssumptions {
  /** Blended all-in voice AI + telephony $/minute. PLANNING ASSUMPTION — verify against invoices. */
  voiceCostPerMinute: number;
  hostingPerSiteMonthly: number;
  phoneNumberMonthly: number;
  crmSoftwareAllocatedMonthly: number;
  paymentProcessingRate: number;
  onboardingLaborHourly: number;
  supportLaborHourly: number;
  supportHoursPerCustomerMonthly: number;
  /** Shared platform tools allocated across active customers later. */
  sharedToolsMonthly: number;
  provenance: DataProvenance;
  sources: string[];
}

export interface OperatingExpenseLine {
  id: string;
  name: string;
  monthlyAmount: number;
  category: "sales" | "tools" | "labor" | "admin" | "marketing";
  provenance: DataProvenance;
}

export interface FunnelAssumptions {
  monthlyLeads: number;
  leadToAppointmentRate: number;
  appointmentShowRate: number;
  showToCloseRate: number;
  avgDaysLeadToClose: number;
  monthlyLogoChurnRate: number;
  monthlyExpansionRate: number;
  mixStarter: number;
  mixGrowth: number;
  mixPremium: number;
  scenario: "conservative" | "base" | "aggressive";
  provenance: DataProvenance;
}

export interface Customer {
  id: string;
  name: string;
  tierId: TierId;
  status: CustomerStatus;
  setupFeeContracted: number;
  mrrContracted: number;
  billingFrequency: "monthly" | "annual";
  activationDate: string | null;
  cancellationDate: string | null;
  cancellationReason: string | null;
  leadSource: string;
  acquisitionCostAttributed: number;
  voiceMinutesUsedLast30d: number;
  setupInvoiced: number;
  setupCollected: number;
  recurringInvoicedMtd: number;
  recurringCollectedMtd: number;
  addonMrr: number;
  provenance: DataProvenance;
}

export interface Opportunity {
  id: string;
  name: string;
  stage: "qualified" | "appointment_booked" | "appointment_held" | "proposal" | "won" | "lost";
  tierId: TierId;
  expectedSetup: number;
  expectedMrr: number;
  leadSource: string;
  acquisitionCostAttributed: number;
  createdDate: string;
  closeDate: string | null;
  provenance: DataProvenance;
}

export interface CashPosition {
  operatingCash: number;
  provenance: DataProvenance;
  asOf: string;
}

export interface ModelAssumptions {
  businessName: string;
  currency: "USD";
  targetGrossMargin: number;
  pricingTiers: PricingTier[];
  unitCosts: UnitCostAssumptions;
  operatingExpenses: OperatingExpenseLine[];
  funnel: Record<"conservative" | "base" | "aggressive", FunnelAssumptions>;
  cash: CashPosition;
  taxRateAssumption: number;
  revenueRecognitionNotes: string[];
}
