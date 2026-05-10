import type { PageQueryParams } from "./common";
import type { PaymentStatus } from "./payment";

export type EnrollmentStatus = "ACTIVE" | "EXPIRED" | "CANCELLED";

export interface Enrollment {
  id: number;
  student_id: number;
  plan_id: number;
  start_date: string;
  end_date: string;
  status: EnrollmentStatus;
  payment_status: PaymentStatus | null;
  created_at: string;
  updated_at: string;
}

export interface EnrollmentCreatePayload {
  student_id: number;
  plan_id: number;
  start_date: string;
  first_payment_due_date?: string | null;
}

export interface EnrollmentUpdatePayload {
  start_date?: string;
  end_date?: string;
  status?: EnrollmentStatus;
}

export interface EnrollmentQueryParams extends PageQueryParams {
  student_id?: number;
  plan_id?: number;
  status?: EnrollmentStatus;
  student_search?: string;
}
