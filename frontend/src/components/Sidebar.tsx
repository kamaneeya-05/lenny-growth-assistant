import React, { useState } from 'react';
import {
  Plus,
  MessageSquare,
  Trash2,
  Database,
  Sparkles,
  Search,
  Download,
  Share2,
  Bot
} from 'lucide-react';
import { Session, KnowledgeStatus } from '../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onExportSession: () => void;
  knowledgeStatus: KnowledgeStatus | null;
  onOpenKnowledge: () => void;
  activeProvider: string;
  activeModel: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onExportSession,
  knowledgeStatus,
  onOpenKnowledge,
  activeProvider,
  activeModel,
}) => {
  const [filterText, setFilterText] = useState('');

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(filterText.toLowerCase())
  );

  return (
    <aside className="w-72 bg-[#0d1322] border-r border-slate-800/80 flex flex-col h-screen select-none shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-600/25 ring-1 ring-white/15">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xs font-bold text-white tracking-tight flex items-center gap-1.5">
                Lenny Assistant
                <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  AI PRO
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 font-medium">Growth & Product Engine</p>
            </div>
          </div>
        </div>

        {/* Action Buttons: New Chat & Export */}
        <div className="flex items-center gap-2">
          <button
            onClick={onNewChat}
            className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 px-3 rounded-xl transition-all shadow-md shadow-indigo-600/25 text-xs active:scale-[0.98]"
          >
            <Plus className="w-4 h-4 stroke-[2.5]" />
            <span>New Chat</span>
          </button>

          {activeSessionId && (
            <button
              onClick={onExportSession}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
              title="Export Conversation (Markdown)"
            >
              <Download className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Search / Filter bar for sessions */}
        {sessions.length > 2 && (
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              placeholder="Filter chats..."
              className="w-full bg-slate-900/90 border border-slate-800 focus:border-indigo-500/60 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-400 outline-none transition-all"
            />
          </div>
        )}
      </div>

      {/* Sessions Feed */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Recent Conversations ({sessions.length})
        </div>

        {filteredSessions.length === 0 ? (
          <div className="text-center py-8 px-4 text-xs text-slate-400">
            {filterText ? 'No matching conversations' : 'No chats yet. Start a new conversation.'}
          </div>
        ) : (
          filteredSessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <div
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`group flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-xs transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white shadow-sm ring-1 ring-slate-700/80 font-medium'
                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <MessageSquare
                    className={`w-3.5 h-3.5 shrink-0 ${
                      isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-300'
                    }`}
                  />
                  <span className="truncate">{session.title}</span>
                </div>

                <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => onDeleteSession(session.id, e)}
                    className="p-1 hover:text-rose-400 text-slate-400 rounded transition-colors"
                    title="Delete Chat"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Knowledge & Status Drawer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/50 space-y-2">
        {/* Knowledge Base Status Button */}
        <button
          onClick={onOpenKnowledge}
          className="w-full flex items-center justify-between p-2.5 rounded-2xl bg-slate-900/90 hover:bg-slate-850 border border-slate-800 text-xs transition-all group"
        >
          <div className="flex items-center gap-2 text-slate-300">
            <Database className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-white">Transcript Archive</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-[11px] text-slate-400 group-hover:text-slate-300 font-mono">
              {knowledgeStatus?.total_sources || 14} sources
            </span>
          </div>
        </button>

        {/* Active Provider Pill */}
        <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-slate-900/40 border border-slate-800/60 text-[11px] text-slate-400 font-mono">
          <div className="flex items-center gap-1.5">
            <Bot className="w-3.5 h-3.5 text-indigo-400" />
            <span className="capitalize">{activeProvider}</span>
          </div>
          <span className="text-slate-300 truncate max-w-[110px]" title={activeModel}>
            {activeModel}
          </span>
        </div>
      </div>
    </aside>
  );
};
