interface ErrorStateProps {
  message: string;
}

export function ErrorState({ message }: ErrorStateProps): JSX.Element {
  return <div className="state state-error">{message}</div>;
}

