import type { PageQueryParams, Status } from "./common";

export interface Plan {
  id: number;
  name: string;
  price: string;
  duration_days: number;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface PlanPayload {
  name: string;
  price: string;
  duration_days: number;
  status: Status;
}

export interface PlanQueryParams extends PageQueryParams {
  name?: string;
}

