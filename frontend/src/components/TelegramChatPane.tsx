import React, { useEffect, useRef, useState } from 'react';
import type { Session, Message } from '../types';
import { sendMessage } from '../api';

interface Props {
  sessionId: string | null;
  session: Session | null;
}

const TelegramChatPane: React.FC<Props> = ({ sessionId, session }) => {
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const messagesToDisplay = session?.messages || [];
  console.log("TelegramChatPane rendering with messages:", messagesToDisplay);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messagesToDisplay.length]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    if (!sessionId) {
      window.alert('Start or select a session from the left before sending messages.');
      return;
    }
    const text = input.trim();
    setSending(true);
    try {
      await sendMessage(sessionId, { text: text });
      setInput('');
      // No longer need to manually add the message here.
      // The polling mechanism in App.tsx will fetch the updated message list.
    } finally {
      setSending(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div
        style={{
          marginTop: '0.25rem',
          textAlign: 'center',
          fontWeight: 600,
          fontSize: '1.05rem',
          padding: '0.4rem 0',
          borderBottom: '2px solid #374151',
          letterSpacing: 0.5,
        }}
      >
        TELEGRAM CHAT
      </div>
      <div
        ref={scrollRef}
        style={{
          height: '60vh',
          overflowY: 'auto',
          padding: '0.5rem 0.75rem 0.5rem 0',
          border: '2px solid #374151',
          borderRadius: '0.5rem',
          marginTop: '0.5rem',
          background: '#020617',
        }}
      >
        {messagesToDisplay.length ? (
          messagesToDisplay.map((msg: Message, idx: number) => {
            const isAgent = msg.sender === 'agent';
            const align = isAgent ? 'flex-end' : 'flex-start';
            const bg = isAgent ? '#111827' : '#1d4ed8'; // Agent messages darker, customer lighter blue
            const headerLabel = isAgent ? 'You' : session?.customer.name || 'Customer';
            const time = new Date(msg.timestamp).toLocaleTimeString(undefined, {
              hour: '2-digit',
              minute: '2-digit',
            });
            return (
              <div
                key={msg.message_id || idx} // Prefer message_id for a stable key
                style={{ display: 'flex', justifyContent: align, margin: '0.25rem 0' }}
              >
                <div
                  style={{
                    maxWidth: '80%',
                    padding: '0.45rem 0.7rem',
                    borderRadius: 10,
                    background: bg,
                    fontSize: '0.95rem',
                    boxShadow: '0 0 0 1px rgba(15,23,42,0.4)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: isAgent ? '#9ca3af' : '#e5e7eb',
                      marginBottom: '0.15rem',
                    }}
                  >
                    {headerLabel}
                  </div>
                  <div style={{ color: '#e5e7eb', marginBottom: '0.15rem' }}>{msg.text}</div>
                  <div
                    style={{
                      fontSize: '0.7rem',
                      color: '#9ca3af',
                      textAlign: isAgent ? 'right' : 'left',
                    }}
                  >
                    {time}
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>
            No messages yet. Start chatting from the input below or select a session.
          </div>
        )}
      </div>
      <form
        onSubmit={handleSubmit}
        style={{
          marginTop: '0.75rem',
          padding: '0.6rem 0.65rem 0.65rem',
          borderTop: '2px solid #374151',
          background: '#020617',
          display: 'flex',
          gap: '0.6rem',
          alignItems: 'flex-end',
        }}
      >
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={sessionId ? 'type to chat to client:' : 'Select a session to chat...'}
          rows={3}
          style={{
            flex: 1,
            padding: '0.45rem 0.6rem',
            borderRadius: 6,
            border: '1px solid #1f2937',
            background: '#020617',
            color: '#e5e7eb',
            resize: 'vertical',
            fontSize: '0.95rem',
          }}
          disabled={!sessionId}
        />
        <button
          type="submit"
          disabled={sending || !sessionId}
          style={{
            padding: '0.45rem 0.9rem',
            borderRadius: 999,
            border: 'none',
            background: '#22c55e',
            color: '#022c22',
            fontWeight: 600,
            cursor: (sending || !sessionId) ? 'not-allowed' : 'pointer',
            opacity: (sending || !sessionId) ? 0.7 : 1,
            whiteSpace: 'nowrap',
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default TelegramChatPane;
