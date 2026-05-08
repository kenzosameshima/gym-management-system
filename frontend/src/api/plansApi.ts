import { httpClient } from "./httpClient";
import type { Page } from "../types/common";
import type { Plan, PlanPayload, PlanQueryParams } from "../types/plan";

const PLAN_ENDPOINTS = {
  base: "/api/plans",
  byId: (planId: number) => `/api/plans/${planId}`
} as const;

export async function getPlans(params: PlanQueryParams = {}): Promise<Page<Plan>> {
  const response = await httpClient.get<Page<Plan>>(PLAN_ENDPOINTS.base, { params });
  return response.data;
}

export async function createPlan(payload: PlanPayload): Promise<Plan> {
  const response = await httpClient.post<Plan>(PLAN_ENDPOINTS.base, payload);
  return response.data;
}

export async function updatePlan(planId: number, payload: Partial<PlanPayload>): Promise<Plan> {
  const response = await httpClient.put<Plan>(PLAN_ENDPOINTS.byId(planId), payload);
  return response.data;
}

export async function deletePlan(planId: number): Promise<Plan> {
  const response = await httpClient.delete<Plan>(PLAN_ENDPOINTS.byId(planId));
  return response.data;
}

