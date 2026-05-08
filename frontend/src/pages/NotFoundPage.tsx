import { Link } from "react-router-dom";

export function NotFoundPage(): JSX.Element {
  return (
    <main className="login-shell">
      <section className="panel login-panel">
        <h1>Page not found</h1>
        <Link to="/dashboard">Return to dashboard</Link>
      </section>
    </main>
  );
}

