import { describe, expect, it } from "vitest";
import {
  calculateArr,
  calculateCac,
  calculateCacPaybackMonths,
  calculateLogoChurn,
  calculateLtv,
  calculateMrr,
  calculateNrr,
  customerMonthlyRecurring,
  minPriceForMargin,
} from "./metrics";
import type { Customer } from "./types";

function cust(partial: Partial<Customer> & Pick<Customer, "id" | "status">): Customer {
  return {
    name: partial.name ?? partial.id,
    tierId: "growth",
    setupFeeContracted: 0,
    mrrContracted: 1000,
    billingFrequency: "monthly",
    activationDate: "2026-01-01",
    cancellationDate: null,
    cancellationReason: null,
    leadSource: "test",
    acquisitionCostAttributed: 0,
    voiceMinutesUsedLast30d: 0,
    setupInvoiced: 0,
    setupCollected: 0,
    recurringInvoicedMtd: 0,
    recurringCollectedMtd: 0,
    addonMrr: 0,
    provenance: "planning_illustration",
    ...partial,
  };
}

describe("MRR / ARR", () => {
  it("excludes setup fees and inactive customers from MRR", () => {
    const list = [
      cust({ id: "a", status: "active", mrrContracted: 1497, setupFeeContracted: 3500 }),
      cust({ id: "b", status: "churned", mrrContracted: 1497 }),
      cust({ id: "c", status: "signed", mrrContracted: 1497 }),
    ];
    expect(calculateMrr(list)).toBe(1497);
    expect(calculateArr(1497)).toBe(1497 * 12);
  });

  it("normalizes annual billing to monthly", () => {
    const c = cust({
      id: "ann",
      status: "active",
      billingFrequency: "annual",
      mrrContracted: 17964,
    });
    expect(customerMonthlyRecurring(c)).toBe(1497);
  });
});

describe("churn / NRR / LTV / CAC", () => {
  it("computes logo churn", () => {
    const list = [
      cust({ id: "1", status: "active", activationDate: "2026-01-01" }),
      cust({
        id: "2",
        status: "churned",
        activationDate: "2026-01-01",
        cancellationDate: "2026-09-15",
      }),
      cust({ id: "3", status: "active", activationDate: "2026-09-10" }), // not in start cohort
    ];
    const churn = calculateLogoChurn({
      customers: list,
      periodStart: "2026-09-01",
      periodEnd: "2026-09-30",
    });
    expect(churn).toBeCloseTo(0.5);
  });

  it("computes NRR", () => {
    expect(
      calculateNrr({
        startingMrr: 10000,
        expansionMrr: 1000,
        contractionMrr: 500,
        churnedMrr: 1500,
      }),
    ).toBeCloseTo(0.9);
  });

  it("computes LTV and CAC payback", () => {
    const ltv = calculateLtv({ arpa: 1500, grossMargin: 0.7, monthlyLogoChurn: 0.05 });
    expect(ltv).toBeCloseTo(1500 * 0.7 * 20);
    const payback = calculateCacPaybackMonths({ cac: 420, arpa: 1500, grossMargin: 0.7 });
    expect(payback).toBeCloseTo(420 / (1500 * 0.7));
  });

  it("returns null CAC when no new customers", () => {
    expect(calculateCac(500, 0)).toBeNull();
  });
});

describe("pricing helpers", () => {
  it("min price for target margin", () => {
    expect(minPriceForMargin(300, 0.7)).toBeCloseTo(1000);
  });
});
