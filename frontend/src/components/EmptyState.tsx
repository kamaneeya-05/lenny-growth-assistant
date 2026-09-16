import React from 'react';
import { Sparkles, ArrowRight, BookOpen, Feather, FileCode, Zap, CheckCircle2 } from 'lucide-react';

interface EmptyStateProps {
  onSelectPrompt: (
    prompt: string,
    options?: { generate_ship30_essay?: boolean; generate_artifact?: boolean }
  ) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const promptSuggestions = [
    {
      title: "AI & Taste in Product Craft",
      guest: "Adam Mosseri",
      prompt: "What does Adam Mosseri say about AI being a tailwind for authenticity and taste in product design?",
      icon: <Sparkles className="w-4 h-4 text-indigo-400" />,
      tag: "Grounded Q&A",
    },
    {
      title: "B2B Growth Loops & Monetization",
      guest: "Elena Verna",
      prompt: "How does Elena Verna explain B2B growth loops, product-led sales, and monetization?",
      icon: <Zap className="w-4 h-4 text-amber-400" />,
      tag: "Growth Framework",
    },
    {
      title: "Ship 30 for 30 Deep Dive Essay",
      guest: "Stewart Butterfield / Slack",
      prompt: "Turn Stewart Butterfield's mental models for building Slack into an approximately 1,250-word Ship 30 for 30 essay",
      icon: <Feather className="w-4 h-4 text-rose-400" />,
      tag: "Ship 30 Essay",
      options: { generate_ship30_essay: true },
    },
    {
      title: "HTML Strategy One-Pager Artifact",
      guest: "Product Leadership",
      prompt: "Create an interactive HTML product strategy one-pager artifact based on finding Product-Market Fit",
      icon: <FileCode className="w-4 h-4 text-emerald-400" />,
      tag: "HTML Artifact",
      options: { generate_artifact: true },
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center max-w-3xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Brand Hero */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Grounded in Lenny's Podcast & Newsletter Archive</span>
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">
          What product challenge are you solving today?
        </h2>
        <p className="text-xs text-slate-400 max-w-lg mx-auto leading-relaxed">
          Ask complex growth questions, generate high-impact Ship 30 for 30 essays, and preview
          interactive HTML/Markdown strategy artifacts—strictly grounded in verified transcripts.
        </p>
      </div>

      {/* Suggested Prompts Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
        {promptSuggestions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(item.prompt, item.options)}
            className="p-4 rounded-2xl bg-slate-900/60 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/50 transition-all hover:shadow-lg hover:shadow-indigo-950/20 group text-xs space-y-2 flex flex-col justify-between"
          >
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-slate-800 border border-slate-700">
                    {item.icon}
                  </div>
                  <span className="font-semibold text-white group-hover:text-indigo-300 transition-colors">
                    {item.title}
                  </span>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                  {item.tag}
                </span>
              </div>
              <p className="text-slate-400 leading-relaxed line-clamp-2">
                {item.prompt}
              </p>
            </div>

            <div className="flex items-center gap-1 text-[11px] font-medium text-indigo-400 group-hover:translate-x-1 transition-transform pt-2">
              <span>Explore insight</span>
              <ArrowRight className="w-3 h-3" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
