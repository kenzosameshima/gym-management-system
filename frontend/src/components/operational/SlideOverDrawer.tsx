import { useEffect, useRef } from "react";
import type React from "react";

interface SlideOverDrawerProps {
  isOpen: boolean;
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  description?: string;
  footer?: React.ReactNode;
}

export function SlideOverDrawer({
  isOpen,
  title,
  description,
  children,
  footer,
  onClose
}: SlideOverDrawerProps): JSX.Element | null {
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    closeButtonRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent): void {
      if (event.key === "Escape") {
        onCloseRef.current();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="drawer-layer" role="presentation">
      <button
        type="button"
        className="drawer-backdrop"
        aria-label="Fechar painel"
        onClick={onClose}
      />
      <aside
        className="slide-over-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        aria-describedby={description !== undefined ? "drawer-description" : undefined}
      >
        <header className="drawer-header">
          <div>
            <h2 id="drawer-title">{title}</h2>
            {description !== undefined && <p id="drawer-description">{description}</p>}
          </div>
          <button
            type="button"
            className="secondary"
            ref={closeButtonRef}
            onClick={onClose}
          >
            Fechar
          </button>
        </header>
        <div className="drawer-body">{children}</div>
        {footer !== undefined && <footer className="drawer-footer">{footer}</footer>}
      </aside>
    </div>
  );
}
