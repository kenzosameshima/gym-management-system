interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Carregando..." }: LoadingStateProps): JSX.Element {
  return <div className="state state-loading" role="status" aria-live="polite">{message}</div>;
}
