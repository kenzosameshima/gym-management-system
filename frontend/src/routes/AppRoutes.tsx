import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "../layouts/AppLayout";
import { AccessControlPage } from "../pages/AccessControlPage";
import { DashboardPage } from "../pages/DashboardPage";
import { EnrollmentsPage } from "../pages/EnrollmentsPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { PaymentsPage } from "../pages/PaymentsPage";
import { PlansPage } from "../pages/PlansPage";
import { ReportsPage } from "../pages/ReportsPage";
import { StudentsPage } from "../pages/StudentsPage";
import { WorkoutPlansPage } from "../pages/WorkoutPlansPage";
import { ProtectedRoute } from "./ProtectedRoute";
import { RoleRoute } from "./RoleRoute";

const MANAGEMENT_ROLES = ["ADMIN", "RECEPTIONIST"] as const;
const WORKOUT_ROLES = ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"] as const;

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/students" element={<StudentsPage />} />
          <Route element={<RoleRoute roles={[...MANAGEMENT_ROLES]} />}>
            <Route path="/plans" element={<PlansPage />} />
            <Route path="/enrollments" element={<EnrollmentsPage />} />
            <Route path="/payments" element={<PaymentsPage />} />
            <Route path="/access-control" element={<AccessControlPage />} />
          </Route>
          <Route element={<RoleRoute roles={[...WORKOUT_ROLES]} />}>
            <Route path="/workouts" element={<WorkoutPlansPage />} />
          </Route>
          <Route path="/reports" element={<ReportsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

