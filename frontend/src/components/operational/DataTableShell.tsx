import type React from "react";
import { EmptyState } from "../EmptyState";
import { ErrorState } from "../ErrorState";
import { LoadingState } from "../LoadingState";

interface DataTableShellProps {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  isLoading?: boolean;
  error?: string | null;
  isEmpty?: boolean;
  emptyMessage?: string;
}

export function DataTableShell({
  title,
  description,
  actions,
  children,
  isLoading = false,
  error = null,
  isEmpty = false,
  emptyMessage = "Nenhum registro encontrado."
}: DataTableShellProps): JSX.Element {
  return (
    <section className="data-table-shell">
      {(title !== undefined || description !== undefined || actions !== undefined) && (
        <header className="section-header">
          <div>
            {title !== undefined && <h2>{title}</h2>}
            {description !== undefined && <p>{description}</p>}
          </div>
          {actions !== undefined && <div className="section-actions">{actions}</div>}
        </header>
      )}
      {error !== null ? <ErrorState message={error} /> : null}
      {isLoading ? <LoadingState /> : isEmpty ? <EmptyState message={emptyMessage} /> : children}
    </section>
  );
}
