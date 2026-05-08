import { httpClient } from "./httpClient";
import type { Page } from "../types/common";
import type { Student, StudentPayload, StudentQueryParams } from "../types/student";

const STUDENT_ENDPOINTS = {
  base: "/api/students",
  byId: (studentId: number) => `/api/students/${studentId}`
} as const;

export async function getStudents(params: StudentQueryParams = {}): Promise<Page<Student>> {
  const response = await httpClient.get<Page<Student>>(STUDENT_ENDPOINTS.base, { params });
  return response.data;
}

export async function createStudent(payload: StudentPayload): Promise<Student> {
  const response = await httpClient.post<Student>(STUDENT_ENDPOINTS.base, payload);
  return response.data;
}

export async function updateStudent(studentId: number, payload: Partial<StudentPayload>): Promise<Student> {
  const response = await httpClient.put<Student>(STUDENT_ENDPOINTS.byId(studentId), payload);
  return response.data;
}

export async function deleteStudent(studentId: number): Promise<Student> {
  const response = await httpClient.delete<Student>(STUDENT_ENDPOINTS.byId(studentId));
  return response.data;
}

