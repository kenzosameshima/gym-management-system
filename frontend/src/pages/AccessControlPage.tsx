import { FormEvent, useState } from "react";
import { checkAccess } from "../api/accessApi";
import { ErrorState } from "../components/ErrorState";
import type { AccessDecision } from "../types/access";
import { getErrorMessage } from "./pageUtils";

export function AccessControlPage(): JSX.Element {
  const [cpf, setCpf] = useState("");
  const [decision, setDecision] = useState<AccessDecision | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      setDecision(await checkAccess({ cpf }));
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Access Control</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="panel form-grid" onSubmit={handleSubmit}>
        <input placeholder="CPF" value={cpf} onChange={(event) => setCpf(event.target.value)} required />
        <button type="submit" disabled={isSaving}>{isSaving ? "Checking..." : "Check access"}</button>
      </form>
      {decision !== null && (
        <section className={decision.allowed ? "panel result allowed" : "panel result blocked"}>
          <h2>{decision.allowed ? "Allowed" : "Blocked"}</h2>
          <p>CPF: {decision.cpf_attempted}</p>
          <p>Student: {decision.student_id ?? "-"}</p>
          <p>Reason: {decision.reason ?? "-"}</p>
        </section>
      )}
    </section>
  );
}

