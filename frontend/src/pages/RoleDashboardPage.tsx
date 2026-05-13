import { useEffect, useMemo, useState } from "react";
import { getEnrollments } from "../api/enrollmentsApi";
import {
  getActiveStudentsReport,
  getDailyAccessReport,
  getDefaultersReport,
  getMostUsedPlansReport,
  getRevenueSummaryReport,
  getWorkoutSummaryReport
} from "../api/reportsApi";
import { DailyAccessChart, PlanUsageChart, RevenueChart, WorkoutActivityChart } from "../components/Charts";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import {
  ContextPanel,
  DataTableShell,
  PageHeader,
  PageSection,
  QuickActionBar,
  StatGrid
} from "../components/operational";
import { StatCard } from "../components/StatCard";
import { useAuth } from "../contexts/AuthContext";
import type {
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
import { formatCurrency, getErrorMessage } from "./pageUtils";

interface DashboardData {
  activeStudents?: ActiveStudentsReport;
  activeEnrollments?: number;
  defaulters?: DefaultersReport;
  revenue?: RevenueSummaryReport;
  dailyAccess?: DailyAccessReport;
  plans?: MostUsedPlansReport;
  workout?: WorkoutSummaryReport;
}

function accessTotals(report?: DailyAccessReport): { total: number; allowed: number; blocked: number; today?: DailyAccessReportItem } {
  const days = report?.days ?? [];
  const todayKey = new Date().toISOString().slice(0, 10);
  return {
    total: days.reduce((total, day) => total + day.total_attempts, 0),
    allowed: days.reduce((total, day) => total + day.allowed_count, 0),
    blocked: days.reduce((total, day) => total + day.blocked_count, 0),
    today: days.find((day) => day.date === todayKey) ?? days[days.length - 1]
  };
}

function revenueGap(revenue?: RevenueSummaryReport): number {
  if (revenue === undefined) {
    return 0;
  }
  return Number(revenue.overdue_revenue) + Number(revenue.pending_revenue);
}

function DashboardAlerts({ data, role }: { data: DashboardData; role: "ADMIN" | "RECEPTIONIST" | "INSTRUCTOR" }): JSX.Element {
  const alerts: { tone: "danger" | "warning" | "success"; title: string; detail: string }[] = [];
  const totals = accessTotals(data.dailyAccess);

  if (role !== "INSTRUCTOR" && (data.defaulters?.total ?? 0) > 0) {
    alerts.push({
      tone: "danger",
      title: "Inadimplência ativa",
      detail: `${data.defaulters?.total ?? 0} aluno(s) exigem atenção financeira.`
    });
  }
  if (role !== "INSTRUCTOR" && totals.blocked > 0) {
    alerts.push({
      tone: "warning",
      title: "Acessos bloqueados",
      detail: `${totals.blocked} bloqueio(s) no período carregado.`
    });
  }
  if (role !== "RECEPTIONIST" && (data.workout?.inactive_workout_plans ?? 0) > 0) {
    alerts.push({
      tone: "warning",
      title: "Fichas inativas",
      detail: `${data.workout?.inactive_workout_plans ?? 0} ficha(s) precisam revisão.`
    });
  }
  if (alerts.length === 0) {
    alerts.push({
      tone: "success",
      title: "Operação sem alertas críticos",
      detail: "Nenhum ponto crítico apareceu nos indicadores atuais."
    });
  }

  return (
    <div className="dashboard-alerts">
      {alerts.map((alert) => (
        <ContextPanel key={alert.title} tone={alert.tone} title={alert.title}>
          <p>{alert.detail}</p>
        </ContextPanel>
      ))}
    </div>
  );
}

function DefaultersTable({ report, limit = 5 }: { report?: DefaultersReport; limit?: number }): JSX.Element {
  const columns: Column<DefaulterStudentReportItem>[] = [
    { key: "name", header: "Aluno", render: (item) => item.name },
    { key: "amount", header: "Vencido", render: (item) => formatCurrency(item.overdue_amount) },
    { key: "payments", header: "Mensalidades", render: (item) => item.overdue_payments }
  ];
  return (
    <DataTableShell title="Alunos inadimplentes">
      <DataTable
        columns={columns}
        rows={(report?.students ?? []).slice(0, limit)}
        getRowKey={(item) => item.student_id}
        emptyMessage="Nenhum inadimplente no momento."
      />
    </DataTableShell>
  );
}

function PlanTable({ report }: { report?: MostUsedPlansReport }): JSX.Element {
  const columns: Column<MostUsedPlanReportItem>[] = [
    { key: "plan", header: "Plano", render: (item) => item.plan_name },
    { key: "count", header: "Matrículas", render: (item) => item.enrollments_count }
  ];
  return (
    <DataTableShell title="Planos mais usados">
      <DataTable
        columns={columns}
        rows={(report?.plans ?? []).slice(0, 5)}
        getRowKey={(item) => item.plan_id}
        emptyMessage="Sem dados de planos."
      />
    </DataTableShell>
  );
}

function AccessSummary({ report }: { report?: DailyAccessReport }): JSX.Element {
  const totals = accessTotals(report);
  return (
    <ContextPanel title="Resumo de acessos">
      <dl className="detail-list">
        <div><dt>Hoje</dt><dd>{totals.today?.total_attempts ?? 0} tentativa(s)</dd></div>
        <div><dt>Liberados</dt><dd>{totals.allowed}</dd></div>
        <div><dt>Bloqueados</dt><dd>{totals.blocked}</dd></div>
      </dl>
    </ContextPanel>
  );
}

function AdminDashboard({ data }: { data: DashboardData }): JSX.Element {
  const totals = accessTotals(data.dailyAccess);
  return (
    <>
      <PageHeader title="Painel administrativo" description="Prioridade para receita, inadimplência, planos e alertas operacionais." />
      <QuickActionBar actions={[
        { label: "Receber mensalidade", to: "/payments", primary: true },
        { label: "Nova matrícula", to: "/enrollments" },
        { label: "Liberar acesso", to: "/access-control" },
        { label: "Relatórios", to: "/reports" }
      ]} />
      <DashboardAlerts data={data} role="ADMIN" />
      <StatGrid>
        <StatCard label="Receita prevista" value={formatCurrency(data.revenue?.expected_revenue ?? 0)} />
        <StatCard label="Recebido" value={formatCurrency(data.revenue?.received_revenue ?? 0)} />
        <StatCard label="Risco financeiro" value={formatCurrency(revenueGap(data.revenue))} />
        <StatCard label="Matrículas ativas" value={data.activeEnrollments ?? 0} />
        <StatCard label="Alunos ativos" value={data.activeStudents?.total ?? 0} />
        <StatCard label="Inadimplentes" value={data.defaulters?.total ?? 0} />
        <StatCard label="Acessos bloqueados" value={totals.blocked} />
        <StatCard label="Fichas ativas" value={data.workout?.active_workout_plans ?? 0} />
      </StatGrid>
      <div className="dashboard-work-grid">
        <DefaultersTable report={data.defaulters} />
        <PlanTable report={data.plans} />
        <AccessSummary report={data.dailyAccess} />
      </div>
      <PageSection title="Análises detalhadas" description="Gráficos ficam abaixo das ações e alertas operacionais.">
        <div className="chart-grid">
          {data.revenue !== undefined && <RevenueChart received={Number(data.revenue.received_revenue)} overdue={Number(data.revenue.overdue_revenue)} pending={Number(data.revenue.pending_revenue)} />}
          {data.dailyAccess !== undefined && <DailyAccessChart data={data.dailyAccess.days.map((day) => ({ date: day.date, allowed: day.allowed_count, blocked: day.blocked_count }))} />}
          {data.plans !== undefined && <PlanUsageChart data={data.plans.plans.slice(0, 8).map((plan) => ({ name: plan.plan_name, enrollments: plan.enrollments_count }))} />}
          {data.workout !== undefined && <WorkoutActivityChart active={data.workout.active_workout_plans} inactive={data.workout.inactive_workout_plans} progress={data.workout.exercise_progress_records} />}
        </div>
      </PageSection>
    </>
  );
}

function ReceptionistDashboard({ data }: { data: DashboardData }): JSX.Element {
  const totals = accessTotals(data.dailyAccess);
  return (
    <>
      <PageHeader title="Painel da recepção" description="Atalhos e pendências para acelerar atendimento, check-in e cobranças." />
      <QuickActionBar actions={[
        { label: "Check-in rápido", to: "/access-control", primary: true },
        { label: "Atender aluno", to: "/students" },
        { label: "Nova matrícula", to: "/enrollments" },
        { label: "Receber mensalidade", to: "/payments" }
      ]} />
      <DashboardAlerts data={data} role="RECEPTIONIST" />
      <StatGrid>
        <StatCard label="Check-ins hoje" value={totals.today?.total_attempts ?? 0} detail={`${totals.today?.blocked_count ?? 0} bloqueado(s)`} />
        <StatCard label="Alunos inadimplentes" value={data.defaulters?.total ?? 0} />
        <StatCard label="Pagamentos pendentes" value={formatCurrency(data.revenue?.pending_revenue ?? 0)} />
        <StatCard label="Pagamentos vencidos" value={formatCurrency(data.revenue?.overdue_revenue ?? 0)} />
        <StatCard label="Matrículas ativas" value={data.activeEnrollments ?? 0} />
        <StatCard label="Alunos ativos" value={data.activeStudents?.total ?? 0} />
      </StatGrid>
      <div className="dashboard-work-grid">
        <DefaultersTable report={data.defaulters} limit={8} />
        <AccessSummary report={data.dailyAccess} />
        <ContextPanel title="Próximas ações">
          <dl className="detail-list">
            <div><dt>Cobrança</dt><dd>Priorize vencidos e pendentes antes do atendimento de matrícula.</dd></div>
            <div><dt>Check-in</dt><dd>Use o modo rápido para manter o campo de CPF sempre ativo.</dd></div>
            <div><dt>Renovação</dt><dd>Revise matrículas em atendimento quando houver pendência financeira.</dd></div>
          </dl>
        </ContextPanel>
      </div>
      <PageSection title="Acessos do período">
        {data.dailyAccess !== undefined && (
          <div className="chart-grid">
            <DailyAccessChart data={data.dailyAccess.days.map((day) => ({ date: day.date, allowed: day.allowed_count, blocked: day.blocked_count }))} />
          </div>
        )}
      </PageSection>
    </>
  );
}

function InstructorDashboard({ data }: { data: DashboardData }): JSX.Element {
  return (
    <>
      <PageHeader title="Painel do instrutor" description="Foco em fichas ativas, evolução registrada e revisão de treinos." />
      <QuickActionBar actions={[
        { label: "Fichas de treino", to: "/workouts", primary: true },
        { label: "Atender aluno", to: "/students" },
        { label: "Relatórios", to: "/reports" }
      ]} />
      <DashboardAlerts data={data} role="INSTRUCTOR" />
      <StatGrid>
        <StatCard label="Fichas ativas" value={data.workout?.active_workout_plans ?? 0} />
        <StatCard label="Fichas inativas" value={data.workout?.inactive_workout_plans ?? 0} />
        <StatCard label="Exercícios cadastrados" value={data.workout?.total_exercises ?? 0} />
        <StatCard label="Evoluções registradas" value={data.workout?.exercise_progress_records ?? 0} />
      </StatGrid>
      <div className="dashboard-work-grid">
        <ContextPanel title="Atualizações de treino" tone={(data.workout?.inactive_workout_plans ?? 0) > 0 ? "warning" : "success"}>
          <dl className="detail-list">
            <div><dt>Fichas para revisar</dt><dd>{data.workout?.inactive_workout_plans ?? 0}</dd></div>
            <div><dt>Atividade registrada</dt><dd>{data.workout?.exercise_progress_records ?? 0} evolução(ões)</dd></div>
            <div><dt>Próximo passo</dt><dd>Abra fichas de treino e atualize cargas, repetições ou observações.</dd></div>
          </dl>
        </ContextPanel>
        <ContextPanel title="Acesso rápido ao atendimento">
          <p>Use a busca de alunos para abrir o contexto do aluno e revisar fichas sem trocar de fluxo.</p>
        </ContextPanel>
      </div>
      <PageSection title="Resumo de treinos">
        {data.workout !== undefined && (
          <div className="chart-grid">
            <WorkoutActivityChart active={data.workout.active_workout_plans} inactive={data.workout.inactive_workout_plans} progress={data.workout.exercise_progress_records} />
          </div>
        )}
      </PageSection>
    </>
  );
}

export function RoleDashboardPage(): JSX.Element {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadDashboard(): Promise<void> {
      if (user === null) {
        return;
      }
      setIsLoading(true);
      setError(null);
      try {
        const nextData: DashboardData = {};
        if (user.role === "ADMIN" || user.role === "RECEPTIONIST") {
          const [activeStudents, defaulters, revenue, dailyAccess, plans, activeEnrollments] = await Promise.all([
            getActiveStudentsReport(),
            getDefaultersReport(),
            getRevenueSummaryReport(),
            getDailyAccessReport(),
            getMostUsedPlansReport(),
            getEnrollments({ limit: 1, status: "ACTIVE" })
          ]);
          nextData.activeStudents = activeStudents;
          nextData.defaulters = defaulters;
          nextData.revenue = revenue;
          nextData.dailyAccess = dailyAccess;
          nextData.plans = plans;
          nextData.activeEnrollments = activeEnrollments.total;
        }
        if (user.role === "ADMIN" || user.role === "INSTRUCTOR") {
          nextData.workout = await getWorkoutSummaryReport();
        }
        if (isMounted) {
          setData(nextData);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(getErrorMessage(loadError));
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }
    void loadDashboard();
    return () => {
      isMounted = false;
    };
  }, [user]);

  const dashboardContent = useMemo(() => {
    if (user?.role === "ADMIN") {
      return <AdminDashboard data={data} />;
    }
    if (user?.role === "RECEPTIONIST") {
      return <ReceptionistDashboard data={data} />;
    }
    return <InstructorDashboard data={data} />;
  }, [data, user?.role]);

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <section className="page-stack role-dashboard-page">
      {error !== null && <ErrorState message={error} />}
      {dashboardContent}
    </section>
  );
}
