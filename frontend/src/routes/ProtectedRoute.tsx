import { Navigate, Outlet, useLocation } from "react-router-dom";
import { LoadingState } from "../components/LoadingState";
import { useAuth } from "../contexts/AuthContext";

export function ProtectedRoute(): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingState message="Verificando sessao..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
