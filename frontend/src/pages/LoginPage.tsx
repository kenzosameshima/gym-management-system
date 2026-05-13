import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { Navigate, useNavigate } from "react-router-dom";
import { ROLE_HOME_PATH } from "../auth/roleAccess";
import { ErrorState } from "../components/ErrorState";
import { useAuth } from "../contexts/AuthContext";
import { getErrorMessage } from "./pageUtils";

export function LoginPage(): JSX.Element {
  const { isAuthenticated, login, user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to={user === null ? "/dashboard" : ROLE_HOME_PATH[user.role]} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      const currentUser = await login({ email, password });
      toast.success("Entrada realizada.");
      navigate(ROLE_HOME_PATH[currentUser.role], { replace: true });
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
