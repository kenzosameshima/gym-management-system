import { useEffect, useState } from "react";
import {
  getActiveStudentsReport,
  getDailyAccessReport,
  getDefaultersReport,
  getRevenueSummaryReport,
  getWorkoutSummaryReport
} from "../api/reportsApi";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatCard } from "../components/StatCard";
import { useAuth } from "../contexts/AuthContext";
import type {
  ActiveStudentsReport,
  DailyAccessReport,
  DefaultersReport,
  RevenueSummaryReport,
  WorkoutSummaryReport
} from "../types/reports";
import { formatCurrency, getErrorMessage } from "./pageUtils";

interface DashboardData {
  activeStudents?: ActiveStudentsReport;
  defaulters?: DefaultersReport;
  revenue?: RevenueSummaryReport;
  dailyAccess?: DailyAccessReport;
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
          const [activeStudents, defaulters, revenue, dailyAccess] = await Promise.all([
            getActiveStudentsReport(),
            getDefaultersReport(),
            getRevenueSummaryReport(),
            getDailyAccessReport()
          ]);
          nextData.activeStudents = activeStudents;
          nextData.defaulters = defaulters;
          nextData.revenue = revenue;
          nextData.dailyAccess = dailyAccess;
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
        <h1>Dashboard</h1>
      </header>
      {error !== null && <ErrorState message={error} />}
      <div className="stats-grid">
        {data.activeStudents !== undefined && <StatCard label="Active students" value={data.activeStudents.total} />}
        {data.defaulters !== undefined && <StatCard label="Defaulters" value={data.defaulters.total} />}
        {data.revenue !== undefined && (
          <StatCard label="Received revenue" value={formatCurrency(data.revenue.received_revenue)} />
        )}
        {data.dailyAccess !== undefined && (
          <StatCard
            label="Access attempts"
            value={data.dailyAccess.days.reduce((total, day) => total + day.total_attempts, 0)}
          />
        )}
        {data.workout !== undefined && (
          <StatCard
            label="Workout plans"
            value={data.workout.active_workout_plans}
            detail={`${data.workout.total_exercises} exercises`}
          />
        )}
      </div>
    </section>
  );
}

