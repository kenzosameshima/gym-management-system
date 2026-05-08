interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Loading..." }: LoadingStateProps): JSX.Element {
  return <div className="state state-loading">{message}</div>;
}

