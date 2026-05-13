import { lazy, Suspense } from "react";
import type React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { LoadingState } from "../components/LoadingState";
import { AppLayout } from "../layouts/AppLayout";
import { AccessControlPage } from "../pages/AccessControlPage";
import { ChangePasswordPage } from "../pages/ChangePasswordPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { PlansPage } from "../pages/PlansPage";
import { StudentWorkspacePage } from "../pages/StudentWorkspacePage";
import { ADMIN_ROLES, ALL_STAFF_ROLES, OPERATIONS_ROLES, WORKOUT_ROLES } from "../auth/roleAccess";
import { ProtectedRoute } from "./ProtectedRoute";
import { RoleRoute } from "./RoleRoute";

const DashboardPage = lazy(() =>
  import("../pages/RoleDashboardPage").then((module) => ({ default: module.RoleDashboardPage }))
);
const EnrollmentsPage = lazy(() =>
  import("../pages/EnrollmentsPage").then((module) => ({ default: module.EnrollmentsPage }))
);
const PaymentsPage = lazy(() =>
  import("../pages/PaymentsPage").then((module) => ({ default: module.PaymentsPage }))
);
const ReportsPage = lazy(() =>
  import("../pages/ReportsPage").then((module) => ({ default: module.ReportsPage }))
);
const TeamPage = lazy(() =>
  import("../pages/TeamPage").then((module) => ({ default: module.TeamPage }))
);
const WorkoutPlansPage = lazy(() =>
  import("../pages/WorkoutPlansPage").then((module) => ({ default: module.WorkoutPlansPage }))
);

function LazyPage({ children }: { children: React.ReactNode }): JSX.Element {
  return <Suspense fallback={<LoadingState message="Carregando tela..." />}>{children}</Suspense>;
}

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<LazyPage><DashboardPage /></LazyPage>} />
          <Route element={<RoleRoute roles={ALL_STAFF_ROLES} />}>
            <Route path="/students" element={<StudentWorkspacePage />} />
            <Route path="/reports" element={<LazyPage><ReportsPage /></LazyPage>} />
          </Route>
          <Route element={<RoleRoute roles={OPERATIONS_ROLES} />}>
            <Route path="/enrollments" element={<LazyPage><EnrollmentsPage /></LazyPage>} />
            <Route path="/payments" element={<LazyPage><PaymentsPage /></LazyPage>} />
            <Route path="/access-control" element={<AccessControlPage />} />
            <Route path="/plans" element={<PlansPage />} />
          </Route>
          <Route element={<RoleRoute roles={ADMIN_ROLES} />}>
            <Route path="/team" element={<LazyPage><TeamPage /></LazyPage>} />
          </Route>
          <Route element={<RoleRoute roles={WORKOUT_ROLES} />}>
            <Route path="/workouts" element={<LazyPage><WorkoutPlansPage /></LazyPage>} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
