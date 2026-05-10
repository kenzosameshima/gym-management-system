import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { createStudent, deleteStudent, getStudents, updateStudent } from "../api/studentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useAuth } from "../contexts/AuthContext";
import { useSortableRows } from "../hooks/useSortableRows";
import type { Page } from "../types/common";
import type { Student, StudentPayload } from "../types/student";
import { formatDate, formatFinancialStatus, getErrorMessage, STATUS_OPTIONS } from "./pageUtils";

const EMPTY_FORM: StudentPayload = {
  name: "",
  cpf: "",
  birth_date: "",
  phone: "",
  email: "",
  address: "",
  status: "ACTIVE"
};

export function StudentsPage(): JSX.Element {
  const { user } = useAuth();
  const canWrite = user?.role === "ADMIN" || user?.role === "RECEPTIONIST";
  const [page, setPage] = useState<Page<Student> | null>(null);
  const [form, setForm] = useState<StudentPayload>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [nameSearch, setNameSearch] = useState("");
  const [cpfSearch, setCpfSearch] = useState("");
  const [emailSearch, setEmailSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"" | StudentPayload["status"]>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadStudents(offset = page?.offset ?? 0): Promise<void> {
    setIsLoading(true);
    setError(null);
    try {
      setPage(await getStudents({
        limit: 20,
        offset,
        name: nameSearch || undefined,
        cpf: cpfSearch || undefined,
        email: emailSearch || undefined,
        status: statusFilter || undefined
      }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadStudents(0);
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      if (editingId === null) {
        await createStudent(form);
      } else {
        await updateStudent(editingId, form);
      }
      setForm(EMPTY_FORM);
      setEditingId(null);
      toast.success(editingId === null ? "Student created." : "Student updated.");
      await loadStudents(0);
    } catch (submitError) {
      toast.error("Student save failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  function startEdit(student: Student): void {
    setEditingId(student.id);
    setForm({
      name: student.name,
      cpf: student.cpf,
      birth_date: student.birth_date,
      phone: student.phone,
      email: student.email,
      address: student.address,
      status: student.status
    });
  }

  async function handleDelete(studentId: number): Promise<void> {
    if (!confirm("Deactivate this student?")) {
      return;
    }
    await deleteStudent(studentId);
    toast.success("Student deactivated.");
    await loadStudents();
  }

  const columns: Column<Student>[] = [
    { key: "name", header: "Name", render: (student) => student.name, sortValue: (student) => student.name },
    { key: "cpf", header: "CPF", render: (student) => student.cpf, sortValue: (student) => student.cpf },
    { key: "email", header: "Email", render: (student) => student.email, sortValue: (student) => student.email },
    { key: "birth_date", header: "Birth date", render: (student) => formatDate(student.birth_date) },
    { key: "status", header: "Status", render: (student) => student.status },
    { key: "financial", header: "Financial status", render: (student) => formatFinancialStatus(student.financial_status) },
    {
      key: "actions",
      header: "Actions",
      render: (student) =>
        canWrite ? (
          <div className="row-actions">
            <button type="button" className="secondary" onClick={() => startEdit(student)}>
              Edit
            </button>
            <button type="button" className="danger" onClick={() => void handleDelete(student.id)}>
              Delete
            </button>
          </div>
        ) : (
          "Read only"
        )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);

  return (
    <section className="page-stack">
      <header className="page-header">
        <h1>Students</h1>
      </header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadStudents(0); }}>
        <label>Name<input placeholder="Name" value={nameSearch} onChange={(event) => setNameSearch(event.target.value)} /></label>
        <label>CPF<input placeholder="CPF" value={cpfSearch} onChange={(event) => setCpfSearch(event.target.value)} /></label>
        <label>Email<input placeholder="Email" value={emailSearch} onChange={(event) => setEmailSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "" | StudentPayload["status"])}>
          <option value="">All</option>
          {STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}
        </select></label>
        <button type="submit">Search</button>
      </form>
      {canWrite && (
        <form className="panel form-grid" onSubmit={handleSubmit}>
          <label>Name<input placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required /></label>
          <label>CPF<input placeholder="CPF" value={form.cpf} onChange={(event) => setForm({ ...form, cpf: event.target.value })} required /></label>
          <label>Birth date<input type="date" value={form.birth_date} onChange={(event) => setForm({ ...form, birth_date: event.target.value })} required /></label>
          <label>Phone<input placeholder="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} required /></label>
          <label>Email<input type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label>
          <label>Address<input placeholder="Address" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} required /></label>
          <label>Status
            <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as StudentPayload["status"] })}>
              {STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}
            </select>
          </label>
          <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : editingId === null ? "Create student" : "Update student"}</button>
        </form>
      )}
      {page === null ? <LoadingState /> : <DataTable columns={columns} rows={sorted.rows} getRowKey={(student) => student.id} emptyMessage="No students found." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadStudents(nextOffset)} sortKey={sorted.sortKey} sortDirection={sorted.sortDirection} onSortChange={sorted.setSortKey} />}
    </section>
  );
}
