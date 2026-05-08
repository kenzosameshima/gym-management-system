import axios from "axios";

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
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
  return "Unexpected error.";
}

export function formatCurrency(value: string | number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

export function formatDate(value: string | null): string {
  if (value === null || value === "") {
    return "-";
  }
  return new Intl.DateTimeFormat("en-US").format(new Date(`${value}T00:00:00`));
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(value));
}

export const STATUS_OPTIONS = ["ACTIVE", "INACTIVE"] as const;

