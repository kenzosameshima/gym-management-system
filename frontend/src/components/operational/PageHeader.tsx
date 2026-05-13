import type React from "react";

interface PageHeaderProps {
  title: string;
  eyebrow?: string;
  description?: string;
  actions?: React.ReactNode;
  meta?: React.ReactNode;
}

export function PageHeader({
  title,
  eyebrow,
  description,
  actions,
  meta
}: PageHeaderProps): JSX.Element {
  return (
    <header className="page-header operational-page-header">
      <div className="page-heading">
        {eyebrow !== undefined && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {description !== undefined && <p className="page-description">{description}</p>}
        {meta !== undefined && <div className="page-meta">{meta}</div>}
      </div>
      {actions !== undefined && <div className="page-actions">{actions}</div>}
    </header>
  );
}
