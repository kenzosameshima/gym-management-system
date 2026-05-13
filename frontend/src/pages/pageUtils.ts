import axios from "axios";

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === "ECONNABORTED") {
      return "A operacao demorou demais. Verifique a conexao e tente novamente.";
    }
    if (error.response === undefined) {
      return "Nao foi possivel conectar ao servidor. Verifique a API e tente novamente.";
    }
    if (error.response.status === 401) {
      return "Sua sessao expirou. Entre novamente.";
    }
    if (error.response.status === 403) {
      return "Voce nao tem permissao para executar esta acao.";
    }
    const detail = error.response?.data;
    if (typeof detail === "object" && detail !== null && "message" in detail) {
      return String(detail.message);
    }
    if (typeof detail === "object" && detail !== null && "detail" in detail) {
      return String(detail.detail);
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Erro inesperado.";
}

export function formatCurrency(value: string | number): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value));
}

export function formatDate(value: string | null): string {
  if (value === null || value === "") {
    return "-";
  }
  return new Intl.DateTimeFormat("pt-BR").format(new Date(`${value}T00:00:00`));
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value));
}

export function formatFinancialStatus(value: string): string {
  const labels: Record<string, string> = {
    IN_GOOD_STANDING: "Em dia",
    DEFAULTER: "Inadimplente",
    NO_ACTIVE_ENROLLMENT: "Sem matricula ativa",
    INACTIVE: "Inativo",
    ACTIVE: "Ativo",
    PENDING: "Pendente",
    PAID: "Pago",
    OVERDUE: "Vencido",
    EXPIRED: "Expirado",
    CANCELLED: "Cancelado"
  };
  return labels[value] ?? value;
}

export const STATUS_OPTIONS = ["ACTIVE", "INACTIVE"] as const;
