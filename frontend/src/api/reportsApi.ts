import { httpClient } from "./httpClient";
import type {
  ActiveStudentsReport,
  DailyAccessReport,
  DateRangeParams,
  DefaultersReport,
  MostUsedPlansReport,
  RevenueSummaryReport,
  WorkoutSummaryReport
} from "../types/reports";

const REPORT_ENDPOINTS = {
  activeStudents: "/api/reports/students/active",
  defaulters: "/api/reports/students/defaulters",
  mostUsedPlans: "/api/reports/plans/most-used",
  revenueSummary: "/api/reports/revenue/summary",
  dailyAccess: "/api/reports/access/daily",
  workoutSummary: "/api/reports/workouts/summary"
} as const;

export async function getActiveStudentsReport(): Promise<ActiveStudentsReport> {
  const response = await httpClient.get<ActiveStudentsReport>(REPORT_ENDPOINTS.activeStudents);
  return response.data;
}

export async function getDefaultersReport(): Promise<DefaultersReport> {
  const response = await httpClient.get<DefaultersReport>(REPORT_ENDPOINTS.defaulters);
  return response.data;
}

export async function getMostUsedPlansReport(): Promise<MostUsedPlansReport> {
  const response = await httpClient.get<MostUsedPlansReport>(REPORT_ENDPOINTS.mostUsedPlans);
  return response.data;
}

export async function getRevenueSummaryReport(params: DateRangeParams = {}): Promise<RevenueSummaryReport> {
  const response = await httpClient.get<RevenueSummaryReport>(REPORT_ENDPOINTS.revenueSummary, { params });
  return response.data;
}

export async function getDailyAccessReport(params: DateRangeParams = {}): Promise<DailyAccessReport> {
  const response = await httpClient.get<DailyAccessReport>(REPORT_ENDPOINTS.dailyAccess, { params });
  return response.data;
}

export async function getWorkoutSummaryReport(): Promise<WorkoutSummaryReport> {
  const response = await httpClient.get<WorkoutSummaryReport>(REPORT_ENDPOINTS.workoutSummary);
  return response.data;
}

