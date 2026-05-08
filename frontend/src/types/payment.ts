import type { PageQueryParams } from "./common";

export type PaymentStatus = "PENDING" | "PAID" | "OVERDUE";

export interface Payment {
  id: number;
  enrollment_id: number;
  amount: string;
  due_date: string;
  payment_date: string | null;
  status: PaymentStatus;
  created_at: string;
}

export interface PaymentCreatePayload {
  enrollment_id: number;
  amount: string;
  due_date: string;
  status: PaymentStatus;
}

export interface PaymentUpdatePayload {
  amount?: string;
  due_date?: string;
  payment_date?: string | null;
  status?: PaymentStatus;
}

export interface PaymentQueryParams extends PageQueryParams {
  enrollment_id?: number;
  status?: PaymentStatus;
}

