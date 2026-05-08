import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import type { Role } from "../types/common";

interface NavItem {
  to: string;
  label: string;
  roles: Role[];
}

const NAV_ITEMS: NavItem[] = [
  { to: "/dashboard", label: "Dashboard", roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"] },
  { to: "/students", label: "Students", roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"] },
  { to: "/plans", label: "Plans", roles: ["ADMIN", "RECEPTIONIST"] },
  { to: "/enrollments", label: "Enrollments", roles: ["ADMIN", "RECEPTIONIST"] },
  { to: "/payments", label: "Payments", roles: ["ADMIN", "RECEPTIONIST"] },
  { to: "/access-control", label: "Access Control", roles: ["ADMIN", "RECEPTIONIST"] },
  { to: "/workouts", label: "Workouts", roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"] },
  { to: "/reports", label: "Reports", roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"] }
];

export function Navigation(): JSX.Element {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="brand">
        <strong>Gym Management</strong>
        <span>{user?.role}</span>
      </div>
      <nav>
        {NAV_ITEMS.filter((item) => user !== null && item.roles.includes(user.role)).map((item) => (
          <NavLink key={item.to} to={item.to}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span>{user?.full_name}</span>
        <button type="button" className="secondary" onClick={logout}>
          Logout
        </button>
      </div>
    </aside>
  );
}

