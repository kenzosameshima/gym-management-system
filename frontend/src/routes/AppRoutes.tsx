import { lazy, Suspense } from "react";
import type React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { LoadingState } from "../components/LoadingState";
import { AppLayout } from "../layouts/AppLayout";
import { AccessControlPage } from "../pages/AccessControlPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { PlansPage } from "../pages/PlansPage";
import { StudentWorkspacePage } from "../pages/StudentWorkspacePage";
import { ProtectedRoute } from "./ProtectedRoute";
import { RoleRoute } from "./RoleRoute";

const MANAGEMENT_ROLES = ["ADMIN", "RECEPTIONIST"] as const;
const WORKOUT_ROLES = ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"] as const;
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
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<LazyPage><DashboardPage /></LazyPage>} />
          <Route path="/students" element={<StudentWorkspacePage />} />
          <Route element={<RoleRoute roles={[...MANAGEMENT_ROLES]} />}>
            <Route path="/plans" element={<PlansPage />} />
            <Route path="/enrollments" element={<LazyPage><EnrollmentsPage /></LazyPage>} />
            <Route path="/payments" element={<LazyPage><PaymentsPage /></LazyPage>} />
            <Route path="/access-control" element={<AccessControlPage />} />
          </Route>
          <Route element={<RoleRoute roles={[...WORKOUT_ROLES]} />}>
            <Route path="/workouts" element={<LazyPage><WorkoutPlansPage /></LazyPage>} />
          </Route>
          <Route path="/reports" element={<LazyPage><ReportsPage /></LazyPage>} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
