export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface PageQueryParams {
  limit?: number;
  offset?: number;
}

export type Role = "ADMIN" | "RECEPTIONIST" | "INSTRUCTOR";
export type Status = "ACTIVE" | "INACTIVE";

