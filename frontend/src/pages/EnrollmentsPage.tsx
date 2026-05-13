import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { cancelEnrollment, createEnrollment, getEnrollments } from "../api/enrollmentsApi";
import { getPlans } from "../api/plansApi";
import { getStudents } from "../api/studentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useSortableRows } from "../hooks/useSortableRows";
import type { Page } from "../types/common";
import type { Enrollment, EnrollmentCreatePayload } from "../types/enrollment";
import type { Plan } from "../types/plan";
import type { Student } from "../types/student";
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
  const [students, setStudents] = useState<Student[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [showStudentEmail, setShowStudentEmail] = useState(false);
  const [studentSearch, setStudentSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
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

  async function loadFormOptions(): Promise<void> {
    setIsLoadingOptions(true);
    try {
      const [studentPage, planPage] = await Promise.all([
        getStudents({ limit: 100, status: "ACTIVE" }),
        getPlans({ limit: 100, status: "ACTIVE" })
      ]);
      setStudents(studentPage.items);
      setPlans(planPage.items);
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoadingOptions(false);
    }
  }

  useEffect(() => {
    void loadEnrollments();
    void loadFormOptions();
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
      toast.success("Matricula criada.");
      await loadEnrollments();
    } catch (submitError) {
      toast.error("Nao foi possivel criar a matricula.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Enrollment>[] = [
    { key: "id", header: "ID", render: (enrollment) => enrollment.id, sortValue: (enrollment) => enrollment.id },
    { key: "student", header: "Aluno", render: (enrollment) => students.find((student) => student.id === enrollment.student_id)?.name ?? `Aluno #${enrollment.student_id}` },
    { key: "plan", header: "Plano", render: (enrollment) => plans.find((plan) => plan.id === enrollment.plan_id)?.name ?? `Plano #${enrollment.plan_id}` },
    { key: "start", header: "Inicio", render: (enrollment) => formatDate(enrollment.start_date) },
    { key: "end", header: "Fim", render: (enrollment) => formatDate(enrollment.end_date) },
    { key: "status", header: "Status", render: (enrollment) => enrollment.status, sortValue: (enrollment) => enrollment.status },
    { key: "payment", header: "Pagamento", render: (enrollment) => enrollment.payment_status ?? "-" },
    {
      key: "actions",
      header: "Acoes",
      render: (enrollment) => (
        <button type="button" className="danger" onClick={() => { if (confirm("Cancelar esta matricula?")) void cancelEnrollment(enrollment.id).then(() => { toast.success("Matricula cancelada."); return loadEnrollments(); }); }}>
          Cancelar
        </button>
      )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Nova matricula</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadEnrollments(0); }}>
        <label>Buscar aluno<input placeholder="Nome, CPF ou e-mail" value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="">Todos</option>
          {ENROLLMENT_STATUSES.map((status) => <option key={status}>{status}</option>)}
        </select></label>
        <button type="submit">Filtrar</button>
      </form>
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <label>
          <span className="field-title-row">
            Aluno
            <span className="inline-check">
              <input type="checkbox" checked={showStudentEmail} onChange={(event) => setShowStudentEmail(event.target.checked)} />
              E-mail
            </span>
          </span>
          <select value={form.student_id || ""} onChange={(event) => setForm({ ...form, student_id: Number(event.target.value) })} required disabled={isLoadingOptions || students.length === 0}>
            <option value="">{isLoadingOptions ? "Carregando alunos..." : showStudentEmail ? "Selecionar por e-mail" : "Selecionar por nome"}</option>
            {students.map((student) => (
              <option key={student.id} value={student.id}>{showStudentEmail ? student.email : student.name}</option>
            ))}
          </select>
        </label>
        <label>Plano
          <select value={form.plan_id || ""} onChange={(event) => setForm({ ...form, plan_id: Number(event.target.value) })} required disabled={isLoadingOptions || plans.length === 0}>
            <option value="">{isLoadingOptions ? "Carregando planos..." : "Selecionar plano"}</option>
            {plans.map((plan) => (
              <option key={plan.id} value={plan.id}>{plan.name}</option>
            ))}
          </select>
        </label>
        <label>Inicio<input type="date" value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} required /></label>
        <label>Primeiro vencimento<input type="date" value={form.first_payment_due_date ?? ""} onChange={(event) => setForm({ ...form, first_payment_due_date: event.target.value })} /></label>
        <button type="submit" disabled={isSaving}>{isSaving ? "Salvando..." : "Criar matricula"}</button>
      </form>
      {page === null ? <LoadingState /> : <DataTable columns={columns} rows={sorted.rows} getRowKey={(enrollment) => enrollment.id} emptyMessage="Nenhuma matricula encontrada." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadEnrollments(nextOffset)} sortKey={sorted.sortKey} sortDirection={sorted.sortDirection} onSortChange={sorted.setSortKey} />}
    </section>
  );
}
