import data from "@/data/f500.json";
import { CompanyRevenueChart, IndustryRevenueChart } from "@/components/dashboard-charts";
import { CompanyTable } from "@/components/company-table";
import {
  formatBillions,
  formatCompact,
  formatPercent,
  formatTrillions,
} from "@/lib/utils";

const sheetUrl =
  "https://docs.google.com/spreadsheets/d/1y1etk77QLopdToYomWSkjGGYxyCjy9WyvJtb26_r3NM/edit#gid=1516245268";

export default function DashboardPage() {
  const { summary, concentration, top20, top100, industries, states, meta } = data;

  const companyChart = top20.map((r) => ({
    company: r.company,
    revenueBillions: Number((r.revenueMillions / 1000).toFixed(1)),
  }));

  const industryChart = industries.map((r) => ({
    industry: r.industry.length > 18 ? `${r.industry.slice(0, 16)}…` : r.industry,
    revenueBillions: Number((r.revenueMillions / 1000).toFixed(1)),
  }));

  const concRows = [
    { label: "Top 10", value: concentration.top10, tone: "bg-[var(--accent)]" },
    { label: "Top 50", value: concentration.top50, tone: "bg-[var(--chart-2)]" },
    { label: "Top 100", value: concentration.top100, tone: "bg-[var(--chart-4)]" },
    { label: "Rest 101–500", value: concentration.rest, tone: "bg-[var(--signal)]" },
  ];

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 md:px-8 md:py-10">
      <header className="animate-rise mb-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent-deep)]">
              Revenue model
            </p>
            <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl leading-none tracking-tight text-[var(--ink)] md:text-5xl">
              Top 500
            </h1>
            <p className="mt-3 max-w-2xl text-base text-[var(--ink-soft)] md:text-lg">
              U.S. largest companies by FY2024 revenue — scale, concentration, and
              sector mix in one view.
            </p>
          </div>
          <a
            href={sheetUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-xl bg-[var(--ink)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--accent-deep)]"
          >
            Open Google Sheet
          </a>
        </div>
        <p className="mt-4 text-xs text-[var(--muted)]">{meta.source}</p>
      </header>

      <section className="mb-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          {
            label: "Total revenue",
            value: formatTrillions(summary.totalRevenueM),
            hint: `${formatCompact(summary.totalRevenueM * 1_000_000)} USD`,
            delay: "animate-rise",
          },
          {
            label: "Companies",
            value: String(summary.companies),
            hint: `${summary.industries} industries · ${summary.states} states`,
            delay: "animate-rise-delay-1",
          },
          {
            label: "Employees",
            value: formatCompact(summary.totalEmployees),
            hint: `Avg revenue ${formatBillions(summary.avgRevenueM)}`,
            delay: "animate-rise-delay-2",
          },
          {
            label: "Median revenue",
            value: formatBillions(summary.medianRevenueM),
            hint: "Per company in the list",
            delay: "animate-rise-delay-3",
          },
        ].map((kpi) => (
          <article
            key={kpi.label}
            className={`${kpi.delay} rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4 shadow-sm backdrop-blur`}
          >
            <p className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              {kpi.label}
            </p>
            <p className="mt-2 font-[family-name:var(--font-display)] text-3xl tracking-tight text-[var(--ink)]">
              {kpi.value}
            </p>
            <p className="mt-1 text-sm text-[var(--ink-soft)]">{kpi.hint}</p>
          </article>
        ))}
      </section>

      <section className="animate-rise-delay-1 mb-6 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur md:p-6">
        <h2 className="font-[family-name:var(--font-display)] text-2xl tracking-tight">
          Revenue concentration
        </h2>
        <p className="mt-1 text-sm text-[var(--ink-soft)]">
          How much of the ~$18.9T stack sits in the largest cohorts.
        </p>
        <div className="mt-5 space-y-3">
          {concRows.map((row) => {
            const share = row.value / summary.totalRevenueM;
            return (
              <div key={row.label}>
                <div className="mb-1 flex items-baseline justify-between gap-3 text-sm">
                  <span className="font-medium text-[var(--ink)]">{row.label}</span>
                  <span className="tabular-nums text-[var(--ink-soft)]">
                    {formatTrillions(row.value)} · {formatPercent(share)}
                  </span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-black/5">
                  <div
                    className={`conc-bar h-full rounded-full ${row.tone}`}
                    style={{ width: `${Math.max(share * 100, 2)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="mb-6 grid gap-6 lg:grid-cols-2">
        <article className="animate-rise-delay-2 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur md:p-6">
          <h2 className="font-[family-name:var(--font-display)] text-2xl tracking-tight">
            Top 20 by revenue
          </h2>
          <p className="mt-1 mb-3 text-sm text-[var(--ink-soft)]">
            Walmart leads at {formatBillions(top20[0].revenueMillions)}.
          </p>
          <CompanyRevenueChart data={companyChart} />
        </article>

        <article className="animate-rise-delay-3 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur md:p-6">
          <h2 className="font-[family-name:var(--font-display)] text-2xl tracking-tight">
            Top industries
          </h2>
          <p className="mt-1 mb-3 text-sm text-[var(--ink-soft)]">
            Healthcare is the largest sector bucket in this model.
          </p>
          <IndustryRevenueChart data={industryChart} />
        </article>
      </section>

      <section className="animate-rise-delay-2 mb-6 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur md:p-6">
        <h2 className="font-[family-name:var(--font-display)] text-2xl tracking-tight">
          Top HQ states
        </h2>
        <p className="mt-1 mb-4 text-sm text-[var(--ink-soft)]">
          Where the revenue base is headquartered.
        </p>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {states.slice(0, 9).map((s, i) => (
            <div
              key={s.state}
              className="flex items-center justify-between rounded-xl border border-[var(--line)] bg-white/50 px-3 py-2.5"
            >
              <div className="flex items-center gap-3">
                <span className="w-5 text-xs tabular-nums text-[var(--muted)]">{i + 1}</span>
                <span className="font-medium">{s.state}</span>
              </div>
              <span className="tabular-nums text-sm text-[var(--ink-soft)]">
                {formatBillions(s.revenueMillions, 0)}
              </span>
            </div>
          ))}
        </div>
      </section>

      <CompanyTable rows={top100} />

      <footer className="mt-10 border-t border-[var(--line)] pt-4 text-xs text-[var(--muted)]">
        Live web dashboard mirroring the Google Sheets model. Full 500-company
        table and growth scenarios live in the sheet.
      </footer>
    </main>
  );
}
