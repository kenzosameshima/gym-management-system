import "./styles/global.css";

function App(): JSX.Element {
  return (
    <main className="app-shell">
      <section className="status-panel" aria-label="Application status">
        <p className="eyebrow">Phase 1</p>
        <h1>Gym Management System</h1>
        <p className="summary">Base full-stack foundation ready for future modules.</p>
      </section>
    </main>
  );
}

export default App;

