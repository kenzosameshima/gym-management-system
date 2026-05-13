import { Navigate, Outlet } from "react-router-dom";
import { ROLE_HOME_PATH } from "../auth/roleAccess";
import { useAuth } from "../contexts/AuthContext";
import type { Role } from "../types/common";

interface RoleRouteProps {
  roles: Role[];
}

export function RoleRoute({ roles }: RoleRouteProps): JSX.Element {
  const { hasRole, user } = useAuth();

  if (!hasRole(roles)) {
    return <Navigate to={user === null ? "/dashboard" : ROLE_HOME_PATH[user.role]} replace />;
  }

  return <Outlet />;
}
