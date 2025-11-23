import React, { useState } from 'react';
import type { Session, CreateSessionRequest } from '../types';

interface Props {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: (data: CreateSessionRequest) => Promise<void>;
}

const Sidebar: React.FC<Props> = ({ sessions, activeSessionId, onSelectSession, onCreateSession }) => {
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [context, setContext] = useState(''); // New state for context
  const [goal, setGoal] = useState(''); // New state for goal
  const [ownerId, setOwnerId] = useState('sales_agent_001'); // New state for owner_id, with a default
  const [creating, setCreating] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      await onCreateSession({
        name: name,
        phone: phone,
        context: context,
        goal: goal,
        owner_id: ownerId,
      });
      setPhone('');
      setName('');
      setContext('');
      setGoal('');
      // ownerId can persist or reset, depending on UX choice
    } finally {
      setCreating(false);
    }
  }

  return (
    <div style={{
      width: 280,
      background: '#020617',
      borderRight: '1px solid #1f2937',
      padding: '1rem 0.75rem',
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem',
    }}>
      <div
        style={{
          padding: '0.75rem',
          borderRadius: 8,
          background: '#030712',
          border: '1px solid #1f2937',
        }}
      >
        <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Session Setup</div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.2rem', color: '#9ca3af' }}>
            Client Name:
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              style={{ width: '100%', marginTop: 2, padding: '0.25rem 0.4rem', borderRadius: 4, border: '1px solid #1f2937', background: '#020617', color: '#e5e7eb' }}
            />
          </label>
          <label style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.2rem', color: '#9ca3af' }}>
            Client Phone:
            <input
              value={phone}
              onChange={e => setPhone(e.target.value)}
              style={{ width: '100%', marginTop: 2, padding: '0.25rem 0.4rem', borderRadius: 4, border: '1px solid #1f2937', background: '#020617', color: '#e5e7eb' }}
            />
          </label>
          <label style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.2rem', color: '#9ca3af' }}>
            Client Context:
            <textarea
              value={context}
              onChange={e => setContext(e.target.value)}
              rows={2}
              style={{ width: '100%', marginTop: 2, padding: '0.25rem 0.4rem', borderRadius: 4, border: '1px solid #1f2937', background: '#020617', color: '#e5e7eb', resize: 'vertical' }}
            />
          </label>
          <label style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.2rem', color: '#9ca3af' }}>
            Sales Goal:
            <input
              value={goal}
              onChange={e => setGoal(e.target.value)}
              style={{ width: '100%', marginTop: 2, padding: '0.25rem 0.4rem', borderRadius: 4, border: '1px solid #1f2937', background: '#020617', color: '#e5e7eb' }}
            />
          </label>
          <label style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.2rem', color: '#9ca3af' }}>
            Your Agent ID:
            <input
              value={ownerId}
              onChange={e => setOwnerId(e.target.value)}
              style={{ width: '100%', marginTop: 2, padding: '0.25rem 0.4rem', borderRadius: 4, border: '1px solid #1f2937', background: '#020617', color: '#e5e7eb' }}
            />
          </label>
          <button
            type="submit"
            disabled={creating}
            style={{
              marginTop: 6,
              padding: '0.4rem 0.6rem',
              borderRadius: 6,
              border: 'none',
              background: '#3b82f6',
              color: '#e5e7eb',
              fontSize: '0.9rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            {creating ? 'Creating...' : 'Start Session'}
          </button>
        </form>
      </div>

      <div
        style={{
          padding: '0.75rem',
          borderRadius: 8,
          background: '#030712',
          border: '1px solid #1f2937',
        }}
      >
        <div style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Active Sessions</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: '40vh', overflowY: 'auto' }}>
          {sessions.map(session => {
            const label = session.customer.name || session.session_id;
            const active = session.session_id === activeSessionId;
            return (
              <button
                key={session.session_id}
                onClick={() => {
                  console.log("Selecting session with ID:", session.session_id);
                  onSelectSession(session.session_id);
                }}
                style={{
                  textAlign: 'left',
                  padding: '0.4rem 0.5rem',
                  borderRadius: 6,
                  border: 'none',
                  background: active ? '#1d4ed8' : '#020617',
                  color: active ? '#e5e7eb' : '#d1d5db',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  borderLeft: active ? '3px solid #60a5fa' : '3px solid transparent',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <span style={{ fontSize: '0.65rem', color: active ? '#bfdbfe' : '#6b7280' }}>●</span>
                <span>{label}</span>
              </button>
            );
          })}
          {sessions.length === 0 && (
            <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>No sessions yet. Create one above.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
