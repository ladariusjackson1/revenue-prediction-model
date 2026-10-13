import { formatMoney, formatPercent } from "@/lib/utils";

export function MetricCard(props: {
  label: string;
  value: string;
  hint?: string;
  warn?: boolean;
}) {
  return (
    <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4 shadow-sm backdrop-blur">
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--muted)]">
        {props.label}
      </p>
      <p
        className={`mt-2 font-[family-name:var(--font-display)] text-2xl tracking-tight md:text-3xl ${
          props.warn ? "text-[var(--signal)]" : "text-[var(--ink)]"
        }`}
      >
        {props.value}
      </p>
      {props.hint ? (
        <p className="mt-1 text-xs text-[var(--ink-soft)]">{props.hint}</p>
      ) : null}
    </article>
  );
}

export function moneyOrUnavailable(n: number | null | undefined, digits = 0) {
  return formatMoney(n, digits);
}

export function pctOrUnavailable(n: number | null | undefined, digits = 1) {
  return formatPercent(n, digits);
}
