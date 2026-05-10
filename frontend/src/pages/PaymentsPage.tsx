import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getEnrollments } from "../api/enrollmentsApi";
import { createPayment, getPayments, markPaymentPaid, updatePayment } from "../api/paymentsApi";
import { getPlans } from "../api/plansApi";
import { getStudents } from "../api/studentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useSortableRows } from "../hooks/useSortableRows";
import type { Page } from "../types/common";
import type { Enrollment } from "../types/enrollment";
import type { Payment, PaymentCreatePayload } from "../types/payment";
import type { Plan } from "../types/plan";
import type { Student } from "../types/student";
import { formatCurrency, formatDate, getErrorMessage } from "./pageUtils";

const PAYMENT_STATUSES = ["PENDING", "PAID", "OVERDUE"] as const;
const EMPTY_FORM: PaymentCreatePayload = { enrollment_id: 0, amount: "", due_date: "", status: "PENDING" };

export function PaymentsPage(): JSX.Element {
  const [page, setPage] = useState<Page<Payment> | null>(null);
  const [form, setForm] = useState<PaymentCreatePayload>(EMPTY_FORM);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [activeEnrollments, setActiveEnrollments] = useState<Enrollment[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [studentSearch, setStudentSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPayments(offset = page?.offset ?? 0): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getPayments({
        limit: 20,
        offset,
        student_search: studentSearch || undefined,
        status: overdueOnly ? "OVERDUE" : statusFilter === "" ? undefined : statusFilter as Payment["status"]
      }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadPaymentOptions(): Promise<void> {
    setIsLoadingOptions(true);
    try {
      const [enrollmentPage, activeEnrollmentPage, studentPage, planPage] = await Promise.all([
        getEnrollments({ limit: 100 }),
        getEnrollments({ limit: 100, status: "ACTIVE" }),
        getStudents({ limit: 100 }),
        getPlans({ limit: 100 })
      ]);
      setEnrollments(enrollmentPage.items);
      setActiveEnrollments(activeEnrollmentPage.items);
      setStudents(studentPage.items);
      setPlans(planPage.items);
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoadingOptions(false);
    }
  }

  useEffect(() => {
    void loadPayments();
    void loadPaymentOptions();
  }, []);

  function enrollmentLabel(enrollmentId: number): string {
    const enrollment = enrollments.find((item) => item.id === enrollmentId);
    if (enrollment === undefined) {
      return `Enrollment #${enrollmentId}`;
    }
    const student = students.find((item) => item.id === enrollment.student_id);
    const plan = plans.find((item) => item.id === enrollment.plan_id);
    return `${student?.name ?? `Student #${enrollment.student_id}`} - ${plan?.name ?? `Plan #${enrollment.plan_id}`} (${enrollment.status}, ${formatDate(enrollment.start_date)})`;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    try {
      await createPayment(form);
      setForm(EMPTY_FORM);
      toast.success("Payment registered.");
      await loadPayments();
    } catch (submitError) {
      toast.error("Payment save failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Payment>[] = [
    { key: "id", header: "ID", render: (payment) => payment.id, sortValue: (payment) => payment.id },
    { key: "enrollment", header: "Enrollment", render: (payment) => enrollmentLabel(payment.enrollment_id) },
    { key: "amount", header: "Amount", render: (payment) => formatCurrency(payment.amount), sortValue: (payment) => Number(payment.amount) },
    { key: "due", header: "Due", render: (payment) => formatDate(payment.due_date) },
    { key: "paid", header: "Paid", render: (payment) => formatDate(payment.payment_date) },
    { key: "status", header: "Status", render: (payment) => payment.status },
    {
      key: "actions",
      header: "Actions",
      render: (payment) => (
        <div className="row-actions">
          <button type="button" className="secondary" disabled={payment.status === "PAID"} onClick={() => void markPaymentPaid(payment.id).then(() => { toast.success("Payment marked paid."); return loadPayments(); })}>
            Mark paid
          </button>
          <button type="button" className="secondary" onClick={() => void updatePayment(payment.id, { status: "OVERDUE" }).then(() => { toast.success("Payment marked overdue."); return loadPayments(); })}>
            Mark overdue
          </button>
        </div>
      )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Payments</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadPayments(0); }}>
        <label>Student search<input placeholder="Name, CPF, or email" value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} disabled={overdueOnly} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="">All</option>
          {PAYMENT_STATUSES.map((status) => <option key={status}>{status}</option>)}
        </select></label>
        <label className="inline-check"><input type="checkbox" checked={overdueOnly} onChange={(event) => setOverdueOnly(event.target.checked)} /> Overdue only</label>
        <button type="submit">Filter</button>
      </form>
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <label>Enrollment
          <select value={form.enrollment_id || ""} onChange={(event) => setForm({ ...form, enrollment_id: Number(event.target.value) })} required disabled={isLoadingOptions || activeEnrollments.length === 0}>
            <option value="">{isLoadingOptions ? "Loading enrollments..." : "Select by student name"}</option>
            {activeEnrollments.map((enrollment) => <option key={enrollment.id} value={enrollment.id}>{enrollmentLabel(enrollment.id)}</option>)}
          </select>
        </label>
        <label>Amount<input placeholder="Amount" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required /></label>
        <label>Due date<input type="date" value={form.due_date} onChange={(event) => setForm({ ...form, due_date: event.target.value })} required /></label>
        <label>Status
          <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as PaymentCreatePayload["status"] })}>
            {PAYMENT_STATUSES.map((status) => <option key={status}>{status}</option>)}
          </select>
        </label>
        <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : "Register payment"}</button>
      </form>
      {page === null ? <LoadingState /> : <DataTable columns={columns} rows={sorted.rows} getRowKey={(payment) => payment.id} emptyMessage="No payments found." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadPayments(nextOffset)} sortKey={sorted.sortKey} sortDirection={sorted.sortDirection} onSortChange={sorted.setSortKey} />}
    </section>
  );
}
