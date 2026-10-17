import type { Customer, OperatingExpenseLine, PricingTier, UnitCostAssumptions } from "./types";

/** Normalize contracted recurring to monthly. Annual contracts → /12. Setup never included. */
export function customerMonthlyRecurring(c: Customer): number {
  if (c.status !== "active") return 0;
  const base = c.billingFrequency === "annual" ? c.mrrContracted / 12 : c.mrrContracted;
  const addons = c.billingFrequency === "annual" ? c.addonMrr / 12 : c.addonMrr;
  return base + addons;
}

export function calculateMrr(customers: Customer[]): number {
  return customers.reduce((sum, c) => sum + customerMonthlyRecurring(c), 0);
}

/** ARR is annualized run-rate of current MRR — not trailing twelve-month revenue. */
export function calculateArr(mrr: number): number {
  return mrr * 12;
}

export function activePayingCustomers(customers: Customer[]): Customer[] {
  return customers.filter((c) => c.status === "active" && customerMonthlyRecurring(c) > 0);
}

export function calculateArpa(mrr: number, activeCount: number): number | null {
  if (activeCount <= 0) return null;
  return mrr / activeCount;
}

/**
 * Logo churn for a period: cancelled during period / active at period start.
 * Requires activationDate and cancellationDate. Returns null if start cohort empty.
 */
export function calculateLogoChurn(args: {
  customers: Customer[];
  periodStart: string;
  periodEnd: string;
}): number | null {
  const { customers, periodStart, periodEnd } = args;
  const startActive = customers.filter((c) => {
    if (!c.activationDate || c.activationDate > periodStart) return false;
    if (c.cancellationDate && c.cancellationDate <= periodStart) return false;
    return true;
  });
  if (startActive.length === 0) return null;
  const lost = startActive.filter(
    (c) => c.cancellationDate && c.cancellationDate > periodStart && c.cancellationDate <= periodEnd,
  );
  return lost.length / startActive.length;
}

/**
 * Gross revenue churn: MRR lost from cancellations + downgrades in period / starting MRR.
 * Expansions are excluded from the numerator (use NRR for net view).
 */
export function calculateRevenueChurn(args: {
  startingMrr: number;
  lostMrr: number;
}): number | null {
  if (args.startingMrr <= 0) return null;
  return args.lostMrr / args.startingMrr;
}

/**
 * NRR = (start + expansion - contraction - churn) / start.
 * Early-stage: label when history < 3 months of cohort data.
 */
export function calculateNrr(args: {
  startingMrr: number;
  expansionMrr: number;
  contractionMrr: number;
  churnedMrr: number;
}): number | null {
  if (args.startingMrr <= 0) return null;
  return (
    (args.startingMrr + args.expansionMrr - args.contractionMrr - args.churnedMrr) /
    args.startingMrr
  );
}

export function calculateCac(totalAcquisitionCost: number, newCustomers: number): number | null {
  if (newCustomers <= 0) return null;
  return totalAcquisitionCost / newCustomers;
}

/**
 * Simple LTV (gross-profit based): ARPA * grossMargin * (1 / monthlyLogoChurn).
 * Requires positive churn. Label as early-stage estimate when churn is assumed.
 */
export function calculateLtv(args: {
  arpa: number;
  grossMargin: number;
  monthlyLogoChurn: number;
}): number | null {
  if (args.monthlyLogoChurn <= 0 || args.arpa <= 0) return null;
  const months = 1 / args.monthlyLogoChurn;
  return args.arpa * args.grossMargin * months;
}

export function calculateCacPaybackMonths(args: {
  cac: number;
  arpa: number;
  grossMargin: number;
}): number | null {
  const monthlyGp = args.arpa * args.grossMargin;
  if (monthlyGp <= 0 || args.cac <= 0) return null;
  return args.cac / monthlyGp;
}

export function sumOpEx(lines: OperatingExpenseLine[]): number {
  return lines.reduce((s, l) => s + l.monthlyAmount, 0);
}

export function directCostForCustomer(args: {
  customer: Customer;
  tier: PricingTier | undefined;
  unitCosts: UnitCostAssumptions;
}): number {
  const { customer, tier, unitCosts } = args;
  const included = tier?.includedVoiceMinutes ?? 0;
  const billableMins = Math.max(0, customer.voiceMinutesUsedLast30d);
  const overageMins = Math.max(0, billableMins - included);
  // Delivery cost uses actual minutes * infra cost (not customer overage price).
  const voiceCost = billableMins * unitCosts.voiceCostPerMinute;
  const hosting = tier?.includesWebsite ? unitCosts.hostingPerSiteMonthly : 0;
  const phone = tier?.includesVoiceAgent ? unitCosts.phoneNumberMonthly : 0;
  const support =
    unitCosts.supportHoursPerCustomerMonthly * unitCosts.supportLaborHourly;
  const processing =
    customerMonthlyRecurring(customer) * unitCosts.paymentProcessingRate;
  // Overage revenue is separate; cost still includes all minutes.
  void overageMins;
  return voiceCost + hosting + phone + support + processing + unitCosts.crmSoftwareAllocatedMonthly;
}

export function overageRevenue(args: {
  customer: Customer;
  tier: PricingTier | undefined;
}): number {
  if (!args.tier || args.customer.status !== "active") return 0;
  const over = Math.max(0, args.customer.voiceMinutesUsedLast30d - args.tier.includedVoiceMinutes);
  return over * args.tier.overagePerMinute;
}

export function setupOnboardingCost(args: {
  tier: PricingTier;
  unitCosts: UnitCostAssumptions;
}): number {
  return args.tier.estimatedOnboardingHours * args.unitCosts.onboardingLaborHourly;
}

export function tierUnitEconomics(args: {
  tier: PricingTier;
  unitCosts: UnitCostAssumptions;
  assumedMonthlyMinutes: number;
}): {
  setupFee: number;
  monthlyRecurring: number;
  directMonthlyCost: number;
  grossProfitMonthly: number;
  grossMargin: number | null;
  setupDirectCost: number;
  setupGrossProfit: number;
  minMonthlyPriceForTargetMargin: number;
  unprofitableAtMinutes: number | null;
} {
  const { tier, unitCosts, assumedMonthlyMinutes } = args;
  const voiceCost = assumedMonthlyMinutes * unitCosts.voiceCostPerMinute;
  const hosting = tier.includesWebsite ? unitCosts.hostingPerSiteMonthly : 0;
  const phone = tier.includesVoiceAgent ? unitCosts.phoneNumberMonthly : 0;
  const support = unitCosts.supportHoursPerCustomerMonthly * unitCosts.supportLaborHourly;
  const processing = tier.monthlyRecurring * unitCosts.paymentProcessingRate;
  const directMonthlyCost =
    voiceCost + hosting + phone + support + processing + unitCosts.crmSoftwareAllocatedMonthly;
  const grossProfitMonthly = tier.monthlyRecurring - directMonthlyCost;
  const grossMargin =
    tier.monthlyRecurring > 0 ? grossProfitMonthly / tier.monthlyRecurring : null;
  const setupDirectCost = setupOnboardingCost({ tier, unitCosts });
  const setupGrossProfit = tier.setupFee - setupDirectCost;

  // Price needed so (P - variable)/P = target is handled by caller with target margin.
  // Here: min price for margin m: P = direct / (1 - m) when costs treated as fixed at this usage.
  const target = 0.7; // default documentation target; caller may override
  const minMonthlyPriceForTargetMargin =
    target < 1 ? directMonthlyCost / (1 - target) : directMonthlyCost;

  // Find minutes where gross profit hits zero at current price (if voice is only variable scaling).
  const fixedPart = hosting + phone + support + processing + unitCosts.crmSoftwareAllocatedMonthly;
  const room = tier.monthlyRecurring - fixedPart;
  const unprofitableAtMinutes =
    unitCosts.voiceCostPerMinute > 0 && room > 0
      ? Math.floor(room / unitCosts.voiceCostPerMinute) + 1
      : null;

  return {
    setupFee: tier.setupFee,
    monthlyRecurring: tier.monthlyRecurring,
    directMonthlyCost,
    grossProfitMonthly,
    grossMargin,
    setupDirectCost,
    setupGrossProfit,
    minMonthlyPriceForTargetMargin,
    unprofitableAtMinutes,
  };
}

export function minPriceForMargin(directCost: number, targetMargin: number): number | null {
  if (targetMargin >= 1 || targetMargin < 0) return null;
  return directCost / (1 - targetMargin);
}

export function breakEvenRevenue(args: {
  fixedMonthlyOpEx: number;
  variableCostRate: number;
}): number | null {
  // Revenue R such that R - variableCostRate*R - fixed = 0 → R*(1-v)=fixed
  if (args.variableCostRate >= 1) return null;
  return args.fixedMonthlyOpEx / (1 - args.variableCostRate);
}

export function cashRunwayMonths(args: {
  operatingCash: number;
  monthlyNetBurn: number;
}): number | null {
  if (args.monthlyNetBurn <= 0) return null; // not burning
  if (args.operatingCash <= 0) return 0;
  return args.operatingCash / args.monthlyNetBurn;
}

export function recognizedRevenueMtd(customers: Customer[]): {
  setupRecognized: number;
  recurringRecognized: number;
  usageRecognized: number;
  total: number;
} {
  // Recognition policy (documented): setup recognized on activation/collection for this model;
  // recurring recognized as monthly contracted amount for active customers this month;
  // usage = overage (computed by caller and passed via recurringCollected for simplicity here we use invoiced fields).
  const setupRecognized = customers.reduce((s, c) => s + c.setupCollected, 0);
  const recurringRecognized = customers
    .filter((c) => c.status === "active")
    .reduce((s, c) => s + customerMonthlyRecurring(c), 0);
  const usageRecognized = 0; // filled by dashboard with overageRevenue sum
  return {
    setupRecognized,
    recurringRecognized,
    usageRecognized,
    total: setupRecognized + recurringRecognized + usageRecognized,
  };
}

export function collectedCashMtd(customers: Customer[]): number {
  return customers.reduce(
    (s, c) => s + c.setupCollected + c.recurringCollectedMtd,
    0,
  );
}

export function safeDiv(n: number, d: number): number | null {
  if (d === 0 || !Number.isFinite(n) || !Number.isFinite(d)) return null;
  return n / d;
}
