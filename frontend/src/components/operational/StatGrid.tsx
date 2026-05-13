import type React from "react";

interface StatGridProps {
  children: React.ReactNode;
  "aria-label"?: string;
}

export function StatGrid({
  children,
  "aria-label": ariaLabel = "Indicadores"
}: StatGridProps): JSX.Element {
  return (
    <section className="stats-grid stat-grid" aria-label={ariaLabel}>
      {children}
    </section>
  );
}
