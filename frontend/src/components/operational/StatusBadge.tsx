import type React from "react";

type StatusTone = "neutral" | "success" | "warning" | "danger" | "info";

interface StatusBadgeProps {
  children: React.ReactNode;
  tone?: StatusTone;
}

const STATUS_TONE_BY_VALUE: Record<string, StatusTone> = {
  ACTIVE: "success",
  INACTIVE: "neutral",
  PAID: "success",
  PENDING: "warning",
  OVERDUE: "danger",
  CANCELLED: "neutral",
  EXPIRED: "danger",
  IN_GOOD_STANDING: "success",
  DEFAULTER: "danger",
  NO_ACTIVE_ENROLLMENT: "warning",
  Liberado: "success",
  Bloqueado: "danger"
};

export function StatusBadge({ children, tone }: StatusBadgeProps): JSX.Element {
  const value = typeof children === "string" ? children : "";
  const resolvedTone = tone ?? STATUS_TONE_BY_VALUE[value] ?? "neutral";

  return <span className={`status-badge status-badge-${resolvedTone}`}>{children}</span>;
}
