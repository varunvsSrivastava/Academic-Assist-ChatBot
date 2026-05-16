import React from 'react';
import ChatBox from './ChatBox';
import Dashboard from './Dashboard';
import UploadPanel from './UploadPanel';

export default function App() {
  return (
    <div className="app-shell">
      <header className="simple-header">
        <h1>Academic Assistant chatbot</h1>
      </header>

      <main className="layout-grid">
        <section className="panel panel-wide">
          <ChatBox />
        </section>

        <aside className="stack">
          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Upload PDFs</h2>
                <p>Index documents before asking questions.</p>
              </div>
            </div>
            <UploadPanel />
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Dashboard</h2>
                <p>Live metrics from the backend.</p>
              </div>
            </div>
            <Dashboard />
          </section>
        </aside>
      </main>
    </div>
  );
}
