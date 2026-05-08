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
import { formatCurrency, getErrorMessage } from "./pageUtils";

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
    { key: "name", header: "Name", render: (item) => item.name },
    { key: "cpf", header: "CPF", render: (item) => item.cpf },
    { key: "email", header: "Email", render: (item) => item.email }
  ];
  const defaulterColumns: Column<DefaulterStudentReportItem>[] = [
    { key: "name", header: "Name", render: (item) => item.name },
    { key: "amount", header: "Overdue", render: (item) => formatCurrency(item.overdue_amount) },
    { key: "payments", header: "Payments", render: (item) => item.overdue_payments }
  ];
  const planColumns: Column<MostUsedPlanReportItem>[] = [
    { key: "name", header: "Plan", render: (item) => item.plan_name },
    { key: "count", header: "Enrollments", render: (item) => item.enrollments_count }
  ];
  const accessColumns: Column<DailyAccessReportItem>[] = [
    { key: "date", header: "Date", render: (item) => item.date },
    { key: "total", header: "Total", render: (item) => item.total_attempts },
    { key: "allowed", header: "Allowed", render: (item) => item.allowed_count },
    { key: "blocked", header: "Blocked", render: (item) => item.blocked_count }
  ];

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Reports</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={handleFilter}>
        <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
        <button type="submit">Apply filters</button>
      </form>
      {isLoading ? <LoadingState /> : (
        <>
          <div className="stats-grid">
            {data.active !== undefined && <StatCard label="Active students" value={data.active.total} />}
            {data.defaulters !== undefined && <StatCard label="Defaulters" value={data.defaulters.total} />}
            {data.revenue !== undefined && <StatCard label="Expected revenue" value={formatCurrency(data.revenue.expected_revenue)} />}
            {data.workout !== undefined && <StatCard label="Active workout plans" value={data.workout.active_workout_plans} />}
          </div>
          {data.active !== undefined && <DataTable columns={activeColumns} rows={data.active.students} getRowKey={(item) => item.id} emptyMessage="No active students." />}
          {data.defaulters !== undefined && <DataTable columns={defaulterColumns} rows={data.defaulters.students} getRowKey={(item) => item.student_id} emptyMessage="No defaulters." />}
          {data.plans !== undefined && <DataTable columns={planColumns} rows={data.plans.plans} getRowKey={(item) => item.plan_id} emptyMessage="No plan usage data." />}
          {data.access !== undefined && <DataTable columns={accessColumns} rows={data.access.days} getRowKey={(item) => item.date} emptyMessage="No access data." />}
        </>
      )}
    </section>
  );
}

