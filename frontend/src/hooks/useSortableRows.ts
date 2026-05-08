import { useMemo, useState } from "react";
import type { Column } from "../components/DataTable";

export function useSortableRows<T>(rows: T[], columns: Column<T>[]): {
  rows: T[];
  sortKey: string | null;
  sortDirection: "asc" | "desc";
  setSortKey: (key: string) => void;
} {
  const [sortKey, setCurrentSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const sortedRows = useMemo(() => {
    if (sortKey === null) {
      return rows;
    }
    const column = columns.find((item) => item.key === sortKey);
    if (column?.sortValue === undefined) {
      return rows;
    }
    return [...rows].sort((left, right) => {
      const leftValue = column.sortValue?.(left) ?? "";
      const rightValue = column.sortValue?.(right) ?? "";
      const result = typeof leftValue === "number" && typeof rightValue === "number"
        ? leftValue - rightValue
        : String(leftValue).localeCompare(String(rightValue));
      return sortDirection === "asc" ? result : -result;
    });
  }, [columns, rows, sortDirection, sortKey]);

  function setSortKey(key: string): void {
    if (key === sortKey) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setCurrentSortKey(key);
    setSortDirection("asc");
  }

  return { rows: sortedRows, sortKey, sortDirection, setSortKey };
}
