import { FormEvent, useEffect, useState } from "react";
import { createPlan, deletePlan, getPlans, updatePlan } from "../api/plansApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import type { Page } from "../types/common";
import type { Plan, PlanPayload } from "../types/plan";
import { formatCurrency, getErrorMessage, STATUS_OPTIONS } from "./pageUtils";

const EMPTY_FORM: PlanPayload = { name: "", price: "", duration_days: 30, status: "ACTIVE" };

export function PlansPage(): JSX.Element {
  const [page, setPage] = useState<Page<Plan> | null>(null);
  const [form, setForm] = useState<PlanPayload>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPlans(): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getPlans({ limit: 50, offset: 0 }));
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
      await loadPlans();
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const columns: Column<Plan>[] = [
    { key: "name", header: "Name", render: (plan) => plan.name },
    { key: "price", header: "Price", render: (plan) => formatCurrency(plan.price) },
    { key: "duration", header: "Days", render: (plan) => plan.duration_days },
    { key: "status", header: "Status", render: (plan) => plan.status },
    {
      key: "actions",
      header: "Actions",
      render: (plan) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => { setEditingId(plan.id); setForm({ name: plan.name, price: plan.price, duration_days: plan.duration_days, status: plan.status }); }}>
            Edit
          </button>
          <button type="button" className="danger" onClick={() => { if (confirm("Deactivate this plan?")) void deletePlan(plan.id).then(loadPlans); }}>
            Delete
          </button>
        </div>
      )
    }
  ];

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Plans</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <input placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        <input placeholder="Price" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} required />
        <input type="number" min="1" value={form.duration_days} onChange={(event) => setForm({ ...form, duration_days: Number(event.target.value) })} required />
        <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as PlanPayload["status"] })}>
          {STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}
        </select>
        <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : editingId === null ? "Create plan" : "Update plan"}</button>
      </form>
      {isLoading || page === null ? <LoadingState /> : <DataTable columns={columns} rows={page.items} getRowKey={(plan) => plan.id} emptyMessage="No plans found." />}
    </section>
  );
}

