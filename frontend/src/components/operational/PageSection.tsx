import type React from "react";

interface PageSectionProps {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  variant?: "plain" | "panel";
}

export function PageSection({
  title,
  description,
  actions,
  children,
  variant = "plain"
}: PageSectionProps): JSX.Element {
  return (
    <section className={variant === "panel" ? "panel page-section" : "page-section"}>
      {(title !== undefined || description !== undefined || actions !== undefined) && (
        <header className="section-header">
          <div>
            {title !== undefined && <h2>{title}</h2>}
            {description !== undefined && <p>{description}</p>}
          </div>
          {actions !== undefined && <div className="section-actions">{actions}</div>}
        </header>
      )}
      <div className="page-section-body">{children}</div>
    </section>
  );
}
