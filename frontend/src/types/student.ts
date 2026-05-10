import type { PageQueryParams, Status } from "./common";

export type FinancialStatus =
  | "IN_GOOD_STANDING"
  | "DEFAULTER"
  | "NO_ACTIVE_ENROLLMENT"
  | "INACTIVE";

export interface Student {
  id: number;
  name: string;
  cpf: string;
  birth_date: string;
  phone: string;
  email: string;
  address: string;
  status: Status;
  financial_status: FinancialStatus;
  created_at: string;
  updated_at: string;
}

export interface StudentPayload {
  name: string;
  cpf: string;
  birth_date: string;
  phone: string;
  email: string;
  address: string;
  status: Status;
}

export interface StudentQueryParams extends PageQueryParams {
  search?: string;
  cpf?: string;
  email?: string;
  name?: string;
  status?: Status;
}
