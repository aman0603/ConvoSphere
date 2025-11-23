import React, { useState, useEffect, useRef } from 'react';
import type { Session, LocalLLMAnalysis, GeminiAnalysis } from '../types';
import { triggerGemini } from '../api';

interface Props {
  session: Session | null;
}

const IntelligencePane: React.FC<Props> = ({ session }) => {
  const localLlmAnalysis: LocalLLMAnalysis | undefined = session?.local_llm;
  const geminiAnalysis: GeminiAnalysis | undefined = session?.gemini;
  const [geminiInput, setGeminiInput] = useState('');
  const [sendingGemini, setSendingGemini] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const localLlmLastAnalysisAt = localLlmAnalysis?.last_analysis_at
    ? new Date(localLlmAnalysis.last_analysis_at).toLocaleString()
    : 'N/A';

  const geminiLastCallAt = geminiAnalysis?.last_call_at
    ? new Date(geminiAnalysis.last_call_at).toLocaleString()
    : 'N/A';

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [localLlmAnalysis, geminiAnalysis]);

  async function handleTriggerGemini(e: React.FormEvent) {
    e.preventDefault();
    if (!geminiInput.trim() || !session?.session_id) return;
    setSendingGemini(true);
    try {
      await triggerGemini(session.session_id, geminiInput.trim());
      setGeminiInput('');
    } finally {
      setSendingGemini(false);
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
        LLM INSIGHTS
      </div>

      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0.5rem 0.75rem',
          border: '2px solid #374151',
          borderRadius: '0.5rem',
          marginTop: '0.5rem',
          background: '#020617',
          fontSize: '0.9rem',
          color: '#e5e7eb',
        }}
      >
        {localLlmAnalysis || geminiAnalysis ? (
          <div>
            <h3 style={{ color: '#a5b4fc', marginBottom: '0.5rem' }}>Tactical Insights (Local LLM)</h3>
            {localLlmAnalysis ? (
              <div>
                <p><strong>Last Analyzed:</strong> {localLlmLastAnalysisAt}</p>
                {localLlmAnalysis.error ? (
                  <p style={{ color: '#dc2626' }}><strong>Error:</strong> {localLlmAnalysis.error}</p>
                ) : (
                  <>
                    <p><strong>Global Summary:</strong> {localLlmAnalysis.global_summary || 'N/A'}</p>
                    <p><strong>Latest Interaction:</strong> {localLlmAnalysis.latest_interaction_summary || 'N/A'}</p>
                    <p><strong>Sentiment:</strong> {localLlmAnalysis.current_sentiment || 'N/A'}</p>
                    <p><strong>Conversation State:</strong> {localLlmAnalysis.conversation_state_tag || 'N/A'}</p>
                  </>
                )}
              </div>
            ) : (
              <p style={{ color: '#6b7280' }}>No Local LLM analysis available yet.</p>
            )}

            <h3 style={{ color: '#a5b4fc', marginTop: '1.5rem', marginBottom: '0.5rem' }}>Strategic Insights (Gemini)</h3>
            {geminiAnalysis ? (
              <div>
                <p><strong>Last Called:</strong> {geminiLastCallAt}</p>
                {geminiAnalysis.error ? (
                  <p style={{ color: '#dc2626' }}><strong>Error:</strong> {geminiAnalysis.error}</p>
                ) : (
                  <>
                    {geminiAnalysis.response?.reply ? (
                      <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '0.5rem', marginTop: '0.5rem' }}>
                        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', color: '#e5e7eb' }}>
                          {JSON.stringify(geminiAnalysis.response.reply, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      <p style={{ color: '#6b7280' }}>No Gemini response available yet.</p>
                    )}
                  </>
                )}
              </div>
            ) : (
              <p style={{ color: '#6b7280' }}>No Gemini analysis available yet.</p>
            )}
          </div>
        ) : (
          <div style={{ color: '#6b7280' }}>
            No LLM analysis available for this session yet. Send a message or trigger Gemini to get insights.
          </div>
        )}
      </div>

      <form
        onSubmit={handleTriggerGemini}
        style={{
          padding: '1rem 0.75rem',
          borderTop: '2px solid #374151',
          background: '#020617',
          display: 'flex',
          gap: '0.5rem',
          alignItems: 'center',
          marginTop: '0.5rem',
        }}
      >
        <textarea
          value={geminiInput}
          onChange={(e) => setGeminiInput(e.target.value)}
          placeholder="Ask Gemini for strategic advice..."
          rows={1}
          style={{
            flex: 1,
            padding: '0.5rem 0.75rem',
            borderRadius: '0.375rem',
            border: '1px solid #4b5563',
            background: '#1f2937',
            color: '#e5e7eb',
            fontSize: '0.85rem',
            outline: 'none',
            resize: 'none',
            fontFamily: 'inherit',
          }}
          disabled={!session?.session_id || sendingGemini}
        />
        <button
          type="submit"
          disabled={!session?.session_id || sendingGemini || !geminiInput.trim()}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem',
            border: 'none',
            background: '#6366f1',
            color: '#ffffff',
            fontSize: '0.85rem',
            fontWeight: 600,
            cursor: (!session?.session_id || sendingGemini || !geminiInput.trim()) ? 'not-allowed' : 'pointer',
            opacity: (!session?.session_id || sendingGemini || !geminiInput.trim()) ? 0.6 : 1,
            flexShrink: 0,
          }}
        >
          {sendingGemini ? 'Sending...' : 'Trigger Gemini'}
        </button>
      </form>
    </div>
  );
};

export default IntelligencePane;
