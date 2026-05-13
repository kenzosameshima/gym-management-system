import type React from "react";

interface FilterToolbarProps {
  children: React.ReactNode;
  onSubmit?: React.FormEventHandler<HTMLFormElement>;
  actions?: React.ReactNode;
  "aria-label"?: string;
}

export function FilterToolbar({
  children,
  onSubmit,
  actions,
  "aria-label": ariaLabel = "Filtros"
}: FilterToolbarProps): JSX.Element {
  return (
    <form className="toolbar filter-toolbar" aria-label={ariaLabel} onSubmit={onSubmit}>
      <div className="filter-fields">{children}</div>
      {actions !== undefined && <div className="filter-actions">{actions}</div>}
    </form>
  );
}
