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
      toast.success("Signed in.");
      navigate(redirectTo, { replace: true });
    } catch (submitError) {
      toast.error("Sign in failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="login-shell">
      <form className="panel login-panel" onSubmit={handleSubmit}>
        <div>
          <p className="eyebrow">Gym Management System</p>
          <h1>Sign in</h1>
        </div>
        {error !== null && <ErrorState message={error} />}
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={isSaving}>
          {isSaving ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
