import { describe, expect, it } from "vitest";
import { buildForecast } from "./forecast";
import { assumptions } from "@/data/assumptions";

describe("forecast", () => {
  it("builds 12 months without negative customers and growing under base funnel", () => {
    const rows = buildForecast({
      funnel: assumptions.funnel.base,
      tiers: assumptions.pricingTiers,
      months: 12,
      startingCustomers: 4,
      startingMrr: 5000,
      fixedOpExMonthly: 5500,
      variableCostRateOfRecurring: 0.25,
      startingCash: 12000,
    });
    expect(rows).toHaveLength(12);
    expect(rows.every((r) => r.endingCustomers >= 0)).toBe(true);
    expect(rows[11].endingMrr).toBeGreaterThan(rows[0].endingMrr);
  });

  it("does not treat leads as customers — only closed logos add MRR", () => {
    const zeroClose = {
      ...assumptions.funnel.base,
      showToCloseRate: 0,
      monthlyExpansionRate: 0,
    };
    const rows = buildForecast({
      funnel: zeroClose,
      tiers: assumptions.pricingTiers,
      months: 3,
      startingCustomers: 2,
      startingMrr: 2000,
      fixedOpExMonthly: 1000,
      variableCostRateOfRecurring: 0.2,
    });
    expect(rows.every((r) => r.newCustomers === 0)).toBe(true);
    expect(rows[2].endingMrr).toBeLessThan(2000); // churn still applies without expansion
  });
});
