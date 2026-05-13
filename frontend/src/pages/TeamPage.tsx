import { FormEvent, useEffect, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import {
  createUser,
  deleteUser,
  getUserAuditLogs,
  getUsers,
  resetUserPassword,
  updateUser,
  type UserAuditLog,
  type UserCreatePayload
} from "../api/usersApi";
import { transferWorkoutPlans } from "../api/workoutsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatusBadge } from "../components/operational";
import { useAuth } from "../contexts/AuthContext";
import { useSortableRows } from "../hooks/useSortableRows";
import type { AuthUser } from "../types/auth";
import type { Page, Role } from "../types/common";
import { formatDateTime, getErrorMessage } from "./pageUtils";

const ROLE_OPTIONS: Role[] = ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"];
const ROLE_LABELS: Record<Role, string> = {
  ADMIN: "Administrador",
  RECEPTIONIST: "Recepcao",
  INSTRUCTOR: "Instrutor"
};
const EMPTY_FORM: UserCreatePayload = {
  email: "",
  full_name: "",
  password: "",
  role: "RECEPTIONIST"
};

export function TeamPage(): JSX.Element {
  const { user: currentUser } = useAuth();
  const [page, setPage] = useState<Page<AuthUser> | null>(null);
  const [form, setForm] = useState<UserCreatePayload>(EMPTY_FORM);
  const [roleFilter, setRoleFilter] = useState<"" | Role>("");
  const [statusFilter, setStatusFilter] = useState<"" | "active" | "inactive">("active");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [auditUsers, setAuditUsers] = useState<AuthUser[]>([]);
  const [activeInstructors, setActiveInstructors] = useState<AuthUser[]>([]);
  const [auditPage, setAuditPage] = useState<Page<UserAuditLog> | null>(null);
  const [transferFrom, setTransferFrom] = useState<AuthUser | null>(null);
  const [transferToId, setTransferToId] = useState("");
  const [passwordResetUser, setPasswordResetUser] = useState<AuthUser | null>(null);
  const [temporaryPassword, setTemporaryPassword] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isTransferring, setIsTransferring] = useState(false);
  const [isResettingPassword, setIsResettingPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadUsers(offset = page?.offset ?? 0): Promise<void> {
    setIsLoading(true);
    setError(null);
    try {
      setPage(await getUsers({
        limit: 20,
        offset,
        role: roleFilter || undefined,
        is_active: statusFilter === "" ? undefined : statusFilter === "active"
      }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadUsers();
    void loadActiveInstructors();
    void loadAuditLogs();
  }, []);

  async function loadActiveInstructors(): Promise<void> {
    const instructorPage = await getUsers({ limit: 100, role: "INSTRUCTOR", is_active: true });
    setActiveInstructors(instructorPage.items);
  }

  async function loadAuditLogs(): Promise<void> {
    const [logs, users] = await Promise.all([
      getUserAuditLogs({ limit: 8 }),
      getUsers({ limit: 100, is_active: undefined })
    ]);
    setAuditPage(logs);
    setAuditUsers(users.items);
  }

  function startEdit(user: AuthUser): void {
    setEditingId(user.id);
    setForm({
      email: user.email,
      full_name: user.full_name,
      password: "",
      role: user.role
    });
  }

  function resetForm(): void {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      if (editingId === null) {
        await createUser(form);
      } else {
        await updateUser(editingId, {
          email: form.email,
          full_name: form.full_name,
          role: form.role,
          ...(form.password === "" ? {} : { password: form.password })
        });
      }
      toast.success(editingId === null ? "Usuario criado." : "Usuario atualizado.");
      resetForm();
      await Promise.all([loadUsers(), loadAuditLogs(), loadActiveInstructors()]);
    } catch (submitError) {
      toast.error("Nao foi possivel salvar o usuario.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeactivate(user: AuthUser): Promise<void> {
    if (!confirm("Desativar este usuario?")) {
      return;
    }
    try {
      await deleteUser(user.id);
      toast.success("Usuario desativado.");
      await Promise.all([loadUsers(), loadAuditLogs(), loadActiveInstructors()]);
    } catch (deleteError) {
      if (getApiErrorCode(deleteError) === "INSTRUCTOR_HAS_ACTIVE_WORKOUT_PLANS") {
        setTransferFrom(user);
        setTransferToId("");
        toast.error("Transfira as fichas ativas antes de desativar o instrutor.");
        setError("Este instrutor possui fichas ativas. Selecione outro instrutor para receber as fichas e tente novamente.");
        await loadActiveInstructors();
        return;
      }
      toast.error("Nao foi possivel desativar o usuario.");
      setError(getErrorMessage(deleteError));
    }
  }

  async function handleTransferAndDeactivate(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (transferFrom === null || transferToId === "") {
      return;
    }
    setIsTransferring(true);
    setError(null);
    try {
      const result = await transferWorkoutPlans({
        from_instructor_id: transferFrom.id,
        to_instructor_id: Number(transferToId),
        status: "ACTIVE"
      });
      await deleteUser(transferFrom.id);
      toast.success(`${result.transferred_count} ficha(s) transferida(s). Instrutor desativado.`);
      setTransferFrom(null);
      setTransferToId("");
      await Promise.all([loadUsers(), loadActiveInstructors(), loadAuditLogs()]);
    } catch (transferError) {
      toast.error("Nao foi possivel transferir as fichas.");
      setError(getErrorMessage(transferError));
    } finally {
      setIsTransferring(false);
    }
  }

  async function handleReactivate(user: AuthUser): Promise<void> {
    try {
      await updateUser(user.id, { is_active: true });
      toast.success("Usuario reativado.");
      await Promise.all([loadUsers(), loadAuditLogs(), loadActiveInstructors()]);
    } catch (updateError) {
      toast.error("Nao foi possivel reativar o usuario.");
      setError(getErrorMessage(updateError));
    }
  }

  async function handleResetPassword(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (passwordResetUser === null) {
      return;
    }
    setIsResettingPassword(true);
    setError(null);
    try {
      await resetUserPassword(passwordResetUser.id, { temporary_password: temporaryPassword });
      toast.success("Senha temporaria definida.");
      setPasswordResetUser(null);
      setTemporaryPassword("");
      await Promise.all([loadUsers(), loadAuditLogs()]);
    } catch (resetError) {
      toast.error("Nao foi possivel redefinir a senha.");
      setError(getErrorMessage(resetError));
    } finally {
      setIsResettingPassword(false);
    }
  }

  const columns: Column<AuthUser>[] = [
    { key: "name", header: "Nome", render: (user) => user.full_name, sortValue: (user) => user.full_name },
    { key: "email", header: "E-mail", render: (user) => user.email, sortValue: (user) => user.email },
    { key: "role", header: "Papel", render: (user) => ROLE_LABELS[user.role], sortValue: (user) => ROLE_LABELS[user.role] },
    {
      key: "status",
      header: "Status",
      render: (user) => <StatusBadge tone={user.is_active ? "success" : "neutral"}>{user.is_active ? "Ativo" : "Inativo"}</StatusBadge>,
      sortValue: (user) => (user.is_active ? "Ativo" : "Inativo")
    },
    {
      key: "password",
      header: "Senha",
      render: (user) => (
        <StatusBadge tone={user.must_change_password ? "warning" : "success"}>
          {user.must_change_password ? "Troca pendente" : "Definida"}
        </StatusBadge>
      ),
      sortValue: (user) => (user.must_change_password ? "Troca pendente" : "Definida")
    },
    { key: "created", header: "Criado", render: (user) => formatDateTime(user.created_at), sortValue: (user) => user.created_at },
    {
      key: "lastLogin",
      header: "Ultimo acesso",
      render: (user) => user.last_login_at === null ? "-" : formatDateTime(user.last_login_at),
      sortValue: (user) => user.last_login_at ?? ""
    },
    { key: "updated", header: "Atualizado", render: (user) => formatDateTime(user.updated_at), sortValue: (user) => user.updated_at },
    {
      key: "actions",
      header: "Acoes",
      render: (user) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => startEdit(user)}>
            Editar
          </button>
          <button type="button" className="secondary" onClick={() => { setPasswordResetUser(user); setTemporaryPassword(""); }}>
            Redefinir senha
          </button>
          {user.is_active ? (
            <button type="button" className="danger" disabled={user.id === currentUser?.id} onClick={() => void handleDeactivate(user)}>
              Desativar
            </button>
          ) : (
            <button type="button" className="secondary" onClick={() => void handleReactivate(user)}>
              Reativar
            </button>
          )}
        </div>
      )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);
  const transferTargets = activeInstructors.filter((instructor) => instructor.id !== transferFrom?.id);
  const totalUsers = page?.total ?? 0;
  const activeCount = page?.items.filter((user) => user.is_active).length ?? 0;
  const inactiveCount = page?.items.filter((user) => !user.is_active).length ?? 0;
  const pendingPasswordCount = page?.items.filter((user) => user.must_change_password).length ?? 0;

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Equipe</h1></header>
      {error !== null && <ErrorState message={error} />}
      <div className="stats-grid">
        <div className="stat-card"><span>Total no filtro</span><strong>{totalUsers}</strong></div>
        <div className="stat-card"><span>Ativos nesta pagina</span><strong>{activeCount}</strong></div>
        <div className="stat-card"><span>Inativos nesta pagina</span><strong>{inactiveCount}</strong></div>
        <div className="stat-card"><span>Senhas pendentes</span><strong>{pendingPasswordCount}</strong></div>
      </div>
      {transferFrom !== null && (
        <form className="panel form-grid" onSubmit={handleTransferAndDeactivate}>
          <label>Instrutor atual<input value={transferFrom.full_name} disabled /></label>
          <label>Novo instrutor
            <select value={transferToId} onChange={(event) => setTransferToId(event.target.value)} required disabled={transferTargets.length === 0}>
              <option value="">{transferTargets.length === 0 ? "Cadastre outro instrutor ativo" : "Selecionar instrutor"}</option>
              {transferTargets.map((instructor) => (
                <option key={instructor.id} value={instructor.id}>{instructor.full_name}</option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={isTransferring || transferTargets.length === 0}>
            {isTransferring ? "Transferindo..." : "Transferir fichas e desativar"}
          </button>
          <button type="button" className="secondary" onClick={() => setTransferFrom(null)}>Cancelar</button>
        </form>
      )}
      {passwordResetUser !== null && (
        <form className="panel form-grid" onSubmit={handleResetPassword}>
          <label>Usuario<input value={passwordResetUser.full_name} disabled /></label>
          <label>Senha temporaria
            <input
              type="password"
              value={temporaryPassword}
              onChange={(event) => setTemporaryPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          <button type="submit" disabled={isResettingPassword}>
            {isResettingPassword ? "Redefinindo..." : "Definir senha temporaria"}
          </button>
          <button type="button" className="secondary" onClick={() => setPasswordResetUser(null)}>Cancelar</button>
        </form>
      )}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadUsers(0); }}>
        <label>Papel<select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value as "" | Role)}>
          <option value="">Todos</option>
          {ROLE_OPTIONS.map((role) => <option key={role} value={role}>{ROLE_LABELS[role]}</option>)}
        </select></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "" | "active" | "inactive")}>
          <option value="active">Ativos</option>
          <option value="inactive">Inativos</option>
          <option value="">Todos</option>
        </select></label>
        <button type="submit">Filtrar</button>
      </form>
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <label>Nome<input placeholder="Nome completo" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} required /></label>
        <label>E-mail<input type="email" placeholder="E-mail" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label>
        <label>Senha temporaria<input type="password" placeholder={editingId === null ? "Senha inicial" : "Use redefinir senha"} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required={editingId === null} disabled={editingId !== null} /></label>
        <label>Papel<select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as Role })}>
          {ROLE_OPTIONS.map((role) => <option key={role} value={role}>{ROLE_LABELS[role]}</option>)}
        </select></label>
        <button type="submit" disabled={isSaving}>{isSaving ? "Salvando..." : editingId === null ? "Criar usuario" : "Atualizar usuario"}</button>
        {editingId !== null && <button type="button" className="secondary" onClick={resetForm}>Cancelar edicao</button>}
      </form>
      {page === null ? <LoadingState /> : <DataTable columns={columns} rows={sorted.rows} getRowKey={(user) => user.id} emptyMessage="Nenhum usuario encontrado." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadUsers(nextOffset)} sortKey={sorted.sortKey} sortDirection={sorted.sortDirection} onSortChange={sorted.setSortKey} />}
      <section className="panel">
        <header className="section-header">
          <h2>Auditoria recente</h2>
        </header>
        {auditPage === null ? <LoadingState message="Carregando auditoria..." /> : (
          <DataTable
            columns={[
              { key: "created", header: "Data", render: (log) => formatDateTime(log.created_at), sortValue: (log) => log.created_at },
              { key: "action", header: "Evento", render: (log) => formatAuditAction(log.action), sortValue: (log) => log.action },
              { key: "actor", header: "Autor", render: (log) => userName(log.actor_user_id, auditUsers) },
              { key: "target", header: "Alvo", render: (log) => userName(log.target_user_id, auditUsers) },
              { key: "details", header: "Detalhes", render: (log) => formatAuditDetails(log.details) }
            ]}
            rows={auditPage.items}
            getRowKey={(log) => log.id}
            emptyMessage="Nenhum evento registrado."
          />
        )}
      </section>
    </section>
  );
}

function userName(userId: number | null, users: AuthUser[]): string {
  if (userId === null) {
    return "-";
  }
  return users.find((user) => user.id === userId)?.full_name ?? "Usuário não encontrado";
}

function formatAuditAction(action: string): string {
  const labels: Record<string, string> = {
    PASSWORD_CHANGED: "Senha alterada",
    PASSWORD_RESET: "Senha redefinida",
    USER_CREATED: "Usuario criado",
    USER_DEACTIVATED: "Usuario desativado",
    USER_UPDATED: "Usuario atualizado"
  };
  return labels[action] ?? action;
}

function formatAuditDetails(details: string | null): string {
  if (details === null || details.trim() === "") {
    return "-";
  }

  const labels: Record<string, string> = {
    email: "e-mail alterado",
    full_name: "nome alterado",
    is_active: "status alterado",
    password_hash: "senha alterada",
    role: "papel alterado",
    "role=ADMIN": "Administrador",
    "role=INSTRUCTOR": "Instrutor",
    "role=RECEPTIONIST": "Recepção",
    "temporary_password=true": "senha temporária"
  };

  return details
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => labels[item] ?? item)
    .join(", ");
}

function getApiErrorCode(error: unknown): string | null {
  if (!axios.isAxiosError(error)) {
    return null;
  }
  const data = error.response?.data;
  if (typeof data !== "object" || data === null || !("error" in data)) {
    return null;
  }
  const detail = data.error;
  if (typeof detail !== "object" || detail === null || !("code" in detail)) {
    return null;
  }
  return String(detail.code);
}
