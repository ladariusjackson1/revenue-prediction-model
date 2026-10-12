"use client";

import { useDeferredValue, useMemo, useState } from "react";
import { formatBillions, formatPercent } from "@/lib/utils";

type Row = {
  rank: number;
  company: string;
  industry: string;
  revenueMillions: number;
  employees: number;
  pctOfTotal: number;
  state: string;
};

export function CompanyTable({ rows }: { rows: Row[] }) {
  const [query, setQuery] = useState("");
  const deferred = useDeferredValue(query);

  const filtered = useMemo(() => {
    const q = deferred.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter(
      (r) =>
        r.company.toLowerCase().includes(q) ||
        r.industry.toLowerCase().includes(q) ||
        r.state.toLowerCase().includes(q),
    );
  }, [rows, deferred]);

  return (
    <section className="animate-rise-delay-3 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur md:p-6">
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="font-[family-name:var(--font-display)] text-2xl tracking-tight text-[var(--ink)]">
            Top 100 companies
          </h2>
          <p className="mt-1 text-sm text-[var(--ink-soft)]">
            Search by company, industry, or HQ state.
          </p>
        </div>
        <label className="block w-full md:w-72">
          <span className="sr-only">Search companies</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter companies…"
            className="w-full rounded-xl border border-[var(--line)] bg-white/80 px-3 py-2 text-sm text-[var(--ink)] outline-none ring-[var(--accent)] placeholder:text-[var(--muted)] focus:ring-2"
          />
        </label>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-[var(--muted)]">
              <th className="px-2 py-2 font-medium">Rank</th>
              <th className="px-2 py-2 font-medium">Company</th>
              <th className="px-2 py-2 font-medium">Industry</th>
              <th className="px-2 py-2 font-medium">Revenue</th>
              <th className="px-2 py-2 font-medium">Share</th>
              <th className="px-2 py-2 font-medium">State</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-2 py-8 text-center text-[var(--ink-soft)]">
                  No companies match “{query}”.
                </td>
              </tr>
            ) : (
              filtered.map((row) => (
                <tr
                  key={row.rank}
                  className="border-b border-[var(--line)]/70 transition-colors hover:bg-white/60"
                >
                  <td className="px-2 py-2.5 tabular-nums text-[var(--muted)]">{row.rank}</td>
                  <td className="px-2 py-2.5 font-medium text-[var(--ink)]">{row.company}</td>
                  <td className="px-2 py-2.5 text-[var(--ink-soft)]">{row.industry}</td>
                  <td className="px-2 py-2.5 tabular-nums">{formatBillions(row.revenueMillions)}</td>
                  <td className="px-2 py-2.5 tabular-nums">{formatPercent(row.pctOfTotal)}</td>
                  <td className="px-2 py-2.5">{row.state}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
