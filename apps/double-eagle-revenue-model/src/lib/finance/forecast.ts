import type { FunnelAssumptions, PricingTier } from "./types";

export interface ForecastMonth {
  monthIndex: number;
  label: string;
  newCustomers: number;
  churnedCustomers: number;
  endingCustomers: number;
  newMrr: number;
  churnedMrr: number;
  expansionMrr: number;
  endingMrr: number;
  setupRevenue: number;
  recurringRevenue: number;
  variableDeliveryCost: number;
  fixedOpEx: number;
  grossProfit: number;
  operatingProfit: number;
  cumulativeCash: number;
}

function weightedAvgMrr(funnel: FunnelAssumptions, tiers: PricingTier[]): number {
  const byId = Object.fromEntries(tiers.map((t) => [t.id, t]));
  const starter = byId.starter?.monthlyRecurring ?? 0;
  const growth = byId.growth?.monthlyRecurring ?? 0;
  const premium = byId.premium?.monthlyRecurring ?? 0;
  return (
    funnel.mixStarter * starter + funnel.mixGrowth * growth + funnel.mixPremium * premium
  );
}

function weightedAvgSetup(funnel: FunnelAssumptions, tiers: PricingTier[]): number {
  const byId = Object.fromEntries(tiers.map((t) => [t.id, t]));
  const starter = byId.starter?.setupFee ?? 0;
  const growth = byId.growth?.setupFee ?? 0;
  const premium = byId.premium?.setupFee ?? 0;
  return funnel.mixStarter * starter + funnel.mixGrowth * growth + funnel.mixPremium * premium;
}

/**
 * Driver-based 12-month cohort forecast.
 * Customers acquired in month M start contributing recurring revenue in month M (activation = close month).
 * Churn applies to beginning-of-month active base (logo churn rate).
 * No circular refs; pipeline stages are not double-counted — only closed new logos enter the base.
 */
export function buildForecast(args: {
  funnel: FunnelAssumptions;
  tiers: PricingTier[];
  months?: number;
  startingCustomers?: number;
  startingMrr?: number;
  fixedOpExMonthly: number;
  /** Approximate variable delivery cost as % of recurring revenue (planning). */
  variableCostRateOfRecurring: number;
  startingCash?: number;
  startDate?: Date;
}): ForecastMonth[] {
  const months = args.months ?? 12;
  const start = args.startDate ?? new Date();
  const avgMrr = weightedAvgMrr(args.funnel, args.tiers);
  const avgSetup = weightedAvgSetup(args.funnel, args.tiers);

  const closedFromFunnel =
    args.funnel.monthlyLeads *
    args.funnel.leadToAppointmentRate *
    args.funnel.appointmentShowRate *
    args.funnel.showToCloseRate;

  let customers = args.startingCustomers ?? 0;
  let mrr = args.startingMrr ?? 0;
  let cash = args.startingCash ?? 0;
  const rows: ForecastMonth[] = [];

  for (let i = 0; i < months; i++) {
    const d = new Date(start.getFullYear(), start.getMonth() + i, 1);
    const label = d.toLocaleString("en-US", { month: "short", year: "numeric" });

    const newCustomers = closedFromFunnel;
    const churnedCustomers = customers * args.funnel.monthlyLogoChurnRate;
    const churnedMrr = mrr * args.funnel.monthlyLogoChurnRate;
    const expansionMrr = mrr * args.funnel.monthlyExpansionRate;
    const newMrr = newCustomers * avgMrr;

    customers = Math.max(0, customers + newCustomers - churnedCustomers);
    mrr = Math.max(0, mrr + newMrr + expansionMrr - churnedMrr);

    const setupRevenue = newCustomers * avgSetup;
    const recurringRevenue = mrr;
    const variableDeliveryCost = recurringRevenue * args.variableCostRateOfRecurring;
    const fixedOpEx = args.fixedOpExMonthly;
    const grossProfit = setupRevenue + recurringRevenue - variableDeliveryCost;
    // Setup has labor COGS approximated inside variable for planning simplicity;
    // fixed OpEx deducted for operating profit.
    const operatingProfit = grossProfit - fixedOpEx;
    cash += operatingProfit;

    rows.push({
      monthIndex: i + 1,
      label,
      newCustomers,
      churnedCustomers,
      endingCustomers: customers,
      newMrr,
      churnedMrr,
      expansionMrr,
      endingMrr: mrr,
      setupRevenue,
      recurringRevenue,
      variableDeliveryCost,
      fixedOpEx,
      grossProfit,
      operatingProfit,
      cumulativeCash: cash,
    });
  }

  return rows;
}

export function averageDealCycleMonths(avgDaysLeadToClose: number): number {
  return avgDaysLeadToClose / 30;
}
