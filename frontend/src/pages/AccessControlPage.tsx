import { FormEvent, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { checkAccess } from "../api/accessApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { PageHeader, PageSection, StatusBadge } from "../components/operational";
import type { AccessDecision } from "../types/access";
import { getErrorMessage } from "./pageUtils";

function accessReasonLabel(reason: AccessDecision["reason"]): string {
  const labels: Record<NonNullable<AccessDecision["reason"]>, string> = {
    STUDENT_NOT_FOUND: "Aluno não encontrado",
    STUDENT_INACTIVE: "Aluno inativo",
    NO_ACTIVE_ENROLLMENT: "Sem matrícula ativa",
    ENROLLMENT_EXPIRED: "Matrícula expirada",
    PAYMENT_OVERDUE: "Pagamento vencido"
  };
  return reason === null ? "Autorizado para entrada" : labels[reason];
}

export function AccessControlPage(): JSX.Element {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [cpf, setCpf] = useState("");
  const [decision, setDecision] = useState<AccessDecision | null>(null);
  const [history, setHistory] = useState<AccessDecision[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function focusInput(): void {
    window.setTimeout(() => inputRef.current?.focus(), 0);
  }

  useEffect(() => {
    focusInput();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const nextCpf = cpf.trim();
    if (nextCpf === "") {
      focusInput();
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const nextDecision = await checkAccess({ cpf: nextCpf });
      setDecision(nextDecision);
      setHistory((current) => [nextDecision, ...current].slice(0, 10));
      setCpf("");
      toast.success(nextDecision.allowed ? "Acesso liberado." : "Acesso bloqueado.");
    } catch (submitError) {
      toast.error("Não foi possível verificar o acesso.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
      focusInput();
    }
  }

  const columns: Column<AccessDecision>[] = [
    { key: "cpf", header: "CPF", render: (item) => item.cpf_attempted },
    {
      key: "result",
      header: "Resultado",
      render: (item) => (
        <StatusBadge tone={item.allowed ? "success" : "danger"}>
          {item.allowed ? "Liberado" : "Bloqueado"}
        </StatusBadge>
      )
    },
    { key: "student", header: "Aluno", render: (item) => item.student_id ?? "-" },
    { key: "reason", header: "Motivo", render: (item) => accessReasonLabel(item.reason) }
  ];

  return (
    <section className="access-kiosk-page">
      <PageHeader
        title="Check-in rápido"
        description="Entrada contínua por CPF, leitor ou teclado. Pressione Enter para validar."
      />
      {error !== null && <ErrorState message={error} />}
      <div className="access-kiosk-layout">
        <main className="access-kiosk-main">
          <form className="panel access-kiosk-form" onSubmit={handleSubmit}>
            <label htmlFor="access-cpf">CPF</label>
            <input
              id="access-cpf"
              ref={inputRef}
              className="access-kiosk-input"
              autoFocus
              inputMode="numeric"
              autoComplete="off"
              placeholder="Digite ou leia o CPF"
              value={cpf}
              onBlur={focusInput}
              onChange={(event) => setCpf(event.target.value)}
              disabled={isSaving}
              required
            />
            <button type="submit" disabled={isSaving}>
              {isSaving ? "Verificando..." : "Validar entrada"}
            </button>
          </form>
          <section
            className={
              decision === null
                ? "panel access-kiosk-result idle"
                : decision.allowed
                  ? "panel access-kiosk-result allowed"
                  : "panel access-kiosk-result blocked"
            }
            role="status"
            aria-live="polite"
          >
            {decision === null ? (
              <>
                <p className="access-result-label">Aguardando leitura</p>
                <h2>Pronto</h2>
                <p>O campo de CPF permanece ativo para operação contínua.</p>
              </>
            ) : (
              <>
                <p className="access-result-label">Resultado</p>
                <h2>{decision.allowed ? "ACESSO LIBERADO" : "ACESSO BLOQUEADO"}</h2>
                <dl className="access-result-details">
                  <div><dt>CPF</dt><dd>{decision.cpf_attempted}</dd></div>
                  <div><dt>Aluno</dt><dd>{decision.student_id ?? "-"}</dd></div>
                  <div><dt>Motivo</dt><dd>{accessReasonLabel(decision.reason)}</dd></div>
                </dl>
              </>
            )}
          </section>
        </main>
        <aside className="access-kiosk-recent">
          <PageSection title="Últimos check-ins" description="Histórico desta sessão.">
            <DataTable
              columns={columns}
              rows={history}
              getRowKey={(item) => `${item.cpf_attempted}-${item.reason ?? "allowed"}-${history.indexOf(item)}`}
              emptyMessage="Nenhum check-in nesta sessão."
            />
          </PageSection>
        </aside>
      </div>
    </section>
  );
}
