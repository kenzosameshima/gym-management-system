import type React from "react";

interface ContextPanelProps {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  tone?: "default" | "success" | "warning" | "danger";
}

export function ContextPanel({
  title,
  description,
  actions,
  children,
  tone = "default"
}: ContextPanelProps): JSX.Element {
  return (
    <section className={`panel context-panel context-panel-${tone}`}>
      {(title !== undefined || description !== undefined || actions !== undefined) && (
        <header className="section-header">
          <div>
            {title !== undefined && <h2>{title}</h2>}
            {description !== undefined && <p>{description}</p>}
          </div>
          {actions !== undefined && <div className="section-actions">{actions}</div>}
        </header>
      )}
      <div className="context-panel-body">{children}</div>
    </section>
  );
}
