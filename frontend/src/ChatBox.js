import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8001';

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const appendAssistantMessage = (payload) => {
    const text = payload.answer || payload.message || 'No answer returned.';
    setMessages((current) => [
      ...current,
      {
        role: 'assistant',
        text,
        score: payload.score,
        sources: payload.sources || [],
        routeSource: payload.route_source,
        retrievalMode: payload.retrieval_mode,
        validationPassed: payload.validation_passed,
        validationScore: payload.validation_score,
        validationReason: payload.validation_reason,
      },
    ]);
  };

  const send = async () => {
    if (!query) return;
    const userMsg = { role: 'user', text: query };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    try {
      const resp = await axios.post(`${API_BASE_URL}/query`, { query });
      appendAssistantMessage(resp.data);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          text: 'Error contacting backend. Make sure the Python server is running on port 8001.',
          sources: [],
          validationPassed: false,
        },
      ]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  return (
    <div className="chat-shell">
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="message-label">{m.role === 'user' ? 'You' : 'Assistant'}</div>
            <div className="message-text">{m.text}</div>
            {m.role === 'assistant' && (
              <div className="message-meta">
                <span>Score: {typeof m.score === 'number' ? m.score.toFixed(2) : '0.00'}</span>
                <span>Route: {m.routeSource || 'unknown'}</span>
                <span>Grounded: {m.validationPassed ? 'yes' : 'no'}</span>
                {m.validationReason && <span>{m.validationReason}</span>}
                {Array.isArray(m.sources) && m.sources.length > 0 && <span>Sources: {m.sources.join(', ')}</span>}
              </div>
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask your academic question..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              send();
            }
          }}
        />
        <button className="primary-button" onClick={send} disabled={loading} type="button">
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
