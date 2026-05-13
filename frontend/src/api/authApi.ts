import { httpClient } from "./httpClient";
import type { AuthUser, ChangePasswordPayload, LoginRequest, TokenResponse } from "../types/auth";

const AUTH_ENDPOINTS = {
  login: "/api/auth/login",
  me: "/api/auth/me",
  changePassword: "/api/auth/change-password"
} as const;

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const response = await httpClient.post<TokenResponse>(AUTH_ENDPOINTS.login, payload);
  return response.data;
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await httpClient.get<AuthUser>(AUTH_ENDPOINTS.me);
  return response.data;
}

export async function changePassword(payload: ChangePasswordPayload): Promise<AuthUser> {
  const response = await httpClient.post<AuthUser>(AUTH_ENDPOINTS.changePassword, payload);
  return response.data;
}
