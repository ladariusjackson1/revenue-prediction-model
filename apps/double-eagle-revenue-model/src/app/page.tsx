import { ExecutiveDashboard } from "@/components/executive-dashboard";
import { buildAgencyModel } from "@/lib/finance/model";

export default function Page() {
  const base = buildAgencyModel("base");
  const models = {
    conservative: buildAgencyModel("conservative"),
    base,
    aggressive: buildAgencyModel("aggressive"),
  };

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 md:px-8 md:py-10">
      <ExecutiveDashboard initial={base} models={models} />
      <footer className="mt-10 border-t border-[var(--line)] pt-4 text-xs text-[var(--muted)]">
        Double Eagle Financial LLC — playbook in docs/DOUBLE_EAGLE_PLAYBOOK.md · formulas in
        docs/FORMULAS.md · edit drivers in src/data/assumptions.ts
      </footer>
    </main>
  );
}
