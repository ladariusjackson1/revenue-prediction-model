import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBillions(millions: number, digits = 1) {
  return `$${(millions / 1000).toFixed(digits)}B`;
}

export function formatTrillions(millions: number, digits = 2) {
  return `$${(millions / 1_000_000).toFixed(digits)}T`;
}

export function formatCompact(n: number) {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n);
}

export function formatPercent(value: number, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}
