import React, { useState } from 'react';
import { Cpu, ChevronDown, Check, Layout, AlertCircle } from 'lucide-react';
import { ModelsResponse, ModelInfo } from '../types';

interface ChatHeaderProps {
  title: string;
  modelsData: ModelsResponse | null;
  selectedProvider: string;
  selectedModel: string;
  onSelectModel: (provider: string, model: string) => void;
  hasArtifact: boolean;
  isArtifactOpen: boolean;
  onToggleArtifact: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  title,
  modelsData,
  selectedProvider,
  selectedModel,
  onSelectModel,
  hasArtifact,
  isArtifactOpen,
  onToggleArtifact,
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="h-14 border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-20">
      {/* Session Title */}
      <div className="flex items-center gap-3 min-w-0">
        <h2 className="text-sm font-semibold text-white truncate max-w-md">
          {title}
        </h2>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-3">
        {/* Model Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700/80 hover:border-indigo-500/50 text-xs font-medium text-slate-200 transition-all shadow-sm active:scale-95"
          >
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-mono text-[11px] text-white">
              {selectedProvider.toUpperCase()}: {selectedModel}
            </span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {dropdownOpen && (
            <>
              <div
                className="fixed inset-0 z-30"
                onClick={() => setDropdownOpen(false)}
              />
              <div className="absolute right-0 mt-2 w-80 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-40 space-y-1">
                <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-300">
                  Select Model Provider
                </div>

                {modelsData?.models.map((m: ModelInfo) => {
                  const isSelected =
                    m.provider === selectedProvider &&
                    (m.name.includes(selectedModel) || m.id.includes(selectedModel));

                  return (
                    <button
                      key={m.id}
                      onClick={() => {
                        const modelName = m.id.includes(':') ? m.id.split(':')[1] : m.id;
                        onSelectModel(m.provider, modelName);
                        setDropdownOpen(false);
                      }}
                      className={`w-full text-left p-2.5 rounded-xl text-xs flex items-start justify-between transition-colors ${
                        isSelected
                          ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                          : 'hover:bg-slate-800/80 text-slate-300'
                      }`}
                    >
                      <div className="space-y-0.5 min-w-0 pr-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white">{m.name}</span>
                          {m.is_local && (
                            <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                              Local
                            </span>
                          )}
                          {!m.is_available && (
                            <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                              Offline
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 truncate">
                          {m.description}
                        </p>
                      </div>
                      {isSelected && (
                        <Check className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                      )}
                    </button>
                  );
                })}

                {/* Ollama Status Notice */}
                {modelsData?.ollama_status && !modelsData.ollama_status.available && (
                  <div className="p-2 mt-1 rounded-xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span>
                      Ollama offline at localhost:11434. Using high-fidelity demo/mock provider.
                    </span>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Artifact Studio Toggle Button */}
        {hasArtifact && (
          <button
            onClick={onToggleArtifact}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              isArtifactOpen
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30 ring-1 ring-indigo-400'
                : 'bg-slate-900 border border-slate-750 text-indigo-300 hover:bg-slate-800'
            }`}
          >
            <Layout className="w-3.5 h-3.5" />
            <span>Artifact Studio</span>
          </button>
        )}
      </div>
    </header>
  );
};
