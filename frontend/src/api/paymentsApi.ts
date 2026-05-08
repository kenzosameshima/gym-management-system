import { httpClient } from "./httpClient";
import type { Page } from "../types/common";
import type { Payment, PaymentCreatePayload, PaymentQueryParams, PaymentUpdatePayload } from "../types/payment";

const PAYMENT_ENDPOINTS = {
  base: "/api/payments",
  byId: (paymentId: number) => `/api/payments/${paymentId}`,
  pay: (paymentId: number) => `/api/payments/${paymentId}/pay`
} as const;

export async function getPayments(params: PaymentQueryParams = {}): Promise<Page<Payment>> {
  const response = await httpClient.get<Page<Payment>>(PAYMENT_ENDPOINTS.base, { params });
  return response.data;
}

export async function createPayment(payload: PaymentCreatePayload): Promise<Payment> {
  const response = await httpClient.post<Payment>(PAYMENT_ENDPOINTS.base, payload);
  return response.data;
}

export async function updatePayment(paymentId: number, payload: PaymentUpdatePayload): Promise<Payment> {
  const response = await httpClient.put<Payment>(PAYMENT_ENDPOINTS.byId(paymentId), payload);
  return response.data;
}

export async function markPaymentPaid(paymentId: number): Promise<Payment> {
  const response = await httpClient.patch<Payment>(PAYMENT_ENDPOINTS.pay(paymentId));
  return response.data;
}

