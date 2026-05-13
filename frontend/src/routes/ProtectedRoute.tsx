import { Navigate, Outlet, useLocation } from "react-router-dom";
import { LoadingState } from "../components/LoadingState";
import { useAuth } from "../contexts/AuthContext";

export function ProtectedRoute(): JSX.Element {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingState message="Verificando sessao..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (user?.must_change_password === true && location.pathname !== "/change-password") {
    return <Navigate to="/change-password" replace />;
  }

  return <Outlet />;
}
