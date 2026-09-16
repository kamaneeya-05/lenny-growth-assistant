import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Feather,
  FileCode,
  Zap,
  Sliders,
  CheckCircle,
  HelpCircle,
  ChevronUp
} from 'lucide-react';

interface ComposerProps {
  onSend: (
    message: string,
    options?: { generate_ship30_essay?: boolean; generate_artifact?: boolean; artifact_type?: string }
  ) => void;
  isLoading: boolean;
}

export const Composer: React.FC<ComposerProps> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');
  const [showSkillsMenu, setShowSkillsMenu] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = (options?: { generate_ship30_essay?: boolean; generate_artifact?: boolean; artifact_type?: string }) => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim(), options);
    setInput('');
    setShowSkillsMenu(false);
  };

  const skillsList = [
    {
      name: "Ship 30 for 30 Essay (~1,250 words)",
      icon: <Feather className="w-3.5 h-3.5 text-indigo-400" />,
      action: () => {
        const text = input.trim() || "Turn Lenny's best advice on finding product-market fit into a Ship 30 for 30 essay";
        onSend(text, { generate_ship30_essay: true });
        setInput('');
        setShowSkillsMenu(false);
      },
    },
    {
      name: "HTML Product Strategy One-Pager",
      icon: <FileCode className="w-3.5 h-3.5 text-emerald-400" />,
      action: () => {
        const text = input.trim() || "Create an HTML product strategy one-pager framework based on this topic";
        onSend(text, { generate_artifact: true, artifact_type: 'html' });
        setInput('');
        setShowSkillsMenu(false);
      },
    },
    {
      name: "Elena Verna B2B Growth Loops Teardown",
      icon: <Zap className="w-3.5 h-3.5 text-amber-400" />,
      action: () => {
        onSend("How does Elena Verna design B2B growth loops and product-led monetization?");
        setInput('');
        setShowSkillsMenu(false);
      },
    },
    {
      name: "Founder Mode & Product Sense Teardown",
      icon: <Sparkles className="w-3.5 h-3.5 text-rose-400" />,
      action: () => {
        onSend("Synthesize Adam Mosseri, Stewart Butterfield, and Eric Ries on product taste, conviction, and Founder Mode.");
        setInput('');
        setShowSkillsMenu(false);
      },
    },
  ];

  return (
    <div className="p-4 bg-gradient-to-t from-[#090d16] via-[#090d16]/95 to-transparent shrink-0">
      <div className="max-w-3xl mx-auto space-y-2">
        {/* Quick Skills Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <button
            onClick={() => setShowSkillsMenu(!showSkillsMenu)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-750 hover:border-indigo-500/60 text-indigo-300 hover:text-white transition-all shrink-0 hover:bg-slate-800 active:scale-95 font-medium"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Skills Library</span>
            <ChevronUp className={`w-3 h-3 transition-transform ${showSkillsMenu ? 'rotate-180' : ''}`} />
          </button>

          <button
            onClick={() => skillsList[0].action()}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 hover:border-indigo-500/60 text-slate-300 hover:text-white transition-all shrink-0 hover:bg-slate-850 active:scale-95"
          >
            <Feather className="w-3.5 h-3.5 text-indigo-400" />
            <span>Ship 30 Essay (~1,250 words)</span>
          </button>

          <button
            onClick={() => skillsList[1].action()}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 hover:border-emerald-500/60 text-slate-300 hover:text-white transition-all shrink-0 hover:bg-slate-850 active:scale-95"
          >
            <FileCode className="w-3.5 h-3.5 text-emerald-400" />
            <span>HTML Strategy One-Pager</span>
          </button>
        </div>

        {/* Skills Library Popover */}
        {showSkillsMenu && (
          <div className="p-2 rounded-2xl bg-slate-900 border border-slate-750 shadow-2xl space-y-1 animate-in slide-in-from-bottom-2 duration-150">
            <div className="px-3 py-1 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Specialized Product Management Skills
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
              {skillsList.map((s, idx) => (
                <button
                  key={idx}
                  onClick={s.action}
                  className="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-slate-800 text-left text-xs text-slate-200 hover:text-white transition-colors border border-transparent hover:border-slate-700"
                >
                  <div className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 shrink-0">
                    {s.icon}
                  </div>
                  <span className="font-medium truncate">{s.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Textarea Composer */}
        <div className="relative rounded-2xl bg-slate-900/90 border border-slate-750 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/30 shadow-xl transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="Ask a product or growth question grounded in Lenny's Podcast..."
            rows={2}
            className="w-full bg-transparent p-4 pr-14 text-xs text-white placeholder-slate-400 resize-none outline-none leading-relaxed"
          />

          <div className="absolute right-3 bottom-3">
            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || isLoading}
              className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all ${
                input.trim() && !isLoading
                  ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 active:scale-95'
                  : 'bg-slate-800 text-slate-400 cursor-not-allowed'
              }`}
              title="Send Message (Enter)"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Footer info */}
        <div className="flex items-center justify-between px-2 text-[11px] text-slate-400 font-medium">
          <span>Enter to send, Shift + Enter for newline</span>
          <span>100% transcript-grounded citations</span>
        </div>
      </div>
    </div>
  );
};
