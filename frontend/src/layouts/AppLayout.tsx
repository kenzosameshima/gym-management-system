import { FormEvent, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { Navigation } from "../components/Navigation";

function OperationalTopbar(): JSX.Element {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  function handleSearch(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const nextQuery = query.trim();
    navigate(nextQuery === "" ? "/students" : `/students?search=${encodeURIComponent(nextQuery)}`);
  }

  return (
    <header className="topbar">
      <form className="global-search" role="search" onSubmit={handleSearch}>
        <label htmlFor="global-search">Busca rapida</label>
        <input
          id="global-search"
          placeholder="Buscar aluno por nome, CPF ou e-mail"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </form>
      <nav className="quick-actions" aria-label="Acoes rapidas">
        <Link to="/access-control">Check-in rapido</Link>
        <Link to="/enrollments">Nova matricula</Link>
        <Link to="/payments">Receber mensalidade</Link>
        <Link to="/workouts">Ficha de treino</Link>
      </nav>
    </header>
  );
}

export function AppLayout(): JSX.Element {
  return (
    <div className="app-frame">
      <Navigation />
      <main className="content-shell">
        <OperationalTopbar />
        <Outlet />
      </main>
    </div>
  );
}
