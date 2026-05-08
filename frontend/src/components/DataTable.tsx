import type React from "react";
import { EmptyState } from "./EmptyState";
import { LoadingState } from "./LoadingState";

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  sortValue?: (row: T) => string | number;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  getRowKey: (row: T) => string | number;
  emptyMessage: string;
  isLoading?: boolean;
  total?: number;
  limit?: number;
  offset?: number;
  onPageChange?: (offset: number) => void;
  sortKey?: string | null;
  sortDirection?: "asc" | "desc";
  onSortChange?: (key: string) => void;
}

export function DataTable<T>({
  columns,
  rows,
  getRowKey,
  emptyMessage,
  isLoading = false,
  total,
  limit,
  offset,
  onPageChange,
  sortKey = null,
  sortDirection = "asc",
  onSortChange
}: DataTableProps<T>): JSX.Element {
  if (isLoading) {
    return <LoadingState />;
  }

  if (rows.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  const canPage = total !== undefined && limit !== undefined && offset !== undefined && onPageChange !== undefined;
  const hasPrevious = canPage && offset > 0;
  const hasNext = canPage && offset + limit < total;

  return (
    <div className="data-table-stack">
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>
                  {column.sortValue !== undefined && onSortChange !== undefined ? (
                    <button type="button" className="table-sort" onClick={() => onSortChange(column.key)}>
                      {column.header}
                      {sortKey === column.key ? ` ${sortDirection === "asc" ? "ASC" : "DESC"}` : ""}
                    </button>
                  ) : (
                    column.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={getRowKey(row)}>
                {columns.map((column) => (
                  <td key={column.key}>{column.render(row)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {canPage && (
        <div className="pagination">
          <span>
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
          </span>
          <div className="row-actions">
            <button type="button" className="secondary" disabled={!hasPrevious} onClick={() => onPageChange(Math.max(0, offset - limit))}>
              Previous
            </button>
            <button type="button" className="secondary" disabled={!hasNext} onClick={() => onPageChange(offset + limit)}>
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
