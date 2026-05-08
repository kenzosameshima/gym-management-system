import { httpClient } from "./httpClient";
import type { AuthUser, LoginRequest, TokenResponse } from "../types/auth";

const AUTH_ENDPOINTS = {
  login: "/api/auth/login",
  me: "/api/auth/me"
} as const;

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const response = await httpClient.post<TokenResponse>(AUTH_ENDPOINTS.login, payload);
  return response.data;
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await httpClient.get<AuthUser>(AUTH_ENDPOINTS.me);
  return response.data;
}

