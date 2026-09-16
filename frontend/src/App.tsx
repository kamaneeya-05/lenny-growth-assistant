import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatHeader } from './components/ChatHeader';
import { MessageItem } from './components/MessageItem';
import { Composer } from './components/Composer';
import { EmptyState } from './components/EmptyState';
import { CitationModal } from './components/CitationModal';
import { ArtifactStudio } from './components/ArtifactStudio';
import { KnowledgeModal } from './components/KnowledgeModal';
import { ApiService } from './services/api';
import { Session, Message, Citation, Artifact, ModelsResponse, KnowledgeStatus } from './types';
import { AlertCircle, Loader2 } from 'lucide-react';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const [modelsData, setModelsData] = useState<ModelsResponse | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama');
  const [selectedModel, setSelectedModel] = useState<string>('llama3.2');

  const [knowledgeStatus, setKnowledgeStatus] = useState<KnowledgeStatus | null>(null);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);
  const [isKnowledgeOpen, setIsKnowledgeOpen] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Initial Data Bootstrap
  useEffect(() => {
    const bootstrap = async () => {
      try {
        const [modelsRes, kbRes] = await Promise.all([
          ApiService.getModels(),
          ApiService.getKnowledgeStatus(),
        ]);
        setModelsData(modelsRes);
        setSelectedProvider(modelsRes.active_provider || 'ollama');
        setSelectedModel(modelsRes.active_model || 'llama3.2');
        setKnowledgeStatus(kbRes);

        // Load sessions
        const loadedSessions = await ApiService.listSessions();
        setSessions(loadedSessions);

        if (loadedSessions.length > 0) {
          handleSelectSession(loadedSessions[0].id);
        } else {
          handleNewChat();
        }
      } catch (err: any) {
        console.error('Bootstrap error:', err);
        setError(`Failed to connect to backend: ${err.message}. Ensure backend is running on port 8000.`);
      }
    };
    bootstrap();
  }, []);

  const handleSelectSession = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setError(null);
    try {
      const sess = await ApiService.getSession(sessionId);
      setActiveSession(sess);
      setMessages(sess.messages || []);

      // Check if session has an artifact to populate studio
      const artifactsInSess = sess.messages?.filter((m) => m.artifact).map((m) => m.artifact!);
      if (artifactsInSess && artifactsInSess.length > 0) {
        setActiveArtifact(artifactsInSess[artifactsInSess.length - 1]);
      } else {
        setActiveArtifact(null);
        setIsArtifactOpen(false);
      }
    } catch (err: any) {
      setError(`Failed to load session: ${err.message}`);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSess = await ApiService.createSession(
        'New Conversation',
        selectedProvider,
        selectedModel
      );
      setSessions((prev) => [newSess, ...prev]);
      setActiveSessionId(newSess.id);
      setActiveSession(newSess);
      setMessages([]);
      setActiveArtifact(null);
      setIsArtifactOpen(false);
      setError(null);
    } catch (err: any) {
      setError(`Failed to create session: ${err.message}`);
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await ApiService.deleteSession(sessionId);
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setSessions(remaining);

      if (activeSessionId === sessionId) {
        if (remaining.length > 0) {
          handleSelectSession(remaining[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch (err: any) {
      setError(`Failed to delete session: ${err.message}`);
    }
  };

  const handleExportSession = () => {
    if (!activeSession || messages.length === 0) return;

    let md = `# ${activeSession.title}\n`;
    md += `*Exported from The Lenny Growth Assistant on ${new Date().toLocaleDateString()}*\n\n---\n\n`;

    messages.forEach((m) => {
      const author = m.role === 'user' ? '### 👤 User' : '### 💡 The Lenny Growth Assistant';
      md += `${author}\n\n${m.content}\n\n`;
      if (m.citations && m.citations.length > 0) {
        md += `**Sources Cited:**\n`;
        m.citations.forEach((c) => {
          md += `- **${c.title}** (${c.guest || 'Lenny'}), Timestamp: ${c.timestamp_str || 'N/A'}\n  > "${c.excerpt}"\n`;
        });
        md += `\n`;
      }
      md += `---\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeSession.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSendMessage = async (
    text: string,
    options?: { generate_ship30_essay?: boolean; generate_artifact?: boolean; artifact_type?: string }
  ) => {
    if (!activeSessionId) return;

    const optimisticMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await ApiService.sendMessage(activeSessionId, text, {
        model_provider: selectedProvider,
        model_name: selectedModel,
        ...options,
      });

      setMessages((prev) => [...prev, response.message]);

      if (response.artifact) {
        setActiveArtifact(response.artifact);
        setIsArtifactOpen(true);
      }

      // Refresh sessions list
      const updatedList = await ApiService.listSessions();
      setSessions(updatedList);
      const current = updatedList.find((s) => s.id === activeSessionId);
      if (current) setActiveSession(current);
    } catch (err: any) {
      setError(`Error generating response: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectModel = (provider: string, model: string) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
    if (activeSessionId) {
      ApiService.updateSession(activeSessionId, {
        model_provider: provider,
        model_name: model,
      }).catch(console.error);
    }
  };

  const refreshKnowledge = async () => {
    try {
      const res = await ApiService.getKnowledgeStatus();
      setKnowledgeStatus(res);
    } catch (err) {
      console.error('Failed refreshing knowledge status:', err);
    }
  };

  // Collect all artifacts in active conversation
  const sessionArtifacts: Artifact[] = messages
    .filter((m) => m.artifact)
    .map((m) => m.artifact!);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#090d16] text-slate-100 font-sans">
      {/* 1. Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onExportSession={handleExportSession}
        knowledgeStatus={knowledgeStatus}
        onOpenKnowledge={() => setIsKnowledgeOpen(true)}
        activeProvider={selectedProvider}
        activeModel={selectedModel}
      />

      {/* 2. Main Chat Column */}
      <main className="flex-1 flex flex-col h-screen min-w-0 relative">
        <ChatHeader
          title={activeSession?.title || 'New Conversation'}
          modelsData={modelsData}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          onSelectModel={handleSelectModel}
          hasArtifact={activeArtifact !== null || sessionArtifacts.length > 0}
          isArtifactOpen={isArtifactOpen}
          onToggleArtifact={() => setIsArtifactOpen(!isArtifactOpen)}
        />

        {/* Error Notification Banner */}
        {error && (
          <div className="mx-6 my-2 p-3 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 flex items-center justify-between animate-in fade-in">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-rose-400 hover:text-rose-200 font-semibold px-2 py-0.5"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Message Feed / Empty State */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <EmptyState onSelectPrompt={handleSendMessage} />
          ) : (
            <div className="pb-6">
              {messages.map((msg) => (
                <MessageItem
                  key={msg.id}
                  message={msg}
                  onOpenCitation={(cite) => setActiveCitation(cite)}
                  onOpenArtifact={() => {
                    if (msg.artifact) {
                      setActiveArtifact(msg.artifact);
                    }
                    setIsArtifactOpen(true);
                  }}
                />
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="py-5 px-6 bg-slate-900/20 border-y border-slate-800/30">
                  <div className="max-w-3xl mx-auto flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-indigo-600/30 text-indigo-400 flex items-center justify-center animate-pulse ring-1 ring-indigo-500/40">
                      <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                    <div className="space-y-0.5">
                      <p className="text-xs font-semibold text-white">
                        Synthesizing Grounded Insights...
                      </p>
                      <p className="text-[11px] text-slate-400 font-medium">
                        Cross-referencing verified quotes across Lenny's transcript archive
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Composer */}
        <Composer onSend={handleSendMessage} isLoading={isLoading} />
      </main>

      {/* 3. Artifact Studio (Split-screen or Fullscreen) */}
      {isArtifactOpen && activeArtifact && (
        <ArtifactStudio
          artifacts={sessionArtifacts.length > 0 ? sessionArtifacts : [activeArtifact]}
          activeArtifact={activeArtifact}
          onSelectArtifact={(art) => setActiveArtifact(art)}
          onClose={() => setIsArtifactOpen(false)}
        />
      )}

      {/* 4. Citation Details Modal with Audio Bar */}
      {activeCitation && (
        <CitationModal
          citation={activeCitation}
          onClose={() => setActiveCitation(null)}
        />
      )}

      {/* 5. Knowledge Base & Archive Search Explorer Modal */}
      {isKnowledgeOpen && (
        <KnowledgeModal
          status={knowledgeStatus}
          onClose={() => setIsKnowledgeOpen(false)}
          onRefresh={refreshKnowledge}
          onSelectQuery={(q) => handleSendMessage(q)}
        />
      )}
    </div>
  );
};
