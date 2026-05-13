import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import type { Role } from "../types/common";

interface NavItem {
  to: string;
  label: string;
  roles: Role[];
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const ROLE_LABELS: Record<Role, string> = {
  ADMIN: "Administrador",
  RECEPTIONIST: "Recepcao",
  INSTRUCTOR: "Instrutor"
};

const NAV_SECTIONS: NavSection[] = [
  {
    title: "OPERAÇÕES",
    items: [
      {
        to: "/access-control",
        label: "Check-in",
        roles: ["ADMIN", "RECEPTIONIST"]
      },
      {
        to: "/students",
        label: "Alunos",
        roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"]
      },
      {
        to: "/payments",
        label: "Pagamentos",
        roles: ["ADMIN", "RECEPTIONIST"]
      },
      {
        to: "/enrollments",
        label: "Matrículas e renovações",
        roles: ["ADMIN", "RECEPTIONIST"]
      }
    ]
  },
  {
    title: "TREINAMENTO",
    items: [
      {
        to: "/workouts",
        label: "Treinos e evolução",
        roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"]
      }
    ]
  },
  {
    title: "GESTÃO",
    items: [
      {
        to: "/dashboard",
        label: "Painel operacional",
        roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"]
      },
      {
        to: "/reports",
        label: "Relatórios",
        roles: ["ADMIN", "RECEPTIONIST", "INSTRUCTOR"]
      },
      {
        to: "/plans",
        label: "Planos",
        roles: ["ADMIN", "RECEPTIONIST"]
      }
    ]
  }
];

export function Navigation(): JSX.Element {
  const { user, logout } = useAuth();
  const visibleSections = NAV_SECTIONS.map((section) => ({
    ...section,
    items: section.items.filter((item) => user !== null && item.roles.includes(user.role))
  })).filter((section) => section.items.length > 0);

  return (
    <aside className="sidebar">
      <div className="brand">
        <strong>Gestao da Academia</strong>
        <span>{user === null ? "" : ROLE_LABELS[user.role]}</span>
      </div>
      <nav className="sidebar-nav" aria-label="Navegacao principal">
        {visibleSections.map((section) => (
          <section className="nav-section" key={section.title}>
            {section.title !== "" && <p className="nav-section-title">{section.title}</p>}
            <div className="nav-section-links">
              {section.items.map((item) => (
                <NavLink key={item.to} to={item.to}>
                  <span className="nav-label">{item.label}</span>
                </NavLink>
              ))}
            </div>
          </section>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span>{user === null ? "" : ROLE_LABELS[user.role]}</span>
        <button type="button" className="secondary" onClick={logout}>
          Sair
        </button>
      </div>
    </aside>
  );
}
