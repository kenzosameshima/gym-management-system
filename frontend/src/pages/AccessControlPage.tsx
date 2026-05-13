import { FormEvent, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { checkAccessByStudentId } from "../api/accessApi";
import { searchStudents } from "../api/studentsApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { PageHeader, PageSection, StatusBadge } from "../components/operational";
import type { AccessDecision } from "../types/access";
import type { StudentSearchResult } from "../types/student";
import { formatDateTime, formatFinancialStatus, getErrorMessage } from "./pageUtils";

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

type AccessHistoryItem = AccessDecision & {
  checked_at: string;
};

function financialStatusTone(status: StudentSearchResult["financial_status"]): "success" | "warning" | "danger" | "neutral" {
  if (status === "IN_GOOD_STANDING") {
    return "success";
  }
  if (status === "DEFAULTER") {
    return "danger";
  }
  if (status === "NO_ACTIVE_ENROLLMENT") {
    return "warning";
  }
  return "neutral";
}

export function AccessControlPage(): JSX.Element {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<StudentSearchResult[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<StudentSearchResult | null>(null);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const [decision, setDecision] = useState<AccessDecision | null>(null);
  const [history, setHistory] = useState<AccessHistoryItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function focusInput(): void {
    window.setTimeout(() => inputRef.current?.focus(), 0);
  }

  useEffect(() => {
    focusInput();
  }, []);

  useEffect(() => {
    const nextQuery = query.trim();
    if (selectedStudent !== null || nextQuery.length < 2) {
      setSuggestions([]);
      setIsSearching(false);
      return undefined;
    }

    let isCurrent = true;
    setIsSearching(true);
    const timeoutId = window.setTimeout(() => {
      void searchStudents({ q: nextQuery, limit: 8 })
        .then((items) => {
          if (isCurrent) {
            setSuggestions(items);
            setHighlightedIndex(0);
          }
        })
        .catch((searchError) => {
          if (isCurrent) {
            setError(getErrorMessage(searchError));
            setSuggestions([]);
          }
        })
        .finally(() => {
          if (isCurrent) {
            setIsSearching(false);
          }
        });
    }, 180);

    return () => {
      isCurrent = false;
      window.clearTimeout(timeoutId);
    };
  }, [query, selectedStudent]);

  function selectStudent(student: StudentSearchResult): void {
    setSelectedStudent(student);
    setQuery(student.name);
    setSuggestions([]);
    setDecision(null);
    setError(null);
  }

  function clearSelection(): void {
    setSelectedStudent(null);
    setDecision(null);
    setQuery("");
    setSuggestions([]);
    focusInput();
  }

  async function performCheckIn(student: StudentSearchResult): Promise<void> {
    setIsSaving(true);
    setError(null);
    try {
      const nextDecision = await checkAccessByStudentId(student.id);
      setDecision(nextDecision);
      setHistory((current) => [
        { ...nextDecision, checked_at: new Date().toISOString() },
        ...current
      ].slice(0, 8));
      toast.success(nextDecision.allowed ? "Entrada liberada." : "Entrada bloqueada.");
    } catch (submitError) {
      toast.error("Nao foi possivel verificar o acesso.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
      focusInput();
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (selectedStudent !== null) {
      await performCheckIn(selectedStudent);
      return;
    }
    if (suggestions.length > 0) {
      selectStudent(suggestions[Math.min(highlightedIndex, suggestions.length - 1)]);
      return;
    }
    if (query.trim() === "") {
      focusInput();
      return;
    }
    toast.error("Selecione um aluno da busca para realizar o check-in.");
  }

  const columns: Column<AccessHistoryItem>[] = [
    { key: "checked_at", header: "Hora", render: (item) => formatDateTime(item.checked_at) },
    { key: "student", header: "Aluno", render: (item) => item.student_name ?? "Não identificado" },
    {
      key: "result",
      header: "Resultado",
      render: (item) => (
        <StatusBadge tone={item.allowed ? "success" : "danger"}>
          {item.allowed ? "Liberado" : "Bloqueado"}
        </StatusBadge>
      )
    },
    { key: "reason", header: "Motivo", render: (item) => accessReasonLabel(item.reason) }
  ];

  return (
    <section className="access-kiosk-page">
      <PageHeader
        title="Check-in rápido"
        description="Busque o aluno e registre a entrada em poucos cliques."
      />
      {error !== null && <ErrorState message={error} />}
      <div className="access-kiosk-layout">
        <main className="access-kiosk-main">
          <form className="panel access-kiosk-form" onSubmit={handleSubmit}>
            <label htmlFor="access-search">Buscar aluno</label>
            <input
              id="access-search"
              ref={inputRef}
              className="access-kiosk-input"
              autoFocus
              autoComplete="off"
              placeholder="Nome, CPF, telefone ou matrícula"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setSelectedStudent(null);
                setDecision(null);
              }}
              onKeyDown={(event) => {
                if (event.key === "ArrowDown" && suggestions.length > 0) {
                  event.preventDefault();
                  setHighlightedIndex((current) => Math.min(current + 1, suggestions.length - 1));
                }
                if (event.key === "ArrowUp" && suggestions.length > 0) {
                  event.preventDefault();
                  setHighlightedIndex((current) => Math.max(current - 1, 0));
                }
              }}
              disabled={isSaving}
              required
            />
            <button type="submit" disabled={isSaving || isSearching}>
              {isSaving ? "Registrando..." : selectedStudent === null ? "Selecionar" : "Realizar check-in"}
            </button>
            {suggestions.length > 0 && (
              <div className="access-suggestions" role="listbox" aria-label="Sugestoes de alunos">
                {suggestions.map((student, index) => (
                  <button
                    key={student.id}
                    type="button"
                    className={index === highlightedIndex ? "active" : ""}
                    onClick={() => selectStudent(student)}
                    role="option"
                    aria-selected={index === highlightedIndex}
                  >
                    <strong>{student.name}</strong>
                    <span>{student.cpf} · {student.phone}</span>
                  </button>
                ))}
              </div>
            )}
            {isSearching && <p className="access-search-hint">Buscando alunos...</p>}
          </form>
          {selectedStudent !== null && (
            <section className="panel access-student-card" aria-label="Aluno selecionado">
              <div>
                <span className="access-result-label">Aluno selecionado</span>
                <h2>{selectedStudent.name}</h2>
                <p>{selectedStudent.cpf} · {selectedStudent.phone}</p>
              </div>
              <div className="access-student-statuses">
                <div>
                  <span>Plano</span>
                  <StatusBadge tone={financialStatusTone(selectedStudent.financial_status)}>
                    {formatFinancialStatus(selectedStudent.financial_status)}
                  </StatusBadge>
                </div>
                <div>
                  <span>Acesso</span>
                  <StatusBadge tone={decision === null ? "neutral" : decision.allowed ? "success" : "danger"}>
                    {decision === null ? "Aguardando check-in" : decision.allowed ? "Liberado" : "Bloqueado"}
                  </StatusBadge>
                </div>
              </div>
              <div className="access-student-actions">
                <button type="button" onClick={() => void performCheckIn(selectedStudent)} disabled={isSaving}>
                  {isSaving ? "Registrando..." : "Realizar check-in"}
                </button>
                <button type="button" className="secondary" onClick={clearSelection} disabled={isSaving}>Trocar aluno</button>
              </div>
            </section>
          )}
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
                <p className="access-result-label">Operacao</p>
                <h2>Pronto para check-in</h2>
                <p>Pesquise e selecione um aluno para registrar a entrada.</p>
              </>
            ) : (
              <>
                <p className="access-result-label">Resultado</p>
                <h2>{decision.allowed ? "Entrada liberada" : "Entrada bloqueada"}</h2>
                <dl className="access-result-details">
                  <div><dt>Aluno</dt><dd>{decision.student_name ?? "Não identificado"}</dd></div>
                  <div><dt>Motivo</dt><dd>{accessReasonLabel(decision.reason)}</dd></div>
                </dl>
              </>
            )}
          </section>
        </main>
        <aside className="access-kiosk-recent">
          <PageSection title="Últimos check-ins" description="Historico desta sessao.">
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
