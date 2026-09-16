import React, { useState } from 'react';
import { Bot, User, Copy, Check, ExternalLink, Sparkles, BookOpen, Clock, FileCode, CheckCircle2 } from 'lucide-react';
import { Message, Citation } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';

interface MessageItemProps {
  message: Message;
  onOpenCitation: (citation: Citation) => void;
  onOpenArtifact: () => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onOpenCitation,
  onOpenArtifact,
}) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`group py-5 px-6 transition-colors ${
        isUser ? 'bg-transparent' : 'bg-slate-900/30 border-y border-slate-800/40'
      }`}
    >
      <div className="max-w-3xl mx-auto flex items-start gap-4">
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
            isUser
              ? 'bg-slate-800 text-slate-300 ring-1 ring-slate-700'
              : 'bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white shadow-indigo-600/20'
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
        </div>

        {/* Message Content Container */}
        <div className="flex-1 min-w-0 space-y-3">
          {/* Header Row */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold tracking-tight text-white">
              {isUser ? 'You' : 'The Lenny Growth Assistant'}
            </span>

            {/* Actions */}
            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={handleCopy}
                className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 text-xs flex items-center gap-1 transition-colors"
                title="Copy Message"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              </button>
            </div>
          </div>

          {/* Text Body with Rich Markdown */}
          <MarkdownRenderer content={message.content} />

          {/* Inline Artifact Card */}
          {message.artifact && (
            <div
              onClick={onOpenArtifact}
              className="mt-4 p-3.5 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 hover:border-indigo-500/60 cursor-pointer transition-all hover:bg-indigo-950/40 group/art shadow-lg shadow-indigo-950/20"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-indigo-600/30 text-indigo-400 flex items-center justify-center ring-1 ring-indigo-500/40">
                    <FileCode className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300">
                        {message.artifact.artifact_type.toUpperCase()} ARTIFACT
                      </span>
                      <span className="text-[11px] text-slate-400">Click to open studio</span>
                    </div>
                    <h4 className="text-xs font-bold text-white mt-0.5 group-hover/art:text-indigo-300 transition-colors">
                      {message.artifact.title}
                    </h4>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 text-xs font-medium text-indigo-400 group-hover/art:translate-x-0.5 transition-transform">
                  <span>Inspect</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          )}

          {/* Citation Pills Strip */}
          {message.citations && message.citations.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Grounded Transcript Sources ({message.citations.length})</span>
              </div>

              <div className="flex flex-wrap gap-2">
                {message.citations.map((cite, i) => (
                  <button
                    key={i}
                    onClick={() => onOpenCitation(cite)}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-750 border border-slate-700/80 text-[11px] text-slate-200 transition-all hover:border-indigo-500/50 hover:shadow-sm"
                  >
                    <span className="font-semibold text-indigo-400">[{i + 1}]</span>
                    <span className="font-medium text-white truncate max-w-[200px]" title={cite.title}>
                      {cite.guest || cite.title}
                    </span>
                    {cite.timestamp_str && (
                      <span className="text-[10px] text-amber-400 font-mono flex items-center gap-0.5">
                        <Clock className="w-2.5 h-2.5" />
                        {cite.timestamp_str}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
