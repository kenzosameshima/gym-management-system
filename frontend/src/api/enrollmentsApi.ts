import { httpClient } from "./httpClient";
import type {
  Enrollment,
  EnrollmentCreatePayload,
  EnrollmentQueryParams,
  EnrollmentUpdatePayload
} from "../types/enrollment";
import type { Page } from "../types/common";

const ENROLLMENT_ENDPOINTS = {
  base: "/api/enrollments",
  byId: (enrollmentId: number) => `/api/enrollments/${enrollmentId}`
} as const;

export async function getEnrollments(params: EnrollmentQueryParams = {}): Promise<Page<Enrollment>> {
  const response = await httpClient.get<Page<Enrollment>>(ENROLLMENT_ENDPOINTS.base, { params });
  return response.data;
}

export async function createEnrollment(payload: EnrollmentCreatePayload): Promise<Enrollment> {
  const response = await httpClient.post<Enrollment>(ENROLLMENT_ENDPOINTS.base, payload);
  return response.data;
}

export async function updateEnrollment(
  enrollmentId: number,
  payload: EnrollmentUpdatePayload
): Promise<Enrollment> {
  const response = await httpClient.put<Enrollment>(ENROLLMENT_ENDPOINTS.byId(enrollmentId), payload);
  return response.data;
}

export async function cancelEnrollment(enrollmentId: number): Promise<Enrollment> {
  const response = await httpClient.delete<Enrollment>(ENROLLMENT_ENDPOINTS.byId(enrollmentId));
  return response.data;
}

