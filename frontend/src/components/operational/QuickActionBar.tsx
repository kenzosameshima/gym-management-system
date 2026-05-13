import { Link } from "react-router-dom";
import type React from "react";

export interface QuickAction {
  to?: string;
  label: string;
  onClick?: () => void;
  primary?: boolean;
}

interface QuickActionBarProps {
  actions: QuickAction[];
  "aria-label"?: string;
}

export function QuickActionBar({
  actions,
  "aria-label": ariaLabel = "Ações rápidas"
}: QuickActionBarProps): JSX.Element {
  return (
    <nav className="quick-actions quick-action-bar" aria-label={ariaLabel}>
      {actions.map((action) => {
        const className = action.primary === true ? "quick-action-primary" : undefined;
        if (action.to !== undefined) {
          return (
            <Link key={`${action.label}-${action.to}`} to={action.to} className={className}>
              {action.label}
            </Link>
          );
        }

        return (
          <button
            key={action.label}
            type="button"
            className={action.primary === true ? undefined : "secondary"}
            onClick={action.onClick}
          >
            {action.label}
          </button>
        );
      })}
    </nav>
  );
}
