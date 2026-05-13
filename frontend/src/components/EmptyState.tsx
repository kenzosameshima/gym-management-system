interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps): JSX.Element {
  return <div className="state state-empty" role="status">{message}</div>;
}
