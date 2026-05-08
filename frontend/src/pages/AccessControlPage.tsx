import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { checkAccess } from "../api/accessApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import type { AccessDecision } from "../types/access";
import { getErrorMessage } from "./pageUtils";

export function AccessControlPage(): JSX.Element {
  const [cpf, setCpf] = useState("");
  const [decision, setDecision] = useState<AccessDecision | null>(null);
  const [history, setHistory] = useState<AccessDecision[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      const nextDecision = await checkAccess({ cpf });
      setDecision(nextDecision);
      setHistory((current) => [nextDecision, ...current].slice(0, 10));
      toast.success(nextDecision.allowed ? "Access allowed." : "Access blocked.");
    } catch (submitError) {
      toast.error("Access check failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }
  const columns: Column<AccessDecision>[] = [
    { key: "cpf", header: "CPF", render: (item) => item.cpf_attempted },
    { key: "result", header: "Result", render: (item) => item.allowed ? "Allowed" : "Blocked" },
    { key: "student", header: "Student", render: (item) => item.student_id ?? "-" },
    { key: "reason", header: "Reason", render: (item) => item.reason ?? "-" }
  ];

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Access Control</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="panel access-form" onSubmit={handleSubmit}>
        <label>CPF<input className="access-input" autoFocus placeholder="Type CPF and press Enter" value={cpf} onChange={(event) => setCpf(event.target.value)} required /></label>
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
      <section className="page-stack">
        <h2>Recent checks</h2>
        <DataTable columns={columns} rows={history} getRowKey={(item) => `${item.cpf_attempted}-${item.reason ?? "allowed"}-${history.indexOf(item)}`} emptyMessage="No checks in this session." />
      </section>
    </section>
  );
}
