import { FormEvent, useEffect, useState } from "react";
import {
  getActiveStudentsReport,
  getDailyAccessReport,
  getDefaultersReport,
  getMostUsedPlansReport,
  getRevenueSummaryReport,
  getWorkoutSummaryReport
} from "../api/reportsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatCard } from "../components/StatCard";
import { useAuth } from "../contexts/AuthContext";
import type {
  ActiveStudentReportItem,
  ActiveStudentsReport,
  DailyAccessReport,
  DailyAccessReportItem,
  DefaulterStudentReportItem,
  DefaultersReport,
  MostUsedPlanReportItem,
  MostUsedPlansReport,
  RevenueSummaryReport,
  WorkoutSummaryReport
} from "../types/reports";
import { formatCurrency, formatFinancialStatus, getErrorMessage } from "./pageUtils";

interface ReportData {
  active?: ActiveStudentsReport;
  defaulters?: DefaultersReport;
  plans?: MostUsedPlansReport;
  revenue?: RevenueSummaryReport;
  access?: DailyAccessReport;
  workout?: WorkoutSummaryReport;
}

export function ReportsPage(): JSX.Element {
  const { user } = useAuth();
  const [data, setData] = useState<ReportData>({});
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadReports(): Promise<void> {
    if (user === null) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const params = { start_date: startDate || undefined, end_date: endDate || undefined };
      const nextData: ReportData = {};
      if (user.role === "ADMIN" || user.role === "RECEPTIONIST") {
        const [active, defaulters, plans, revenue, access] = await Promise.all([
          getActiveStudentsReport(),
          getDefaultersReport(),
          getMostUsedPlansReport(),
          getRevenueSummaryReport(params),
          getDailyAccessReport(params)
        ]);
        nextData.active = active;
        nextData.defaulters = defaulters;
        nextData.plans = plans;
        nextData.revenue = revenue;
        nextData.access = access;
      }
      if (user.role === "ADMIN" || user.role === "INSTRUCTOR") {
        nextData.workout = await getWorkoutSummaryReport();
      }
      setData(nextData);
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadReports();
  }, [user]);

  function handleFilter(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    void loadReports();
  }

  const activeColumns: Column<ActiveStudentReportItem>[] = [
    { key: "name", header: "Nome", render: (item) => item.name },
    { key: "cpf", header: "CPF", render: (item) => item.cpf },
    { key: "email", header: "E-mail", render: (item) => item.email },
    { key: "financial", header: "Situacao financeira", render: (item) => formatFinancialStatus(item.financial_status) }
  ];
  const defaulterColumns: Column<DefaulterStudentReportItem>[] = [
    { key: "name", header: "Nome", render: (item) => item.name },
    { key: "amount", header: "Vencido", render: (item) => formatCurrency(item.overdue_amount) },
    { key: "payments", header: "Mensalidades", render: (item) => item.overdue_payments }
  ];
  const planColumns: Column<MostUsedPlanReportItem>[] = [
    { key: "name", header: "Plano", render: (item) => item.plan_name },
    { key: "count", header: "Matriculas", render: (item) => item.enrollments_count }
  ];
  const accessColumns: Column<DailyAccessReportItem>[] = [
    { key: "date", header: "Data", render: (item) => item.date },
    { key: "total", header: "Total", render: (item) => item.total_attempts },
    { key: "allowed", header: "Liberados", render: (item) => item.allowed_count },
    { key: "blocked", header: "Bloqueados", render: (item) => item.blocked_count }
  ];

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Indicadores e relatorios</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={handleFilter}>
        <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
        <button type="submit">Aplicar filtros</button>
      </form>
      {isLoading ? <LoadingState /> : (
        <>
          <div className="stats-grid">
            {data.active !== undefined && <StatCard label="Alunos ativos" value={data.active.total} />}
            {data.defaulters !== undefined && <StatCard label="Inadimplentes" value={data.defaulters.total} />}
            {data.revenue !== undefined && <StatCard label="Receita prevista" value={formatCurrency(data.revenue.expected_revenue)} />}
            {data.workout !== undefined && <StatCard label="Fichas ativas" value={data.workout.active_workout_plans} />}
          </div>
          {data.active !== undefined && <DataTable columns={activeColumns} rows={data.active.students} getRowKey={(item) => item.id} emptyMessage="Nenhum aluno ativo." />}
          {data.defaulters !== undefined && <DataTable columns={defaulterColumns} rows={data.defaulters.students} getRowKey={(item) => item.student_id} emptyMessage="Nenhum inadimplente." />}
          {data.plans !== undefined && <DataTable columns={planColumns} rows={data.plans.plans} getRowKey={(item) => item.plan_id} emptyMessage="Sem dados de planos." />}
          {data.access !== undefined && <DataTable columns={accessColumns} rows={data.access.days} getRowKey={(item) => item.date} emptyMessage="Sem dados de acesso." />}
        </>
      )}
    </section>
  );
}
