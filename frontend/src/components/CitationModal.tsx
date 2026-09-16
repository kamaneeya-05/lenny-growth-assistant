import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Clock, User, FileText, CheckCircle2, Play, Pause, Volume2, Sparkles, Share2 } from 'lucide-react';
import { Citation } from '../types';

interface CitationModalProps {
  citation: Citation | null;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({ citation, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(35);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setProgress((prev) => (prev >= 100 ? 0 : prev + 1));
      }, 400);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  if (!citation) return null;

  const handleShare = () => {
    navigator.clipboard.writeText(
      `"${citation.excerpt}" — ${citation.guest || 'Lenny\'s Podcast'}, from ${citation.title}`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-2xl rounded-3xl bg-slate-900 border border-slate-750 shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950/60">
          <div className="space-y-1.5 min-w-0 pr-4">
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {citation.source_type.toUpperCase()}
              </span>
              <span className="text-xs text-emerald-400 flex items-center gap-1 font-mono font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {Math.round(citation.relevance_score * 100)}% Verified Match
              </span>
            </div>
            <h3 className="text-base font-bold text-white leading-snug">
              {citation.title}
            </h3>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Podcast Audio Simulation Bar */}
        <div className="px-6 py-4 bg-indigo-950/30 border-b border-indigo-900/30 flex items-center gap-4">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shadow-lg shadow-indigo-600/30 transition-all shrink-0 active:scale-95"
            title={isPlaying ? 'Pause Segment' : 'Play Segment'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>

          <div className="flex-1 space-y-1">
            <div className="flex items-center justify-between text-[11px] text-slate-300 font-medium">
              <span className="flex items-center gap-1.5">
                <Volume2 className="w-3.5 h-3.5 text-indigo-400" />
                Audio Passage Segment
              </span>
              <span className="font-mono text-indigo-300">
                {citation.timestamp_str || '00:00:00'}
              </span>
            </div>

            {/* Scrubber bar */}
            <div
              className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden cursor-pointer"
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const clickPos = (e.clientX - rect.left) / rect.width;
                setProgress(Math.round(clickPos * 100));
              }}
            >
              <div
                className="h-full bg-indigo-500 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>

        {/* Metadata Strip */}
        <div className="px-6 py-3 bg-slate-900/60 border-b border-slate-800 flex flex-wrap items-center gap-4 text-xs text-slate-300">
          {citation.guest && (
            <div className="flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-medium text-white">{citation.guest}</span>
            </div>
          )}
          {citation.timestamp_str && (
            <div className="flex items-center gap-1.5 font-mono text-slate-400">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Timestamp: {citation.timestamp_str}</span>
            </div>
          )}
          {citation.url && (
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 hover:underline ml-auto font-medium"
            >
              <span>Substack Post</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>

        {/* Verbatim Transcript Excerpt */}
        <div className="p-6 overflow-y-auto flex-1 space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              Verbatim Transcript Evidence
            </span>
            <button
              onClick={handleShare}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-sans"
            >
              <Share2 className="w-3 h-3" />
              <span>{copied ? 'Copied Quote!' : 'Copy Quote'}</span>
            </button>
          </div>

          <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800/80 font-mono text-xs leading-relaxed text-slate-200 whitespace-pre-wrap selection:bg-indigo-500/40">
            {citation.excerpt}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Indexed with speaker diarization and timestamp alignments
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
