import { httpClient } from "./httpClient";
import type { AuthUser } from "../types/auth";
import type { Page, PageQueryParams, Role } from "../types/common";

interface UserQueryParams extends PageQueryParams {
  role?: Role;
  is_active?: boolean;
}

export interface UserCreatePayload {
  email: string;
  full_name: string;
  password: string;
  role: Role;
}

export interface UserUpdatePayload {
  email?: string;
  full_name?: string;
  password?: string;
  role?: Role;
  is_active?: boolean;
}

export interface UserPasswordResetPayload {
  temporary_password: string;
}

export interface UserAuditLog {
  id: number;
  actor_user_id: number | null;
  target_user_id: number | null;
  action: string;
  details: string | null;
  created_at: string;
}

const USER_ENDPOINTS = {
  base: "/api/users",
  audit: "/api/users/audit",
  byId: (userId: number) => `/api/users/${userId}`,
  resetPassword: (userId: number) => `/api/users/${userId}/reset-password`
} as const;

export async function getUsers(params: UserQueryParams = {}): Promise<Page<AuthUser>> {
  const response = await httpClient.get<Page<AuthUser>>(USER_ENDPOINTS.base, { params });
  return response.data;
}

export async function createUser(payload: UserCreatePayload): Promise<AuthUser> {
  const response = await httpClient.post<AuthUser>(USER_ENDPOINTS.base, payload);
  return response.data;
}

export async function updateUser(userId: number, payload: UserUpdatePayload): Promise<AuthUser> {
  const response = await httpClient.put<AuthUser>(USER_ENDPOINTS.byId(userId), payload);
  return response.data;
}

export async function deleteUser(userId: number): Promise<AuthUser> {
  const response = await httpClient.delete<AuthUser>(USER_ENDPOINTS.byId(userId));
  return response.data;
}

export async function resetUserPassword(
  userId: number,
  payload: UserPasswordResetPayload
): Promise<AuthUser> {
  const response = await httpClient.post<AuthUser>(USER_ENDPOINTS.resetPassword(userId), payload);
  return response.data;
}

export async function getUserAuditLogs(params: PageQueryParams & { target_user_id?: number } = {}): Promise<Page<UserAuditLog>> {
  const response = await httpClient.get<Page<UserAuditLog>>(USER_ENDPOINTS.audit, { params });
  return response.data;
}
