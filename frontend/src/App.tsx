import React, { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import TelegramChatPane from './components/TelegramChatPane';
import GeminiChatPane from './components/GeminiChatPane'; // Reverted import
import type { Session, CreateSessionRequest } from './types';
import { createSession, getSession, listSessions } from './api';

const POLLING_INTERVAL_MS = 3000; // Poll every 3 seconds

const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [loadingSession, setLoadingSession] = useState(false);

  // Initial load of sessions
  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch((err) => {
        console.error("Failed to load sessions:", err);
        // ignore initial load errors, e.g., if no sessions exist
      });
  }, []);

  // Effect to handle WebSocket connection for real-time updates
  useEffect(() => {
    if (!activeSessionId) {
      return;
    }

    // Still fetch the session once initially when selected
    const fetchInitialSession = async () => {
      setLoadingSession(true);
      try {
        const res = await getSession(activeSessionId);
        setActiveSession(res);
      } catch (error) {
        console.error('Failed to fetch initial session:', error);
        setActiveSession(null);
      } finally {
        setLoadingSession(false);
      }
    };
    fetchInitialSession();

    const wsUrl = `ws://localhost:8000/ws/${activeSessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`WebSocket connected for session: ${activeSessionId}`);
    };

    ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      try {
        const updatedSession = JSON.parse(event.data);
        setActiveSession(updatedSession);
        console.log("Called setActiveSession with:", updatedSession);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected for session: ${activeSessionId}`);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    // Cleanup WebSocket on unmount or when activeSessionId changes
    return () => {
      ws.close();
    };
  }, [activeSessionId]);

  // New useEffect to log when activeSession state actually changes
  useEffect(() => {
    console.log("activeSession state has been updated:", activeSession);
  }, [activeSession]);

  async function handleCreateSession(data: CreateSessionRequest) {
    const res = await createSession(data);
    // Add new session to the list if not already there
    setSessions((prev) => {
      if (!prev.some(s => s.session_id === res.session_id)) {
        return [...prev, res];
      }
      return prev;
    });
    setActiveSessionId(res.session_id);
    setActiveSession(res);
  }

  function handleSelectSession(id: string) {
    setActiveSessionId(id);
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#020617', color: '#e5e7eb' }}>
      {console.log("Sessions passed to Sidebar:", sessions)} {/* Debug log */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
      />
      <div
        style={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          padding: '1rem 1.5rem',
          boxSizing: 'border-box',
        }}
      >
        <div
          style={{
            display: 'flex',
            width: '100%',
            maxWidth: 1180,
            gap: '1rem',
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <TelegramChatPane sessionId={activeSessionId} session={activeSession} />
          </div>
          <div
            style={{
              width: 2,
              background: '#374151',
              alignSelf: 'stretch',
              position: 'relative',
              margin: '0 0.25rem',
            }}
          >
            <div
              style={{
                position: 'absolute',
                top: '-0.6rem',
                left: '50%',
                transform: 'translateX(-50%)',
                fontSize: '0.7rem',
                color: '#6b7280',
                padding: '0 0.25rem',
                background: '#020617',
              }}
            >
              LLM INSIGHTS
            </div>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            {loadingSession && <div style={{ fontSize: '0.9rem', color: '#9ca3af' }}>Loading session...</div>}
            <GeminiChatPane // Reverted component name
              session={activeSession}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
