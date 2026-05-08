import { FormEvent, useEffect, useState } from "react";
import { cancelEnrollment, createEnrollment, getEnrollments } from "../api/enrollmentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import type { Page } from "../types/common";
import type { Enrollment, EnrollmentCreatePayload } from "../types/enrollment";
import { formatDate, getErrorMessage } from "./pageUtils";

const EMPTY_FORM: EnrollmentCreatePayload = {
  student_id: 0,
  plan_id: 0,
  start_date: "",
  first_payment_due_date: ""
};

export function EnrollmentsPage(): JSX.Element {
  const [page, setPage] = useState<Page<Enrollment> | null>(null);
  const [form, setForm] = useState<EnrollmentCreatePayload>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadEnrollments(): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getEnrollments({ limit: 50, offset: 0 }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadEnrollments();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    try {
      await createEnrollment({
        ...form,
        first_payment_due_date: form.first_payment_due_date || null
      });
      setForm(EMPTY_FORM);
      await loadEnrollments();
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Enrollment>[] = [
    { key: "id", header: "ID", render: (enrollment) => enrollment.id },
    { key: "student", header: "Student", render: (enrollment) => enrollment.student_id },
    { key: "plan", header: "Plan", render: (enrollment) => enrollment.plan_id },
    { key: "start", header: "Start", render: (enrollment) => formatDate(enrollment.start_date) },
    { key: "end", header: "End", render: (enrollment) => formatDate(enrollment.end_date) },
    { key: "status", header: "Status", render: (enrollment) => enrollment.status },
    {
      key: "actions",
      header: "Actions",
      render: (enrollment) => (
        <button type="button" className="danger" onClick={() => { if (confirm("Cancel this enrollment?")) void cancelEnrollment(enrollment.id).then(loadEnrollments); }}>
          Cancel
        </button>
      )
    }
  ];

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Enrollments</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <input type="number" min="1" placeholder="Student ID" value={form.student_id || ""} onChange={(event) => setForm({ ...form, student_id: Number(event.target.value) })} required />
        <input type="number" min="1" placeholder="Plan ID" value={form.plan_id || ""} onChange={(event) => setForm({ ...form, plan_id: Number(event.target.value) })} required />
        <input type="date" value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} required />
        <input type="date" value={form.first_payment_due_date ?? ""} onChange={(event) => setForm({ ...form, first_payment_due_date: event.target.value })} />
        <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : "Create enrollment"}</button>
      </form>
      {isLoading || page === null ? <LoadingState /> : <DataTable columns={columns} rows={page.items} getRowKey={(enrollment) => enrollment.id} emptyMessage="No enrollments found." />}
    </section>
  );
}

