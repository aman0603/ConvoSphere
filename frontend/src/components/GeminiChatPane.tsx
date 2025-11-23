import React from 'react';
import type { Session, LocalLLMAnalysis } from '../types';

interface Props {
  session: Session | null;
}

const IntelligencePane: React.FC<Props> = ({ session }) => {
  const localLlmAnalysis: LocalLLMAnalysis | undefined = session?.local_llm;
  const lastAnalysisAt = localLlmAnalysis?.last_analysis_at
    ? new Date(localLlmAnalysis.last_analysis_at).toLocaleString()
    : 'N/A';

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
        TACTICAL INSIGHTS (Local LLM)
      </div>
      <div
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
        {localLlmAnalysis ? (
          <div>
            <p><strong>Last Analyzed:</strong> {lastAnalysisAt}</p>
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
            {/* Add more intelligence metrics here as they become available */}
          </div>
        ) : (
          <div style={{ color: '#6b7280' }}>
            No LLM analysis available for this session yet. Send a message to get insights.
          </div>
        )}
      </div>
      {/* Remove the chat input form for this pane */}
    </div>
  );
};

export default IntelligencePane;
