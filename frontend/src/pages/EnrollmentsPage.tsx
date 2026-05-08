import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { cancelEnrollment, createEnrollment, getEnrollments } from "../api/enrollmentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useSortableRows } from "../hooks/useSortableRows";
import type { Page } from "../types/common";
import type { Enrollment, EnrollmentCreatePayload } from "../types/enrollment";
import { formatDate, getErrorMessage } from "./pageUtils";

const EMPTY_FORM: EnrollmentCreatePayload = {
  student_id: 0,
  plan_id: 0,
  start_date: "",
  first_payment_due_date: ""
};
const ENROLLMENT_STATUSES = ["ACTIVE", "EXPIRED", "CANCELLED"] as const;

export function EnrollmentsPage(): JSX.Element {
  const [page, setPage] = useState<Page<Enrollment> | null>(null);
  const [form, setForm] = useState<EnrollmentCreatePayload>(EMPTY_FORM);
  const [studentSearch, setStudentSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadEnrollments(offset = page?.offset ?? 0): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getEnrollments({ limit: 20, offset, student_search: studentSearch || undefined, status: statusFilter === "" ? undefined : statusFilter as Enrollment["status"] }));
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
      toast.success("Enrollment created.");
      await loadEnrollments();
    } catch (submitError) {
      toast.error("Enrollment save failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Enrollment>[] = [
    { key: "id", header: "ID", render: (enrollment) => enrollment.id, sortValue: (enrollment) => enrollment.id },
    { key: "student", header: "Student", render: (enrollment) => enrollment.student_id },
    { key: "plan", header: "Plan", render: (enrollment) => enrollment.plan_id },
    { key: "start", header: "Start", render: (enrollment) => formatDate(enrollment.start_date) },
    { key: "end", header: "End", render: (enrollment) => formatDate(enrollment.end_date) },
    { key: "status", header: "Status", render: (enrollment) => enrollment.status, sortValue: (enrollment) => enrollment.status },
    {
      key: "actions",
      header: "Actions",
      render: (enrollment) => (
        <button type="button" className="danger" onClick={() => { if (confirm("Cancel this enrollment?")) void cancelEnrollment(enrollment.id).then(() => { toast.success("Enrollment cancelled."); return loadEnrollments(); }); }}>
          Cancel
        </button>
      )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Enrollments</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadEnrollments(0); }}>
        <label>Student search<input placeholder="Name, CPF, or email" value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="">All</option>
          {ENROLLMENT_STATUSES.map((status) => <option key={status}>{status}</option>)}
        </select></label>
        <button type="submit">Filter</button>
      </form>
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <input type="number" min="1" placeholder="Student ID" value={form.student_id || ""} onChange={(event) => setForm({ ...form, student_id: Number(event.target.value) })} required />
        <input type="number" min="1" placeholder="Plan ID" value={form.plan_id || ""} onChange={(event) => setForm({ ...form, plan_id: Number(event.target.value) })} required />
        <input type="date" value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} required />
        <input type="date" value={form.first_payment_due_date ?? ""} onChange={(event) => setForm({ ...form, first_payment_due_date: event.target.value })} />
        <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : "Create enrollment"}</button>
      </form>
      {page === null ? <LoadingState /> : <DataTable columns={columns} rows={sorted.rows} getRowKey={(enrollment) => enrollment.id} emptyMessage="No enrollments found." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadEnrollments(nextOffset)} sortKey={sorted.sortKey} sortDirection={sorted.sortDirection} onSortChange={sorted.setSortKey} />}
    </section>
  );
}
