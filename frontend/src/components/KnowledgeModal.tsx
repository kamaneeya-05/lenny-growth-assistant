import React, { useState } from 'react';
import {
  X,
  Database,
  RefreshCw,
  Download,
  ExternalLink,
  Search,
  BookOpen,
  Sparkles,
  MessageSquare,
  Clock,
  User,
  CheckCircle2
} from 'lucide-react';
import { KnowledgeStatus } from '../types';
import { ApiService } from '../services/api';

interface KnowledgeModalProps {
  status: KnowledgeStatus | null;
  onClose: () => void;
  onRefresh: () => void;
  onSelectQuery?: (query: string) => void;
}

export const KnowledgeModal: React.FC<KnowledgeModalProps> = ({
  status,
  onClose,
  onRefresh,
  onSelectQuery,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'search'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const data = await ApiService.searchTranscripts(searchQuery.trim(), 8);
      setSearchResults(data.results || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleTriggerReindex = async (downloadRemote: boolean) => {
    setIsIngesting(true);
    setIngestMsg(downloadRemote ? 'Downloading transcripts & re-indexing...' : 'Re-indexing local transcripts...');
    try {
      await ApiService.triggerIngestion({ download_remote: downloadRemote, force_reindex: true });
      onRefresh();
      setIngestMsg('Re-indexing complete!');
      setTimeout(() => setIngestMsg(null), 3000);
    } catch (e: any) {
      setIngestMsg(`Error: ${e.message}`);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-3xl rounded-3xl bg-slate-900 border border-slate-750 shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-start justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center ring-1 ring-indigo-500/30">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Transcript Archive & Knowledge Base
              </h3>
              <p className="text-xs text-slate-400">
                Grounded in Lenny's Podcast and Newsletter repositories
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="px-5 border-b border-slate-800 flex items-center gap-6 bg-slate-950/20 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3 border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'overview'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Overview & Sources ({status?.total_sources || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('search')}
            className={`py-3 border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'search'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Archive Search Explorer</span>
          </button>
        </div>

        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-3 p-4 bg-slate-950/40 border-b border-slate-800">
              <div className="p-3.5 rounded-2xl bg-slate-800/40 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Total Documents</span>
                <div className="text-xl font-bold text-white mt-1">{status?.total_sources || 0}</div>
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-800/40 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Indexed Chunks</span>
                <div className="text-xl font-bold text-indigo-400 mt-1">{status?.total_chunks || 0}</div>
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-800/40 border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Vocabulary Size</span>
                <div className="text-xl font-bold text-emerald-400 mt-1">{status?.vocab_size?.toLocaleString() || 0}</div>
              </div>
            </div>

            {/* Ingestion Action Bar */}
            <div className="p-3 bg-slate-900/60 border-b border-slate-800 flex items-center justify-between">
              <span className="text-xs text-slate-300 font-medium">
                {ingestMsg || 'Manage transcript ingestion & indexing:'}
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleTriggerReindex(false)}
                  disabled={isIngesting}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-xs font-medium text-slate-200 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isIngesting ? 'animate-spin' : ''}`} />
                  <span>Re-index Local</span>
                </button>

                <button
                  onClick={() => handleTriggerReindex(true)}
                  disabled={isIngesting}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-colors disabled:opacity-50 shadow-md shadow-indigo-600/20"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Fetch & Re-index</span>
                </button>
              </div>
            </div>

            {/* Source Documents List */}
            <div className="p-4 overflow-y-auto flex-1 space-y-2">
              <div className="space-y-1.5">
                {status?.sources?.map((s, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-xs hover:border-slate-700 transition-colors"
                  >
                    <div className="space-y-0.5 min-w-0 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                          {s.type}
                        </span>
                        <span className="font-semibold text-white truncate">{s.title}</span>
                      </div>
                      {s.guest && (
                        <p className="text-[11px] text-slate-400">Guest: {s.guest}</p>
                      )}
                    </div>

                    <div className="flex items-center gap-4 shrink-0 text-right font-mono text-[11px] text-slate-400">
                      <div>
                        <span className="text-slate-200">{s.chunks}</span> chunks
                      </div>
                      <div>
                        <span className="text-slate-200">{s.word_count?.toLocaleString()}</span> words
                      </div>
                      {s.url && (
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:text-indigo-300"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Tab 2: Archive Search Explorer */}
        {activeTab === 'search' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Search Input Bar */}
            <form onSubmit={handleSearch} className="p-4 border-b border-slate-800 bg-slate-950/40 flex items-center gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search verbatim quotes across all transcripts (e.g. 'taste', 'retention smile', 'friction')..."
                  className="w-full bg-slate-900 border border-slate-750 focus:border-indigo-500 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-400 outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={isSearching || !searchQuery.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-colors disabled:opacity-50"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </form>

            {/* Search Results Feed */}
            <div className="p-4 overflow-y-auto flex-1 space-y-3">
              {searchResults.length === 0 ? (
                <div className="text-center py-12 text-slate-400 text-xs space-y-1">
                  <Search className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                  <p className="font-semibold text-slate-300">Explore Lenny's Transcript Archive</p>
                  <p>Type keywords, guest names, or product management concepts to inspect exact passages.</p>
                </div>
              ) : (
                searchResults.map((r, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2 hover:border-indigo-500/40 transition-colors"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2 font-medium text-white">
                        <span className="text-indigo-400 font-bold">[{i + 1}]</span>
                        <span>{r.title}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-slate-400">
                        {r.timestamp_str && (
                          <span className="flex items-center gap-1 font-mono text-amber-400">
                            <Clock className="w-3 h-3" />
                            {r.timestamp_str}
                          </span>
                        )}
                        <span className="font-mono text-emerald-400">
                          {Math.round(r.score * 100)}% match
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 font-mono leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-850">
                      {r.excerpt}
                    </p>

                    {onSelectQuery && (
                      <div className="flex justify-end pt-1">
                        <button
                          onClick={() => {
                            onSelectQuery(`Tell me more about this insight from ${r.guest || r.title}: "${r.excerpt.slice(0, 150)}..."`);
                            onClose();
                          }}
                          className="flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 font-medium"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>Ask Assistant About This</span>
                        </button>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Lenny Growth Assistant • Grounded Knowledge Engine
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
