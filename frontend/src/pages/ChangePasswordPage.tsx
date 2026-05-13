import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { Navigate, useNavigate } from "react-router-dom";
import { ROLE_HOME_PATH } from "../auth/roleAccess";
import { ErrorState } from "../components/ErrorState";
import { useAuth } from "../contexts/AuthContext";
import { getErrorMessage } from "./pageUtils";

export function ChangePasswordPage(): JSX.Element {
  const { changePassword, user } = useAuth();
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (user !== null && !user.must_change_password) {
    return <Navigate to={ROLE_HOME_PATH[user.role]} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);
    if (newPassword !== confirmPassword) {
      setError("A nova senha e a confirmacao devem ser iguais.");
      return;
    }

    setIsSaving(true);
    try {
      const updatedUser = await changePassword(currentPassword, newPassword);
      toast.success("Senha alterada.");
      navigate(ROLE_HOME_PATH[updatedUser.role], { replace: true });
    } catch (submitError) {
      toast.error("Nao foi possivel alterar a senha.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="login-shell">
      <form className="panel login-panel" onSubmit={handleSubmit}>
        <div>
          <p className="eyebrow">Senha temporaria</p>
          <h1>Definir nova senha</h1>
        </div>
        {error !== null && <ErrorState message={error} />}
        <label>
          Senha atual
          <input
            type="password"
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
            required
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            minLength={8}
            required
          />
        </label>
        <label>
          Confirmar nova senha
          <input
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            minLength={8}
            required
          />
        </label>
        <button type="submit" disabled={isSaving}>
          {isSaving ? "Salvando..." : "Alterar senha"}
        </button>
      </form>
    </main>
  );
}
