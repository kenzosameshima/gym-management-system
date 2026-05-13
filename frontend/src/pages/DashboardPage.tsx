import { useEffect, useState } from "react";
import {
  getActiveStudentsReport,
  getDailyAccessReport,
  getDefaultersReport,
  getMostUsedPlansReport,
  getRevenueSummaryReport,
  getWorkoutSummaryReport
} from "../api/reportsApi";
import { DailyAccessChart, PlanUsageChart, RevenueChart, WorkoutActivityChart } from "../components/Charts";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatCard } from "../components/StatCard";
import { useAuth } from "../contexts/AuthContext";
import type {
  ActiveStudentsReport,
  DailyAccessReport,
  DefaultersReport,
  MostUsedPlansReport,
  RevenueSummaryReport,
  WorkoutSummaryReport
} from "../types/reports";
import { formatCurrency, getErrorMessage } from "./pageUtils";

interface DashboardData {
  activeStudents?: ActiveStudentsReport;
  defaulters?: DefaultersReport;
  revenue?: RevenueSummaryReport;
  dailyAccess?: DailyAccessReport;
  plans?: MostUsedPlansReport;
  workout?: WorkoutSummaryReport;
}

export function DashboardPage(): JSX.Element {
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
          const [activeStudents, defaulters, revenue, dailyAccess, plans] = await Promise.all([
            getActiveStudentsReport(),
            getDefaultersReport(),
            getRevenueSummaryReport(),
            getDailyAccessReport(),
            getMostUsedPlansReport()
          ]);
          nextData.activeStudents = activeStudents;
          nextData.defaulters = defaulters;
          nextData.revenue = revenue;
          nextData.dailyAccess = dailyAccess;
          nextData.plans = plans;
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

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <h1>Visao geral da operacao</h1>
      </header>
      {error !== null && <ErrorState message={error} />}
      <div className="stats-grid">
        {data.activeStudents !== undefined && <StatCard label="Alunos ativos" value={data.activeStudents.total} />}
        {data.defaulters !== undefined && <StatCard label="Alunos inadimplentes" value={data.defaulters.total} />}
        {data.revenue !== undefined && (
          <>
            <StatCard label="Receita prevista" value={formatCurrency(data.revenue.expected_revenue)} />
            <StatCard label="Recebido" value={formatCurrency(data.revenue.received_revenue)} />
            <StatCard label="Vencido" value={formatCurrency(data.revenue.overdue_revenue)} />
            <StatCard label="A receber" value={formatCurrency(data.revenue.pending_revenue)} />
          </>
        )}
        {data.dailyAccess !== undefined && (
          <>
            <StatCard label="Check-ins" value={data.dailyAccess.days.reduce((total, day) => total + day.total_attempts, 0)} />
            <StatCard label="Acessos liberados" value={data.dailyAccess.days.reduce((total, day) => total + day.allowed_count, 0)} />
            <StatCard label="Acessos bloqueados" value={data.dailyAccess.days.reduce((total, day) => total + day.blocked_count, 0)} />
          </>
        )}
        {data.workout !== undefined && (
          <>
            <StatCard label="Fichas ativas" value={data.workout.active_workout_plans} detail={`${data.workout.total_exercises} exercicios`} />
            <StatCard label="Evolucoes registradas" value={data.workout.exercise_progress_records} />
          </>
        )}
      </div>
      <div className="chart-grid">
        {data.revenue !== undefined && (
          <RevenueChart
            received={Number(data.revenue.received_revenue)}
            overdue={Number(data.revenue.overdue_revenue)}
            pending={Number(data.revenue.pending_revenue)}
          />
        )}
        {data.dailyAccess !== undefined && (
          <DailyAccessChart
            data={data.dailyAccess.days.map((day) => ({
              date: day.date,
              allowed: day.allowed_count,
              blocked: day.blocked_count
            }))}
          />
        )}
        {data.plans !== undefined && (
          <PlanUsageChart
            data={data.plans.plans.slice(0, 8).map((plan) => ({
              name: plan.plan_name,
              enrollments: plan.enrollments_count
            }))}
          />
        )}
        {data.workout !== undefined && (
          <WorkoutActivityChart
            active={data.workout.active_workout_plans}
            inactive={data.workout.inactive_workout_plans}
            progress={data.workout.exercise_progress_records}
          />
        )}
      </div>
    </section>
  );
}
