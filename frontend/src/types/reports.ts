import type { Status } from "./common";
import type { FinancialStatus } from "./student";

export interface DateRangeParams {
  start_date?: string;
  end_date?: string;
}

export interface ActiveStudentReportItem {
  id: number;
  name: string;
  cpf: string;
  email: string;
  status: Status;
  financial_status: FinancialStatus;
}

export interface ActiveStudentsReport {
  total: number;
  students: ActiveStudentReportItem[];
}

export interface DefaulterStudentReportItem {
  student_id: number;
  name: string;
  cpf: string;
  email: string;
  overdue_amount: string;
  overdue_payments: number;
}

export interface DefaultersReport {
  total: number;
  students: DefaulterStudentReportItem[];
}

export interface MostUsedPlanReportItem {
  plan_id: number;
  plan_name: string;
  enrollments_count: number;
}

export interface MostUsedPlansReport {
  plans: MostUsedPlanReportItem[];
}

export interface RevenueSummaryReport {
  expected_revenue: string;
  received_revenue: string;
  overdue_revenue: string;
  pending_revenue: string;
}

export interface DailyAccessReportItem {
  date: string;
  total_attempts: number;
  allowed_count: number;
  blocked_count: number;
}

export interface DailyAccessReport {
  days: DailyAccessReportItem[];
}

export interface WorkoutSummaryReport {
  active_workout_plans: number;
  inactive_workout_plans: number;
  total_exercises: number;
  exercise_progress_records: number;
}
