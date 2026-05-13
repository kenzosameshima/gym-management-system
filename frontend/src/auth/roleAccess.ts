import type { Role } from "../types/common";

export const ADMIN_ROLES: Role[] = ["ADMIN"];
export const OPERATIONS_ROLES: Role[] = ["ADMIN", "RECEPTIONIST"];
export const WORKOUT_ROLES: Role[] = ["ADMIN", "INSTRUCTOR"];
export const ALL_STAFF_ROLES: Role[] = ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"];

export const ROLE_HOME_PATH: Record<Role, string> = {
  ADMIN: "/dashboard",
  RECEPTIONIST: "/students",
  INSTRUCTOR: "/workouts"
};

export function canAccessPlans(role: Role | undefined): boolean {
  return role === "ADMIN" || role === "RECEPTIONIST";
}

export function canManagePlans(role: Role | undefined): boolean {
  return role === "ADMIN";
}
