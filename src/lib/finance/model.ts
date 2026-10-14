import { assumptions } from "@/data/assumptions";
import { customers, opportunities } from "@/data/customers";
import { buildForecast } from "./forecast";
import {
  activePayingCustomers,
  breakEvenRevenue,
  calculateArpa,
  calculateArr,
  calculateCac,
  calculateCacPaybackMonths,
  calculateLogoChurn,
  calculateLtv,
  calculateMrr,
  calculateNrr,
  cashRunwayMonths,
  collectedCashMtd,
  customerMonthlyRecurring,
  directCostForCustomer,
  minPriceForMargin,
  overageRevenue,
  sumOpEx,
  tierUnitEconomics,
} from "./metrics";
import type { FunnelAssumptions } from "./types";

export type ScenarioKey = "conservative" | "base" | "aggressive";

export function buildAgencyModel(scenario: ScenarioKey = "base") {
  const tiers = assumptions.pricingTiers;
  const unitCosts = assumptions.unitCosts;
  const funnel = assumptions.funnel[scenario];
  const opEx = sumOpEx(assumptions.operatingExpenses);
  // Shared tools also listed in OpEx — avoid double-count in COGS: unitCosts.sharedToolsMonthly
  // is informational; OpEx line "tools" is the P&L charge.

  const active = activePayingCustomers(customers);
  const mrr = calculateMrr(customers);
  const arr = calculateArr(mrr);

  const usageRev = customers.reduce(
    (s, c) => s + overageRevenue({ customer: c, tier: tiers.find((t) => t.id === c.tierId) }),
    0,
  );

  const directCosts = active.reduce((s, c) => {
    const tier = tiers.find((t) => t.id === c.tierId);
    return s + directCostForCustomer({ customer: c, tier, unitCosts });
  }, 0);

  const recurringRecognized = mrr;
  const setupRecognized = customers.reduce((s, c) => s + c.setupCollected, 0);
  // For MTD snapshot we treat illustrative setupCollected as historical not this month —
  // show setup MTD only from signed-not-yet fully conceptually; document: use recurring + usage for "this month" GP.
  const recognizedThisMonthRecurringAndUsage = recurringRecognized + usageRev;
  const grossProfit = recognizedThisMonthRecurringAndUsage - directCosts;
  const grossMargin =
    recognizedThisMonthRecurringAndUsage > 0
      ? grossProfit / recognizedThisMonthRecurringAndUsage
      : null;
  const operatingProfit = grossProfit - opEx;

  const arpa = calculateArpa(mrr, active.length);

  // Early-stage churn from illustrative history (Feb–Oct window including 1 churn from start cohort).
  const logoChurn = calculateLogoChurn({
    customers,
    periodStart: "2026-09-01",
    periodEnd: "2026-09-30",
  });

  // Starting MRR for Sep: approximate from customers active at Sep 1.
  const startingSepMrr = customers
    .filter((c) => {
      if (!c.activationDate || c.activationDate > "2026-09-01") return false;
      if (c.cancellationDate && c.cancellationDate <= "2026-09-01") return false;
      return true;
    })
    .reduce((s, c) => {
      // For churned mid-month, still count their contracted MRR at start
      const base =
        c.billingFrequency === "annual" ? c.mrrContracted / 12 : c.mrrContracted;
      const addons = c.billingFrequency === "annual" ? c.addonMrr / 12 : c.addonMrr;
      return s + base + addons;
    }, 0);

  const churnedMrrSep = customers
    .filter(
      (c) =>
        c.cancellationDate &&
        c.cancellationDate > "2026-09-01" &&
        c.cancellationDate <= "2026-09-30",
    )
    .reduce((s, c) => {
      const base =
        c.billingFrequency === "annual" ? c.mrrContracted / 12 : c.mrrContracted;
      return s + base;
    }, 0);

  const nrr = calculateNrr({
    startingMrr: startingSepMrr,
    expansionMrr: 0,
    contractionMrr: 0,
    churnedMrr: churnedMrrSep,
  });

  const newCustomersLast90d = customers.filter(
    (c) => c.activationDate && c.activationDate >= "2026-07-01" && c.status !== "lead",
  );
  const cacSpend = newCustomersLast90d.reduce((s, c) => s + c.acquisitionCostAttributed, 0);
  // Only count activated as acquired
  const activatedNew = newCustomersLast90d.filter((c) => c.activationDate).length;
  const cac = calculateCac(cacSpend, activatedNew);

  const assumedChurnForLtv = logoChurn && logoChurn > 0 ? logoChurn : funnel.monthlyLogoChurnRate;
  const ltv =
    arpa != null && grossMargin != null
      ? calculateLtv({
          arpa,
          grossMargin: Math.max(grossMargin, 0),
          monthlyLogoChurn: assumedChurnForLtv,
        })
      : null;

  const cacPayback =
    cac != null && arpa != null && grossMargin != null
      ? calculateCacPaybackMonths({ cac, arpa, grossMargin: Math.max(grossMargin, 0) })
      : null;

  const variableCostRate =
    recognizedThisMonthRecurringAndUsage > 0
      ? directCosts / recognizedThisMonthRecurringAndUsage
      : 0.25;

  const breakEven = breakEvenRevenue({
    fixedMonthlyOpEx: opEx,
    variableCostRate,
  });

  const monthlyNetBurn = operatingProfit < 0 ? -operatingProfit : 0;
  const runway = cashRunwayMonths({
    operatingCash: assumptions.cash.operatingCash,
    monthlyNetBurn,
  });

  const tierEconomics = tiers.map((tier) => {
    const assumedMinutes =
      tier.id === "starter" ? 0 : tier.id === "growth" ? 0 : 150;
    const econ = tierUnitEconomics({ tier, unitCosts, assumedMonthlyMinutes: assumedMinutes });
    const minPrice = minPriceForMargin(econ.directMonthlyCost, assumptions.targetGrossMargin);
    return {
      tier,
      assumedMinutes,
      ...econ,
      minPriceForTargetMargin: minPrice,
      targetMargin: assumptions.targetGrossMargin,
    };
  });

  const mrrByTier = tiers.map((tier) => ({
    tierId: tier.id,
    name: tier.name,
    customers: active.filter((c) => c.tierId === tier.id).length,
    mrr: active
      .filter((c) => c.tierId === tier.id)
      .reduce((s, c) => s + customerMonthlyRecurring(c), 0),
  }));

  const forecast = buildForecast({
    funnel,
    tiers,
    months: 12,
    startingCustomers: active.length,
    startingMrr: mrr,
    fixedOpExMonthly: opEx,
    variableCostRateOfRecurring: Math.min(Math.max(variableCostRate, 0.05), 0.6),
    startingCash: assumptions.cash.operatingCash,
  });

  const forecastsAll = {
    conservative: buildScenarioForecast("conservative", active.length, mrr, opEx, variableCostRate),
    base: buildScenarioForecast("base", active.length, mrr, opEx, variableCostRate),
    aggressive: buildScenarioForecast("aggressive", active.length, mrr, opEx, variableCostRate),
  };

  const pipelineOpen = opportunities.filter((o) => !["won", "lost"].includes(o.stage));
  const pipelineValue = pipelineOpen.reduce((s, o) => s + o.expectedMrr * 12 + o.expectedSetup, 0);
  const pipelineMrr = pipelineOpen.reduce((s, o) => s + o.expectedMrr, 0);

  const customerContributions = active.map((c) => {
    const tier = tiers.find((t) => t.id === c.tierId);
    const direct = directCostForCustomer({ customer: c, tier, unitCosts });
    const recurring = customerMonthlyRecurring(c);
    const usage = overageRevenue({ customer: c, tier });
    const revenue = recurring + usage;
    return {
      id: c.id,
      name: c.name,
      tierId: c.tierId,
      revenue,
      directCost: direct,
      contribution: revenue - direct,
      margin: revenue > 0 ? (revenue - direct) / revenue : null,
      minutes: c.voiceMinutesUsedLast30d,
      unprofitableFlag: revenue - direct < 0,
    };
  });

  return {
    disclaimer:
      "Planning / illustrative data in use. LTV, churn, and NRR are early-stage estimates — not statistically reliable.",
    scenario,
    funnel,
    mrr,
    arr,
    usageRev,
    activeCustomers: active.length,
    arpa,
    grossProfit,
    grossMargin,
    operatingExpenses: opEx,
    operatingProfit,
    collectedCashMtd: collectedCashMtd(customers),
    recognizedRecurring: recurringRecognized,
    recognizedSetupHistorical: setupRecognized,
    recognizedUsage: usageRev,
    cac,
    ltv,
    cacPayback,
    logoChurn,
    nrr,
    breakEven,
    runway,
    monthlyNetBurn,
    cash: assumptions.cash,
    tierEconomics,
    mrrByTier,
    forecast,
    forecastsAll,
    pipelineOpen,
    pipelineValue,
    pipelineMrr,
    customerContributions,
    customers,
    opportunities,
    assumptions,
    recognitionNotes: assumptions.revenueRecognitionNotes,
  };
}

function buildScenarioForecast(
  key: ScenarioKey,
  startingCustomers: number,
  startingMrr: number,
  opEx: number,
  variableCostRate: number,
) {
  const funnel: FunnelAssumptions = assumptions.funnel[key];
  return buildForecast({
    funnel,
    tiers: assumptions.pricingTiers,
    months: 12,
    startingCustomers,
    startingMrr,
    fixedOpExMonthly: opEx,
    variableCostRateOfRecurring: Math.min(Math.max(variableCostRate, 0.05), 0.6),
    startingCash: assumptions.cash.operatingCash,
  });
}

export type AgencyModel = ReturnType<typeof buildAgencyModel>;
