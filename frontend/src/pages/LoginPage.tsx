import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ErrorState } from "../components/ErrorState";
import { useAuth } from "../contexts/AuthContext";
import { getErrorMessage } from "./pageUtils";

export function LoginPage(): JSX.Element {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      await login({ email, password });
      const redirectTo = typeof location.state === "object" && location.state !== null && "from" in location.state
        ? "/dashboard"
        : "/dashboard";
      toast.success("Entrada realizada.");
      navigate(redirectTo, { replace: true });
    } catch (submitError) {
      toast.error("Nao foi possivel entrar.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="login-shell">
      <form className="panel login-panel" onSubmit={handleSubmit}>
        <div>
          <p className="eyebrow">Gestao da Academia</p>
          <h1>Entrar</h1>
        </div>
        {error !== null && <ErrorState message={error} />}
        <label>
          E-mail
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={isSaving}>
          {isSaving ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </main>
  );
}
