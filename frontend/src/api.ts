import type { Session, Message, CreateSessionRequest, SendMessageRequest } from './types'; // Assuming these types are defined or will be

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export function listSessions(): Promise<Session[]> {
  return jsonFetch<Session[]>(`${API_BASE}/api/sessions`); // Assuming an endpoint to list all sessions
}

export function createSession(body: CreateSessionRequest): Promise<Session> {
  return jsonFetch<Session>(`${API_BASE}/api/sessions`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function getSession(sessionId: string): Promise<Session> {
  return jsonFetch<Session>(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}`);
}

export function sendMessage(sessionId: string, body: SendMessageRequest): Promise<Session> {
  return jsonFetch<Session>(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}/send`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

// The following functions are removed as they are no longer relevant for the new backend:
// - pollTelegram: Incoming messages are part of the session object via getSession
// - sendGemini: Gemini calls are handled by the backend

