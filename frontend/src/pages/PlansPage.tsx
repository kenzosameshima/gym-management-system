import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { createPlan, deletePlan, getPlans, updatePlan } from "../api/plansApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useSortableRows } from "../hooks/useSortableRows";
import type { Page } from "../types/common";
import type { Plan, PlanPayload } from "../types/plan";
import { formatCurrency, getErrorMessage, STATUS_OPTIONS } from "./pageUtils";

const EMPTY_FORM: PlanPayload = { name: "", price: "", duration_days: 30, status: "ACTIVE" };

export function PlansPage(): JSX.Element {
  const [page, setPage] = useState<Page<Plan> | null>(null);
  const [form, setForm] = useState<PlanPayload>(EMPTY_FORM);
  const [nameSearch, setNameSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"" | PlanPayload["status"]>("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPlans(offset = page?.offset ?? 0): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getPlans({ limit: 20, offset, name: nameSearch || undefined, status: statusFilter || undefined }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadPlans();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    try {
      if (editingId === null) {
        await createPlan(form);
      } else {
        await updatePlan(editingId, form);
      }
      setForm(EMPTY_FORM);
      setEditingId(null);
      toast.success(editingId === null ? "Plano criado." : "Plano atualizado.");
      await loadPlans();
    } catch (submitError) {
      toast.error("Nao foi possivel salvar o plano.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Plan>[] = [
    { key: "name", header: "Plano", render: (plan) => plan.name, sortValue: (plan) => plan.name },
    { key: "price", header: "Valor", render: (plan) => formatCurrency(plan.price), sortValue: (plan) => Number(plan.price) },
    { key: "duration", header: "Dias", render: (plan) => plan.duration_days },
    { key: "status", header: "Status", render: (plan) => plan.status },
    {
      key: "actions",
      header: "Acoes",
      render: (plan) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => { setEditingId(plan.id); setForm({ name: plan.name, price: plan.price, duration_days: plan.duration_days, status: plan.status }); }}>
            Editar
          </button>
          <button type="button" className="danger" onClick={() => { if (confirm("Desativar este plano?")) void deletePlan(plan.id).then(() => { toast.success("Plano desativado."); return loadPlans(); }); }}>
            Desativar
          </button>
        </div>
      )
    }
  ];
  const sorted = useSortableRows(page?.items ?? [], columns);

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Planos e renovacoes</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadPlans(); }}>
        <label>Plano<input placeholder="Nome do plano" value={nameSearch} onChange={(event) => setNameSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "" | PlanPayload["status"])}>
          <option value="">Todos</option>
          {STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}
        </select></label>
        <button type="submit">Filtrar</button>
      </form>
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <input placeholder="Nome do plano" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        <input placeholder="Valor" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} required />
        <input type="number" min="1" value={form.duration_days} onChange={(event) => setForm({ ...form, duration_days: Number(event.target.value) })} required />
        <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as PlanPayload["status"] })}>
          {STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}
        </select>
        <button type="submit" disabled={isSaving}>{isSaving ? "Salvando..." : editingId === null ? "Criar plano" : "Atualizar plano"}</button>
      </form>
      {page === null ? <LoadingState /> : <DataTable columns={columns} rows={sorted.rows} getRowKey={(plan) => plan.id} emptyMessage="Nenhum plano encontrado." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadPlans(nextOffset)} sortKey={sorted.sortKey} sortDirection={sorted.sortDirection} onSortChange={sorted.setSortKey} />}
    </section>
  );
}
