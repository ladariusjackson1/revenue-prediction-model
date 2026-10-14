"use client";

import { useMemo, useState, useTransition } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AgencyModel, ScenarioKey } from "@/lib/finance/model";
import { formatMoney, formatMonths, formatPercent } from "@/lib/utils";
import { MetricCard } from "./metric-card";
import { ILLUSTRATIVE_DISCLAIMER } from "@/data/customers";

export function ExecutiveDashboard({
  initial,
  models,
}: {
  initial: AgencyModel;
  models: Record<ScenarioKey, AgencyModel>;
}) {
  const [scenario, setScenario] = useState<ScenarioKey>("base");
  const [, startTransition] = useTransition();
  const model = models[scenario];

  const forecastChart = useMemo(
    () =>
      model.forecast.map((m) => ({
        label: m.label,
        MRR: Math.round(m.endingMrr),
        Setup: Math.round(m.setupRevenue),
        OpProfit: Math.round(m.operatingProfit),
      })),
    [model.forecast],
  );

  const scenarioCompare = useMemo(() => {
    const months = models.base.forecast.map((r) => r.label);
    return months.map((label, i) => ({
      label,
      Conservative: Math.round(models.conservative.forecast[i].endingMrr),
      Base: Math.round(models.base.forecast[i].endingMrr),
      Aggressive: Math.round(models.aggressive.forecast[i].endingMrr),
    }));
  }, [models]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-amber-500/30 bg-amber-50/80 px-4 py-3 text-sm text-amber-950">
        <strong>Early-stage / planning mode.</strong> {ILLUSTRATIVE_DISCLAIMER}{" "}
        {model.disclaimer}
      </div>

      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent-deep)]">
            Double Eagle Financial LLC
          </p>
          <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl tracking-tight text-[var(--ink)] md:text-5xl">
            Revenue expansion model
          </h1>
          <p className="mt-2 max-w-2xl text-[var(--ink-soft)]">
            Bookkeeping retainers + AI lead capture for Oxford-area real estate pros, property
            managers, and contractors — MRR, unit economics, forecast, and pipeline.
          </p>
        </div>
        <label className="text-sm text-[var(--ink-soft)]">
          Forecast scenario
          <select
            className="mt-1 block w-full rounded-xl border border-[var(--line)] bg-white px-3 py-2 font-medium text-[var(--ink)] md:w-48"
            value={scenario}
            onChange={(e) => {
              const v = e.target.value as ScenarioKey;
              startTransition(() => setScenario(v));
            }}
          >
            <option value="conservative">Conservative</option>
            <option value="base">Base</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </label>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="MRR"
          value={formatMoney(model.mrr)}
          hint="Active recurring only — setup excluded"
        />
        <MetricCard
          label="ARR (run-rate)"
          value={formatMoney(model.arr)}
          hint="MRR × 12 — not trailing revenue"
        />
        <MetricCard
          label="Active paying customers"
          value={String(model.activeCustomers)}
          hint={`ARPA ${formatMoney(model.arpa)}`}
        />
        <MetricCard
          label="Gross margin"
          value={formatPercent(model.grossMargin)}
          hint={`GP ${formatMoney(model.grossProfit)} on recurring+usage`}
        />
        <MetricCard
          label="Operating profit"
          value={formatMoney(model.operatingProfit)}
          hint={`OpEx ${formatMoney(model.operatingExpenses)} / mo`}
          warn={model.operatingProfit < 0}
        />
        <MetricCard
          label="Collected cash (MTD fields)"
          value={formatMoney(model.collectedCashMtd)}
          hint="From customer payment fields"
        />
        <MetricCard
          label="CAC (illustrative)"
          value={formatMoney(model.cac)}
          hint={`Payback ${formatMonths(model.cacPayback)}`}
        />
        <MetricCard
          label="LTV estimate"
          value={formatMoney(model.ltv)}
          hint="Early-stage; uses logo churn or funnel assumption"
        />
        <MetricCard
          label="Logo churn (Sep)"
          value={formatPercent(model.logoChurn)}
          hint="Customers lost / start-of-period actives"
        />
        <MetricCard
          label="NRR (Sep)"
          value={formatPercent(model.nrr)}
          hint="Early-stage estimate"
        />
        <MetricCard
          label="Break-even revenue"
          value={formatMoney(model.breakEven)}
          hint="Covers fixed OpEx + variable cost rate"
        />
        <MetricCard
          label="Cash runway"
          value={
            model.runway == null
              ? model.operatingProfit >= 0
                ? "Not burning"
                : "Unavailable"
              : formatMonths(model.runway)
          }
          hint={`Cash ${formatMoney(model.cash.operatingCash)} (${model.cash.provenance})`}
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
          <h2 className="font-[family-name:var(--font-display)] text-2xl">MRR by tier</h2>
          <p className="mb-3 text-sm text-[var(--ink-soft)]">Recurring only</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={model.mrrByTier}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(11,31,42,0.08)" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(v) => `$${v}`} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => formatMoney(v)} />
                <Bar dataKey="mrr" fill="#0d8a6a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
          <h2 className="font-[family-name:var(--font-display)] text-2xl">
            12-mo forecast ({scenario})
          </h2>
          <p className="mb-3 text-sm text-[var(--ink-soft)]">
            Driver-based: leads × conversion × churn — not arbitrary growth %
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecastChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(11,31,42,0.08)" />
                <XAxis dataKey="label" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="MRR" stroke="#0d8a6a" fill="#0d8a6a33" />
                <Area type="monotone" dataKey="Setup" stroke="#1f6f8b" fill="#1f6f8b22" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
        <h2 className="font-[family-name:var(--font-display)] text-2xl">
          Scenario comparison — ending MRR
        </h2>
        <p className="mb-3 text-sm text-[var(--ink-soft)]">
          Conservative / Base / Aggressive use different funnel assumptions (see Assumptions).
        </p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={scenarioCompare}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(11,31,42,0.08)" />
              <XAxis dataKey="label" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="Conservative" stroke="#45617a" fill="#45617a22" />
              <Area type="monotone" dataKey="Base" stroke="#0d8a6a" fill="#0d8a6a33" />
              <Area type="monotone" dataKey="Aggressive" stroke="#d97706" fill="#d9770622" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </article>

      <PricingTable model={model} />
      <ContributionTable model={model} />
      <PipelineTable model={model} />
      <ForecastTable model={model} />
      <AssumptionsPanel model={initial} scenario={scenario} />
    </div>
  );
}

function PricingTable({ model }: { model: AgencyModel }) {
  return (
    <section className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
      <h2 className="font-[family-name:var(--font-display)] text-2xl">Pricing & unit economics</h2>
      <p className="mt-1 mb-4 text-sm text-[var(--ink-soft)]">
        Grand Slam tiers: Foundation, Velocity Suite, Enterprise Alpha. AI Lead Capture stacks at
        $499–$999 setup + $99–$149/mo. Costs are planning assumptions — verify against QBO and
        invoices.
      </p>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-[var(--muted)]">
              <th className="px-2 py-2">Tier</th>
              <th className="px-2 py-2">Setup</th>
              <th className="px-2 py-2">MRR</th>
              <th className="px-2 py-2">Incl. mins</th>
              <th className="px-2 py-2">Direct cost</th>
              <th className="px-2 py-2">GP / mo</th>
              <th className="px-2 py-2">Margin</th>
              <th className="px-2 py-2">Min price @ target</th>
              <th className="px-2 py-2">Unprofitable &gt; mins</th>
            </tr>
          </thead>
          <tbody>
            {model.tierEconomics.map((t) => (
              <tr key={t.tier.id} className="border-b border-[var(--line)]/70">
                <td className="px-2 py-2.5 font-medium">{t.tier.name}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(t.setupFee)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(t.monthlyRecurring)}</td>
                <td className="px-2 py-2.5 tabular-nums">{t.tier.includedVoiceMinutes}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(t.directMonthlyCost)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(t.grossProfitMonthly)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatPercent(t.grossMargin)}</td>
                <td className="px-2 py-2.5 tabular-nums">
                  {formatMoney(t.minPriceForTargetMargin)}
                </td>
                <td className="px-2 py-2.5 tabular-nums">
                  {t.unprofitableAtMinutes ?? "n/a"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ContributionTable({ model }: { model: AgencyModel }) {
  return (
    <section className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
      <h2 className="font-[family-name:var(--font-display)] text-2xl">
        Cost to serve / contribution
      </h2>
      <p className="mt-1 mb-4 text-sm text-[var(--ink-soft)]">
        Direct delivery costs only (voice, hosting, phone, support labor, processing, allocated
        CRM). Shared OpEx excluded.
      </p>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-[var(--muted)]">
              <th className="px-2 py-2">Customer</th>
              <th className="px-2 py-2">Tier</th>
              <th className="px-2 py-2">Mins</th>
              <th className="px-2 py-2">Revenue</th>
              <th className="px-2 py-2">Direct cost</th>
              <th className="px-2 py-2">Contribution</th>
              <th className="px-2 py-2">Margin</th>
            </tr>
          </thead>
          <tbody>
            {model.customerContributions.map((c) => (
              <tr
                key={c.id}
                className={`border-b border-[var(--line)]/70 ${
                  c.unprofitableFlag ? "bg-red-50/80" : ""
                }`}
              >
                <td className="px-2 py-2.5 font-medium">{c.name}</td>
                <td className="px-2 py-2.5">{c.tierId}</td>
                <td className="px-2 py-2.5 tabular-nums">{c.minutes}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(c.revenue)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(c.directCost)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(c.contribution)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatPercent(c.margin)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PipelineTable({ model }: { model: AgencyModel }) {
  return (
    <section className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
      <h2 className="font-[family-name:var(--font-display)] text-2xl">CRM pipeline</h2>
      <p className="mt-1 mb-4 text-sm text-[var(--ink-soft)]">
        Pipeline is not booked revenue. Open pipeline MRR {formatMoney(model.pipelineMrr)} ·
        weighted contract value (setup + 12×MRR) {formatMoney(model.pipelineValue)}. Won deals
        become customers only after activation rules.
      </p>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-[var(--muted)]">
              <th className="px-2 py-2">Opportunity</th>
              <th className="px-2 py-2">Stage</th>
              <th className="px-2 py-2">Tier</th>
              <th className="px-2 py-2">Setup</th>
              <th className="px-2 py-2">MRR</th>
              <th className="px-2 py-2">Source</th>
            </tr>
          </thead>
          <tbody>
            {model.opportunities.map((o) => (
              <tr key={o.id} className="border-b border-[var(--line)]/70">
                <td className="px-2 py-2.5 font-medium">{o.name}</td>
                <td className="px-2 py-2.5">{o.stage}</td>
                <td className="px-2 py-2.5">{o.tierId}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(o.expectedSetup)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(o.expectedMrr)}</td>
                <td className="px-2 py-2.5">{o.leadSource}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ForecastTable({ model }: { model: AgencyModel }) {
  return (
    <section className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
      <h2 className="font-[family-name:var(--font-display)] text-2xl">
        Forecast detail ({model.scenario})
      </h2>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-[var(--muted)]">
              <th className="px-2 py-2">Month</th>
              <th className="px-2 py-2">New logos</th>
              <th className="px-2 py-2">Ending customers</th>
              <th className="px-2 py-2">Ending MRR</th>
              <th className="px-2 py-2">Setup</th>
              <th className="px-2 py-2">Op. profit</th>
              <th className="px-2 py-2">Cum. cash</th>
            </tr>
          </thead>
          <tbody>
            {model.forecast.map((r) => (
              <tr key={r.monthIndex} className="border-b border-[var(--line)]/70">
                <td className="px-2 py-2.5">{r.label}</td>
                <td className="px-2 py-2.5 tabular-nums">{r.newCustomers.toFixed(1)}</td>
                <td className="px-2 py-2.5 tabular-nums">{r.endingCustomers.toFixed(1)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(r.endingMrr)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(r.setupRevenue)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(r.operatingProfit)}</td>
                <td className="px-2 py-2.5 tabular-nums">{formatMoney(r.cumulativeCash)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AssumptionsPanel({
  model,
  scenario,
}: {
  model: AgencyModel;
  scenario: ScenarioKey;
}) {
  const f = model.assumptions.funnel[scenario];
  return (
    <section className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm backdrop-blur">
      <h2 className="font-[family-name:var(--font-display)] text-2xl">Visible assumptions</h2>
      <p className="mt-1 mb-4 text-sm text-[var(--ink-soft)]">
        Edit in <code className="rounded bg-black/5 px-1">src/data/assumptions.ts</code>. Full
        formula docs: <code className="rounded bg-black/5 px-1">docs/FORMULAS.md</code>.
      </p>
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 text-sm">
        <Assum label="Monthly leads" value={String(f.monthlyLeads)} />
        <Assum label="Lead → appointment" value={formatPercent(f.leadToAppointmentRate)} />
        <Assum label="Show rate" value={formatPercent(f.appointmentShowRate)} />
        <Assum label="Show → close" value={formatPercent(f.showToCloseRate)} />
        <Assum label="Logo churn / mo" value={formatPercent(f.monthlyLogoChurnRate)} />
        <Assum label="Expansion / mo" value={formatPercent(f.monthlyExpansionRate)} />
        <Assum
          label="Voice $/min (infra)"
          value={formatMoney(model.assumptions.unitCosts.voiceCostPerMinute, 2)}
        />
        <Assum
          label="Target gross margin"
          value={formatPercent(model.assumptions.targetGrossMargin)}
        />
        <Assum label="Currency" value={model.assumptions.currency} />
      </div>
      <ul className="mt-4 list-disc space-y-1 pl-5 text-xs text-[var(--ink-soft)]">
        {model.recognitionNotes.map((n) => (
          <li key={n}>{n}</li>
        ))}
      </ul>
    </section>
  );
}

function Assum({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[var(--line)] bg-white/50 px-3 py-2">
      <p className="text-[11px] uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className="mt-1 font-medium tabular-nums">{value}</p>
    </div>
  );
}
