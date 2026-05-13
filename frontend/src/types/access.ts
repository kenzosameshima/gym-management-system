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
  student_name: string | null;
  cpf_attempted: string;
  allowed: boolean;
  reason: AccessDeniedReason | null;
}

export interface AccessLog {
  id: number;
  student_id: number | null;
  cpf_attempted: string;
  accessed_at: string;
  allowed: boolean;
  reason: AccessDeniedReason | null;
}
