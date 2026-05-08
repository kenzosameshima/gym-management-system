import { FormEvent, useEffect, useState } from "react";
import { createPayment, getPayments, markPaymentPaid, updatePayment } from "../api/paymentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import type { Page } from "../types/common";
import type { Payment, PaymentCreatePayload } from "../types/payment";
import { formatCurrency, formatDate, getErrorMessage } from "./pageUtils";

const PAYMENT_STATUSES = ["PENDING", "PAID", "OVERDUE"] as const;
const EMPTY_FORM: PaymentCreatePayload = { enrollment_id: 0, amount: "", due_date: "", status: "PENDING" };

export function PaymentsPage(): JSX.Element {
  const [page, setPage] = useState<Page<Payment> | null>(null);
  const [form, setForm] = useState<PaymentCreatePayload>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPayments(): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getPayments({ limit: 50, offset: 0 }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadPayments();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    try {
      await createPayment(form);
      setForm(EMPTY_FORM);
      await loadPayments();
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Payment>[] = [
    { key: "id", header: "ID", render: (payment) => payment.id },
    { key: "enrollment", header: "Enrollment", render: (payment) => payment.enrollment_id },
    { key: "amount", header: "Amount", render: (payment) => formatCurrency(payment.amount) },
    { key: "due", header: "Due", render: (payment) => formatDate(payment.due_date) },
    { key: "paid", header: "Paid", render: (payment) => formatDate(payment.payment_date) },
    { key: "status", header: "Status", render: (payment) => payment.status },
    {
      key: "actions",
      header: "Actions",
      render: (payment) => (
        <div className="row-actions">
          <button type="button" className="secondary" disabled={payment.status === "PAID"} onClick={() => void markPaymentPaid(payment.id).then(loadPayments)}>
            Mark paid
          </button>
          <button type="button" className="secondary" onClick={() => void updatePayment(payment.id, { status: "OVERDUE" }).then(loadPayments)}>
            Mark overdue
          </button>
        </div>
      )
    }
  ];

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Payments</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <input type="number" min="1" placeholder="Enrollment ID" value={form.enrollment_id || ""} onChange={(event) => setForm({ ...form, enrollment_id: Number(event.target.value) })} required />
        <input placeholder="Amount" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required />
        <input type="date" value={form.due_date} onChange={(event) => setForm({ ...form, due_date: event.target.value })} required />
        <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as PaymentCreatePayload["status"] })}>
          {PAYMENT_STATUSES.map((status) => <option key={status}>{status}</option>)}
        </select>
        <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : "Register payment"}</button>
      </form>
      {isLoading || page === null ? <LoadingState /> : <DataTable columns={columns} rows={page.items} getRowKey={(payment) => payment.id} emptyMessage="No payments found." />}
    </section>
  );
}

