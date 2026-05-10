import { httpClient } from "./httpClient";
import type { AuthUser } from "../types/auth";
import type { Page, PageQueryParams, Role } from "../types/common";

interface UserQueryParams extends PageQueryParams {
  role?: Role;
}

const USER_ENDPOINTS = {
  base: "/api/users"
} as const;

export async function getUsers(params: UserQueryParams = {}): Promise<Page<AuthUser>> {
  const response = await httpClient.get<Page<AuthUser>>(USER_ENDPOINTS.base, { params });
  return response.data;
}
