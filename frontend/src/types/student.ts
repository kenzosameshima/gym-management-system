import type { PageQueryParams, Status } from "./common";

export interface Student {
  id: number;
  name: string;
  cpf: string;
  birth_date: string;
  phone: string | null;
  email: string;
  address: string | null;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface StudentPayload {
  name: string;
  cpf: string;
  birth_date: string;
  phone?: string | null;
  email: string;
  address?: string | null;
  status: Status;
}

export interface StudentQueryParams extends PageQueryParams {
  search?: string;
  cpf?: string;
  email?: string;
  name?: string;
  status?: Status;
}
