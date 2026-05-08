import { Outlet } from "react-router-dom";
import { Navigation } from "../components/Navigation";

export function AppLayout(): JSX.Element {
  return (
    <div className="app-frame">
      <Navigation />
      <main className="content-shell">
        <Outlet />
      </main>
    </div>
  );
}

