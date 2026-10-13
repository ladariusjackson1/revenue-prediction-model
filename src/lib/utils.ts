import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatMoney(n: number | null | undefined, digits = 0): string {
  if (n == null || !Number.isFinite(n)) return "Unavailable";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(n);
}

export function formatCompact(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "Unavailable";
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n);
}

export function formatPercent(value: number | null | undefined, digits = 1): string {
  if (value == null || !Number.isFinite(value)) return "Unavailable";
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatMonths(value: number | null | undefined, digits = 1): string {
  if (value == null || !Number.isFinite(value)) return "Unavailable";
  return `${value.toFixed(digits)} mo`;
}
