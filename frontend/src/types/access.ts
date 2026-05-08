export type AccessDeniedReason =
  | "STUDENT_NOT_FOUND"
  | "STUDENT_INACTIVE"
  | "NO_ACTIVE_ENROLLMENT"
  | "ENROLLMENT_EXPIRED"
  | "PAYMENT_OVERDUE";

export interface AccessCheckRequest {
  cpf: string;
}

export interface AccessDecision {
  student_id: number | null;
  cpf_attempted: string;
  allowed: boolean;
  reason: AccessDeniedReason | null;
}

