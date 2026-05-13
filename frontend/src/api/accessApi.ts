import { httpClient } from "./httpClient";
import type { AccessCheckRequest, AccessDecision, AccessLog } from "../types/access";
import type { Page } from "../types/common";

const ACCESS_ENDPOINTS = {
  check: "/api/access-control/check",
  logs: "/api/access/logs"
} as const;

export async function checkAccess(payload: AccessCheckRequest): Promise<AccessDecision> {
  const response = await httpClient.post<AccessDecision>(ACCESS_ENDPOINTS.check, payload);
  return response.data;
}

export async function getAccessLogs(params: { limit?: number; offset?: number } = {}): Promise<Page<AccessLog>> {
  const response = await httpClient.get<Page<AccessLog>>(ACCESS_ENDPOINTS.logs, { params });
  return response.data;
}
