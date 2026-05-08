import { httpClient } from "./httpClient";
import type { AccessCheckRequest, AccessDecision } from "../types/access";

const ACCESS_ENDPOINTS = {
  check: "/api/access-control/check"
} as const;

export async function checkAccess(payload: AccessCheckRequest): Promise<AccessDecision> {
  const response = await httpClient.post<AccessDecision>(ACCESS_ENDPOINTS.check, payload);
  return response.data;
}

