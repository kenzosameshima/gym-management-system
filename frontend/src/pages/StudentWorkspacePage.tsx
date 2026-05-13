import { FormEvent, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { useSearchParams } from "react-router-dom";
import { checkAccess, getAccessLogs } from "../api/accessApi";
import { getEnrollments } from "../api/enrollmentsApi";
import { getPayments, markPaymentPaid } from "../api/paymentsApi";
import { getPlans } from "../api/plansApi";
import { createStudent, deleteStudent, getStudents, updateStudent } from "../api/studentsApi";
import { getWorkoutPlans } from "../api/workoutsApi";
import { DataTable, type Column } from "../components/DataTable";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import {
  ContextPanel,
  DataTableShell,
  FilterToolbar,
  PageHeader,
  PageSection,
  QuickActionBar,
  SlideOverDrawer,
  StatusBadge
} from "../components/operational";
import { StatCard } from "../components/StatCard";
import { useAuth } from "../contexts/AuthContext";
import { useSortableRows } from "../hooks/useSortableRows";
import type { AccessDecision, AccessLog } from "../types/access";
import type { Page } from "../types/common";
import type { Enrollment } from "../types/enrollment";
import type { Payment } from "../types/payment";
import type { Plan } from "../types/plan";
import type { Student, StudentPayload } from "../types/student";
import type { WorkoutPlan } from "../types/workout";
import {
  formatCurrency,
  formatDate,
  formatDateTime,
  formatFinancialStatus,
  getErrorMessage,
  STATUS_OPTIONS
} from "./pageUtils";

const EMPTY_FORM: StudentPayload = {
  name: "",
  cpf: "",
  birth_date: "",
  phone: "",
  email: "",
  address: "",
  status: "ACTIVE"
};

type StudentWorkspaceTab = "overview" | "membership" | "payments" | "workouts" | "access";

const WORKSPACE_TABS: { key: StudentWorkspaceTab; label: string }[] = [
  { key: "overview", label: "Resumo" },
  { key: "membership", label: "Matrícula" },
  { key: "payments", label: "Pagamentos" },
  { key: "workouts", label: "Treinos" },
  { key: "access", label: "Acessos" }
];

interface StudentWorkspaceData {
  enrollments: Enrollment[];
  payments: Payment[];
  plans: Plan[];
  workoutPlans: WorkoutPlan[];
  accessLogs: AccessLog[];
  accessDecision: AccessDecision | null;
}

const EMPTY_WORKSPACE_DATA: StudentWorkspaceData = {
  enrollments: [],
  payments: [],
  plans: [],
  workoutPlans: [],
  accessLogs: [],
  accessDecision: null
};

function paymentTone(status: Payment["status"]): "success" | "warning" | "danger" {
  if (status === "PAID") {
    return "success";
  }
  return status === "OVERDUE" ? "danger" : "warning";
}

function studentTone(student: Student): "success" | "warning" | "danger" | "neutral" {
  if (student.status === "INACTIVE") {
    return "neutral";
  }
  if (student.financial_status === "DEFAULTER") {
    return "danger";
  }
  if (student.financial_status === "NO_ACTIVE_ENROLLMENT") {
    return "warning";
  }
  return "success";
}

function accessReasonLabel(reason: AccessDecision["reason"]): string {
  const labels: Record<NonNullable<AccessDecision["reason"]>, string> = {
    STUDENT_NOT_FOUND: "Aluno não encontrado",
    STUDENT_INACTIVE: "Aluno inativo",
    NO_ACTIVE_ENROLLMENT: "Sem matrícula ativa",
    ENROLLMENT_EXPIRED: "Matrícula expirada",
    PAYMENT_OVERDUE: "Pagamento vencido"
  };
  return reason === null ? "Entrada liberada" : labels[reason];
}

export function StudentWorkspacePage(): JSX.Element {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const canManageStudents = user?.role === "ADMIN" || user?.role === "RECEPTIONIST";
  const canViewWorkoutContext = user?.role === "ADMIN" || user?.role === "INSTRUCTOR";
  const visibleWorkspaceTabs = useMemo(
    () => WORKSPACE_TABS.filter((tab) => {
      if (tab.key === "workouts") {
        return canViewWorkoutContext;
      }
      if (tab.key === "membership" || tab.key === "payments" || tab.key === "access") {
        return canManageStudents;
      }
      return true;
    }),
    [canManageStudents, canViewWorkoutContext]
  );
  const [page, setPage] = useState<Page<Student> | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [workspaceData, setWorkspaceData] = useState<StudentWorkspaceData>(EMPTY_WORKSPACE_DATA);
  const [workspaceTab, setWorkspaceTab] = useState<StudentWorkspaceTab>("overview");
  const [isWorkspaceLoading, setIsWorkspaceLoading] = useState(false);
  const [workspaceError, setWorkspaceError] = useState<string | null>(null);
  const [form, setForm] = useState<StudentPayload>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [nameSearch, setNameSearch] = useState(searchParams.get("search") ?? "");
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
      const nextPage = await getStudents({
        limit: 20,
        offset,
        name: nameSearch || undefined,
        cpf: cpfSearch || undefined,
        email: emailSearch || undefined,
        status: statusFilter || undefined
      });
      setPage(nextPage);
      setSelectedStudent((current) => {
        if (current === null) {
          return nextPage.items[0] ?? null;
        }
        return nextPage.items.find((student) => student.id === current.id) ?? current;
      });
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadWorkspace(student: Student): Promise<void> {
    setIsWorkspaceLoading(true);
    setWorkspaceError(null);
    try {
      if (!canManageStudents) {
        const workoutPlanPage = canViewWorkoutContext
          ? await getWorkoutPlans({ limit: 20, student_id: student.id })
          : { items: [] };
        setWorkspaceData({
          ...EMPTY_WORKSPACE_DATA,
          workoutPlans: workoutPlanPage.items
        });
        return;
      }

      const [enrollmentPage, paymentPage, planPage, workoutPlanPage, accessPage] = await Promise.all([
        getEnrollments({ limit: 20, student_id: student.id }),
        getPayments({ limit: 50, student_search: student.cpf }),
        getPlans({ limit: 100 }),
        canViewWorkoutContext ? getWorkoutPlans({ limit: 20, student_id: student.id }) : Promise.resolve({ items: [] }),
        getAccessLogs({ limit: 50 })
      ]);

      setWorkspaceData({
        enrollments: enrollmentPage.items,
        payments: paymentPage.items,
        plans: planPage.items,
        workoutPlans: workoutPlanPage.items,
        accessLogs: accessPage.items.filter(
          (log) => log.student_id === student.id || log.cpf_attempted === student.cpf
        ),
        accessDecision: null
      });
    } catch (loadError) {
      setWorkspaceError(getErrorMessage(loadError));
    } finally {
      setIsWorkspaceLoading(false);
    }
  }

  useEffect(() => {
    void loadStudents(0);
  }, [searchParams]);

  useEffect(() => {
    if (selectedStudent === null) {
      setWorkspaceData(EMPTY_WORKSPACE_DATA);
      return;
    }
    void loadWorkspace(selectedStudent);
  }, [selectedStudent?.id, canManageStudents, canViewWorkoutContext]);

  useEffect(() => {
    if (!visibleWorkspaceTabs.some((tab) => tab.key === workspaceTab)) {
      setWorkspaceTab("overview");
    }
  }, [visibleWorkspaceTabs, workspaceTab]);

  function openCreateDrawer(): void {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setIsDrawerOpen(true);
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
    setIsDrawerOpen(true);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      const savedStudent = editingId === null
        ? await createStudent(form)
        : await updateStudent(editingId, form);
      setForm(EMPTY_FORM);
      setEditingId(null);
      setIsDrawerOpen(false);
      setSelectedStudent(savedStudent);
      toast.success(editingId === null ? "Aluno cadastrado." : "Aluno atualizado.");
      await loadStudents(0);
    } catch (submitError) {
      toast.error("Não foi possível salvar o aluno.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(studentId: number): Promise<void> {
    if (!confirm("Desativar este aluno?")) {
      return;
    }
    await deleteStudent(studentId);
    toast.success("Aluno desativado.");
    if (selectedStudent?.id === studentId) {
      setSelectedStudent(null);
    }
    await loadStudents();
  }

  async function handleAccessCheck(student: Student): Promise<void> {
    setIsWorkspaceLoading(true);
    setWorkspaceError(null);
    try {
      const decision = await checkAccess({ cpf: student.cpf });
      setWorkspaceTab("access");
      toast.success(decision.allowed ? "Acesso liberado." : "Acesso bloqueado.");
      await loadWorkspace(student);
      setWorkspaceData((current) => ({ ...current, accessDecision: decision }));
    } catch (checkError) {
      toast.error("Não foi possível verificar o acesso.");
      setWorkspaceError(getErrorMessage(checkError));
    } finally {
      setIsWorkspaceLoading(false);
    }
  }

  async function handleMarkPaid(paymentId: number): Promise<void> {
    if (selectedStudent === null) {
      return;
    }
    try {
      await markPaymentPaid(paymentId);
      toast.success("Pagamento confirmado.");
      await loadWorkspace(selectedStudent);
    } catch (paymentError) {
      toast.error("Não foi possível confirmar o pagamento.");
      setWorkspaceError(getErrorMessage(paymentError));
    }
  }

  const columns: Column<Student>[] = [
    {
      key: "name",
      header: "Aluno",
      render: (student) => (
        <button type="button" className="table-link-button" onClick={() => setSelectedStudent(student)}>
          {student.name}
        </button>
      ),
      sortValue: (student) => student.name
    },
    { key: "cpf", header: "CPF", render: (student) => student.cpf, sortValue: (student) => student.cpf },
    { key: "email", header: "E-mail", render: (student) => student.email, sortValue: (student) => student.email },
    { key: "status", header: "Status", render: (student) => <StatusBadge>{formatFinancialStatus(student.status)}</StatusBadge> },
    {
      key: "financial",
      header: "Financeiro",
      render: (student) => (
        <StatusBadge tone={studentTone(student)}>{formatFinancialStatus(student.financial_status)}</StatusBadge>
      )
    },
    {
      key: "actions",
      header: "Ações",
      render: (student) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => setSelectedStudent(student)}>
            Abrir
          </button>
          {canManageStudents ? (
            <>
              <button type="button" className="secondary" onClick={() => startEdit(student)}>
                Editar
              </button>
              <button type="button" className="danger" onClick={() => void handleDelete(student.id)}>
                Desativar
              </button>
            </>
          ) : (
            <span>Somente leitura</span>
          )}
        </div>
      )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);

  const activeEnrollment = useMemo(
    () => workspaceData.enrollments.find((enrollment) => enrollment.status === "ACTIVE") ?? null,
    [workspaceData.enrollments]
  );
  const overduePayments = workspaceData.payments.filter((payment) => payment.status === "OVERDUE");
  const pendingPayments = workspaceData.payments.filter((payment) => payment.status === "PENDING");

  return (
    <section className="page-stack students-workspace-page">
      <PageHeader
        title="Atendimento do aluno"
        description="Busque, selecione e acompanhe o aluno sem perder o contexto operacional."
        actions={canManageStudents ? <button type="button" onClick={openCreateDrawer}>Cadastrar aluno</button> : undefined}
      />
      {error !== null && <ErrorState message={error} />}
      <div className="student-workspace-layout">
        <PageSection
          title="Lista de alunos"
          description="Use os filtros e mantenha o aluno selecionado aberto no painel lateral."
        >
          <div className="student-list-stack">
            <div className="student-filters-sticky">
              <FilterToolbar
                onSubmit={(event) => {
                  event.preventDefault();
                  void loadStudents(0);
                }}
                actions={<button type="submit">Buscar</button>}
              >
                <label>Nome<input placeholder="Nome" value={nameSearch} onChange={(event) => setNameSearch(event.target.value)} /></label>
                <label>CPF<input placeholder="CPF" value={cpfSearch} onChange={(event) => setCpfSearch(event.target.value)} /></label>
                <label>E-mail<input placeholder="E-mail" value={emailSearch} onChange={(event) => setEmailSearch(event.target.value)} /></label>
                <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "" | StudentPayload["status"])}>
                  <option value="">Todos</option>
                  {STATUS_OPTIONS.map((status) => <option key={status} value={status}>{formatFinancialStatus(status)}</option>)}
                </select></label>
              </FilterToolbar>
            </div>
            {page === null ? (
              <LoadingState />
            ) : (
              <DataTableShell>
                <DataTable
                  columns={columns}
                  rows={sorted.rows}
                  getRowKey={(student) => student.id}
                  emptyMessage="Nenhum aluno encontrado."
                  isLoading={isLoading}
                  total={page.total}
                  limit={page.limit}
                  offset={page.offset}
                  onPageChange={(nextOffset) => void loadStudents(nextOffset)}
                  sortKey={sorted.sortKey}
                  sortDirection={sorted.sortDirection}
                  onSortChange={sorted.setSortKey}
                />
              </DataTableShell>
            )}
          </div>
        </PageSection>

        <aside className="panel student-context-panel" aria-label="Área de trabalho do aluno">
          {selectedStudent === null ? (
            <EmptyState message="Selecione um aluno para abrir o contexto operacional." />
          ) : (
            <>
              <header className="student-context-header">
                <div>
                  <p className="eyebrow">Aluno selecionado</p>
                  <h2>{selectedStudent.name}</h2>
                  <p>{selectedStudent.cpf} · {selectedStudent.email}</p>
                </div>
                <StatusBadge tone={studentTone(selectedStudent)}>
                  {formatFinancialStatus(selectedStudent.financial_status)}
                </StatusBadge>
              </header>
              <QuickActionBar
                actions={[
                  ...(canManageStudents ? [
                    { label: "Editar", onClick: () => startEdit(selectedStudent) },
                    { label: "Verificar acesso", onClick: () => void handleAccessCheck(selectedStudent), primary: true }
                  ] : []),
                  { label: "Atualizar", onClick: () => void loadWorkspace(selectedStudent) }
                ]}
              />
              <div className="student-tabs" role="tablist" aria-label="Contexto do aluno">
                {visibleWorkspaceTabs.map((tab) => (
                  <button
                    key={tab.key}
                    type="button"
                    role="tab"
                    aria-selected={workspaceTab === tab.key}
                    className={workspaceTab === tab.key ? "student-tab active" : "student-tab secondary"}
                    onClick={() => setWorkspaceTab(tab.key)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              {workspaceError !== null && <ErrorState message={workspaceError} />}
              {isWorkspaceLoading ? <LoadingState message="Carregando contexto do aluno..." /> : (
                <StudentWorkspaceContent
                  tab={workspaceTab}
                  student={selectedStudent}
                  data={workspaceData}
                  activeEnrollment={activeEnrollment}
                  overduePayments={overduePayments}
                  pendingPayments={pendingPayments}
                  canViewManagementContext={canManageStudents}
                  canViewWorkoutContext={canViewWorkoutContext}
                  onMarkPaid={handleMarkPaid}
                />
              )}
            </>
          )}
        </aside>
      </div>

      <SlideOverDrawer
        isOpen={isDrawerOpen}
        title={editingId === null ? "Cadastrar aluno" : "Editar aluno"}
        description="Mantenha os dados operacionais do aluno atualizados."
        onClose={() => setIsDrawerOpen(false)}
      >
        <form className="form-grid student-drawer-form" onSubmit={handleSubmit}>
          <label>Nome<input placeholder="Nome" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required /></label>
          <label>CPF<input placeholder="CPF" value={form.cpf} onChange={(event) => setForm({ ...form, cpf: event.target.value })} required /></label>
          <label>Nascimento<input type="date" value={form.birth_date} onChange={(event) => setForm({ ...form, birth_date: event.target.value })} required /></label>
          <label>Telefone<input placeholder="Telefone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} required /></label>
          <label>E-mail<input type="email" placeholder="E-mail" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label>
          <label>Endereço<input placeholder="Endereço" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} required /></label>
          <label>Status
            <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as StudentPayload["status"] })}>
              {STATUS_OPTIONS.map((status) => <option key={status} value={status}>{formatFinancialStatus(status)}</option>)}
            </select>
          </label>
          <div className="drawer-form-actions">
            <button type="button" className="secondary" onClick={() => setIsDrawerOpen(false)}>Cancelar</button>
            <button type="submit" disabled={isSaving}>{isSaving ? "Salvando..." : editingId === null ? "Cadastrar aluno" : "Atualizar aluno"}</button>
          </div>
        </form>
      </SlideOverDrawer>
    </section>
  );
}

interface StudentWorkspaceContentProps {
  tab: StudentWorkspaceTab;
  student: Student;
  data: StudentWorkspaceData;
  activeEnrollment: Enrollment | null;
  overduePayments: Payment[];
  pendingPayments: Payment[];
  canViewManagementContext: boolean;
  canViewWorkoutContext: boolean;
  onMarkPaid: (paymentId: number) => Promise<void>;
}

function StudentWorkspaceContent({
  tab,
  student,
  data,
  activeEnrollment,
  overduePayments,
  pendingPayments,
  canViewManagementContext,
  canViewWorkoutContext,
  onMarkPaid
}: StudentWorkspaceContentProps): JSX.Element {
  if (!canViewManagementContext && tab !== "overview" && tab !== "workouts") {
    return <EmptyState message="Este contexto está disponível para administradores e recepção." />;
  }
  if (!canViewWorkoutContext && tab === "workouts") {
    return <EmptyState message="Este contexto está disponível para administradores e instrutores." />;
  }

  if (tab === "overview") {
    return (
      <div className="student-context-content">
        <div className="stats-grid student-context-stats">
          <StatCard label="Status" value={formatFinancialStatus(student.status)} />
          <StatCard label="Financeiro" value={formatFinancialStatus(student.financial_status)} />
          <StatCard label="Matrículas" value={canViewManagementContext ? data.enrollments.length : "-"} />
          <StatCard label="Fichas de treino" value={canViewWorkoutContext ? data.workoutPlans.length : "-"} />
        </div>
        <ContextPanel title="Dados de contato">
          <dl className="detail-list">
            <div><dt>Telefone</dt><dd>{student.phone}</dd></div>
            <div><dt>E-mail</dt><dd>{student.email}</dd></div>
            <div><dt>Endereço</dt><dd>{student.address}</dd></div>
            <div><dt>Nascimento</dt><dd>{formatDate(student.birth_date)}</dd></div>
          </dl>
        </ContextPanel>
        {canViewManagementContext && (
          <ContextPanel
            title="Situação operacional"
            tone={overduePayments.length > 0 ? "danger" : pendingPayments.length > 0 ? "warning" : "success"}
          >
            <dl className="detail-list">
              <div><dt>Matrícula ativa</dt><dd>{activeEnrollment === null ? "Não" : `Até ${formatDate(activeEnrollment.end_date)}`}</dd></div>
              <div><dt>Pagamentos vencidos</dt><dd>{overduePayments.length}</dd></div>
              <div><dt>Pagamentos pendentes</dt><dd>{pendingPayments.length}</dd></div>
            </dl>
          </ContextPanel>
        )}
      </div>
    );
  }

  if (tab === "membership") {
    const columns: Column<Enrollment>[] = [
      { key: "plan", header: "Plano", render: (enrollment) => data.plans.find((plan) => plan.id === enrollment.plan_id)?.name ?? "Plano não encontrado" },
      { key: "start", header: "Início", render: (enrollment) => formatDate(enrollment.start_date) },
      { key: "end", header: "Fim", render: (enrollment) => formatDate(enrollment.end_date) },
      { key: "status", header: "Status", render: (enrollment) => <StatusBadge>{formatFinancialStatus(enrollment.status)}</StatusBadge> },
      { key: "payment", header: "Pagamento", render: (enrollment) => enrollment.payment_status === null ? "-" : <StatusBadge tone={paymentTone(enrollment.payment_status)}>{formatFinancialStatus(enrollment.payment_status)}</StatusBadge> }
    ];
    return <DataTable columns={columns} rows={data.enrollments} getRowKey={(enrollment) => enrollment.id} emptyMessage="Nenhuma matrícula encontrada para este aluno." />;
  }

  if (tab === "payments") {
    const columns: Column<Payment>[] = [
      { key: "amount", header: "Valor", render: (payment) => formatCurrency(payment.amount) },
      { key: "due", header: "Vencimento", render: (payment) => formatDate(payment.due_date) },
      { key: "paid", header: "Pago em", render: (payment) => formatDate(payment.payment_date) },
      { key: "status", header: "Status", render: (payment) => <StatusBadge tone={paymentTone(payment.status)}>{formatFinancialStatus(payment.status)}</StatusBadge> },
      {
        key: "actions",
        header: "Ações",
        render: (payment) => payment.status === "PAID" ? "Confirmado" : (
          <button type="button" className="secondary" onClick={() => void onMarkPaid(payment.id)}>
            Confirmar
          </button>
        )
      }
    ];
    return <DataTable columns={columns} rows={data.payments} getRowKey={(payment) => payment.id} emptyMessage="Nenhuma mensalidade encontrada para este aluno." />;
  }

  if (tab === "workouts") {
    const columns: Column<WorkoutPlan>[] = [
      { key: "goal", header: "Objetivo", render: (plan) => plan.goal },
      { key: "status", header: "Status", render: (plan) => <StatusBadge>{formatFinancialStatus(plan.status)}</StatusBadge> },
      { key: "updated", header: "Atualizado", render: (plan) => formatDateTime(plan.updated_at) }
    ];
    return <DataTable columns={columns} rows={data.workoutPlans} getRowKey={(plan) => plan.id} emptyMessage="Nenhuma ficha de treino encontrada para este aluno." />;
  }

  const accessRows = data.accessDecision === null ? data.accessLogs : [
    {
      id: 0,
      student_id: data.accessDecision.student_id,
      cpf_attempted: data.accessDecision.cpf_attempted,
      accessed_at: new Date().toISOString(),
      allowed: data.accessDecision.allowed,
      reason: data.accessDecision.reason
    },
    ...data.accessLogs
  ];
  const columns: Column<AccessLog>[] = [
    { key: "date", header: "Data", render: (item) => item.id === 0 ? "Agora" : formatDateTime(item.accessed_at) },
    { key: "result", header: "Resultado", render: (item) => <StatusBadge tone={item.allowed ? "success" : "danger"}>{item.allowed ? "Liberado" : "Bloqueado"}</StatusBadge> },
    { key: "cpf", header: "CPF", render: (item) => item.cpf_attempted },
    { key: "reason", header: "Motivo", render: (item) => accessReasonLabel(item.reason) }
  ];
  return <DataTable columns={columns} rows={accessRows} getRowKey={(item) => `${item.id}-${item.accessed_at}-${item.cpf_attempted}`} emptyMessage="Nenhum acesso recente encontrado para este aluno." />;
}
