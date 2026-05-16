import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8001';

export default function Dashboard() {
  const [metrics, setMetrics] = useState({ average_score: 0, average_latency: 0, average_accuracy: 0, total: 0 });
  const [status, setStatus] = useState('Connected');

  useEffect(() => {
    async function load() {
      try {
        const resp = await axios.get(`${API_BASE_URL}/_metrics`);
        setMetrics(resp.data);
        setStatus('Connected');
      } catch (err) {
        setStatus('Backend unavailable');
      }
    }

    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="dashboard-grid">
      <div className="metric-card">
        <span className="metric-label">Average Score</span>
        <strong>{metrics.average_score}</strong>
      </div>
      <div className="metric-card">
        <span className="metric-label">Average Latency</span>
        <strong>{metrics.average_latency}s</strong>
      </div>
      <div className="metric-card">
        <span className="metric-label">Average Accuracy</span>
        <strong>{metrics.average_accuracy}</strong>
      </div>
      <div className="metric-card">
        <span className="metric-label">Total Queries</span>
        <strong>{metrics.total}</strong>
      </div>
      <div className="status-pill">{status}</div>
    </div>
  );
}
