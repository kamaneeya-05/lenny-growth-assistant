import React, { useState, useEffect } from 'react';
import {
  X,
  Eye,
  Code,
  Copy,
  Check,
  Download,
  ShieldCheck,
  Sparkles,
  Smartphone,
  Tablet,
  Monitor,
  Maximize2,
  Minimize2,
  FileCode,
  Edit3
} from 'lucide-react';
import { Artifact } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ArtifactStudioProps {
  artifacts: Artifact[];
  activeArtifact: Artifact | null;
  onSelectArtifact: (art: Artifact) => void;
  onClose: () => void;
}

export const ArtifactStudio: React.FC<ArtifactStudioProps> = ({
  artifacts,
  activeArtifact,
  onSelectArtifact,
  onClose,
}) => {
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');
  const [deviceMode, setDeviceMode] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [editableContent, setEditableContent] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (activeArtifact) {
      setEditableContent(activeArtifact.content);
    }
  }, [activeArtifact]);

  if (!activeArtifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(editableContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = activeArtifact.artifact_type.toLowerCase() === 'html' ? 'html' : 'md';
    const mime = activeArtifact.artifact_type.toLowerCase() === 'html' ? 'text/html' : 'text/markdown';
    const blob = new Blob([editableContent], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeArtifact.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const isHtml = activeArtifact.artifact_type.toLowerCase() === 'html';

  return (
    <aside
      className={`bg-[#0c1220] border-l border-slate-800 flex flex-col h-screen shrink-0 shadow-2xl z-30 transition-all duration-200 ${
        isFullscreen ? 'fixed inset-0 w-full' : 'w-[560px]'
      }`}
    >
      {/* Studio Top Bar */}
      <div className="p-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <div className="w-7 h-7 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white flex items-center justify-center shrink-0 shadow-md shadow-indigo-600/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold text-white truncate" title={activeArtifact.title}>
                {activeArtifact.title}
              </h3>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                {activeArtifact.artifact_type}
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
              <span className="flex items-center gap-1 text-emerald-400">
                <ShieldCheck className="w-3 h-3" /> Sandboxed Execution
              </span>
              <span>•</span>
              <span className="flex items-center gap-1 text-slate-400">
                <Edit3 className="w-2.5 h-2.5" /> Live Editable
              </span>
            </div>
          </div>
        </div>

        {/* View Mode & Device Controls */}
        <div className="flex items-center gap-1.5 shrink-0">
          {/* Responsive viewport toggles for HTML */}
          {isHtml && viewMode === 'preview' && (
            <div className="hidden sm:flex bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs mr-1">
              <button
                onClick={() => setDeviceMode('desktop')}
                className={`p-1 rounded ${deviceMode === 'desktop' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                title="Desktop View (100%)"
              >
                <Monitor className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setDeviceMode('tablet')}
                className={`p-1 rounded ${deviceMode === 'tablet' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                title="Tablet View (768px)"
              >
                <Tablet className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setDeviceMode('mobile')}
                className={`p-1 rounded ${deviceMode === 'mobile' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                title="Mobile View (375px)"
              >
                <Smartphone className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Preview vs Code Toggle */}
          <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
                viewMode === 'preview' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setViewMode('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
                viewMode === 'code' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Code className="w-3 h-3" />
              <span>Editor</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title="Copy Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={handleDownload}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title="Download File"
          >
            <Download className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title="Close Studio"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Artifact Gallery Tabs (if multiple artifacts in session) */}
      {artifacts.length > 1 && (
        <div className="px-3 py-1.5 bg-slate-950/80 border-b border-slate-800/80 flex items-center gap-1.5 overflow-x-auto text-[11px]">
          <span className="text-[10px] text-slate-400 uppercase font-semibold mr-1">Gallery:</span>
          {artifacts.map((art) => {
            const isCurr = art.id === activeArtifact.id;
            return (
              <button
                key={art.id}
                onClick={() => onSelectArtifact(art)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg transition-all shrink-0 font-medium ${
                  isCurr
                    ? 'bg-slate-800 text-indigo-300 border border-indigo-500/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <FileCode className="w-3 h-3" />
                <span className="truncate max-w-[130px]">{art.title}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Main Workspace */}
      <div className="flex-1 overflow-hidden relative bg-[#090d16] flex items-center justify-center p-2">
        {viewMode === 'preview' ? (
          isHtml ? (
            /* HTML Preview with responsive device frame */
            <div
              className={`h-full transition-all duration-200 overflow-hidden ${
                deviceMode === 'mobile'
                  ? 'w-[375px] rounded-3xl border-4 border-slate-700 shadow-2xl bg-slate-900'
                  : deviceMode === 'tablet'
                  ? 'w-[768px] rounded-2xl border-4 border-slate-700 shadow-2xl bg-slate-900'
                  : 'w-full rounded-none border-none'
              }`}
            >
              <iframe
                title={activeArtifact.title}
                srcDoc={editableContent}
                sandbox="allow-scripts"
                className="w-full h-full border-none bg-slate-900"
              />
            </div>
          ) : (
            /* Markdown Preview */
            <div className="p-6 overflow-y-auto h-full w-full">
              <MarkdownRenderer content={editableContent} />
            </div>
          )
        ) : (
          /* Live Interactive Code Editor */
          <div className="h-full w-full flex flex-col bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
            <div className="px-4 py-2 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>Live Editor (changes reflect in Preview)</span>
              <span>{editableContent.length} chars</span>
            </div>
            <textarea
              value={editableContent}
              onChange={(e) => setEditableContent(e.target.value)}
              className="flex-1 w-full p-4 bg-transparent text-slate-200 font-mono text-xs resize-none outline-none leading-relaxed selection:bg-indigo-500/40"
              spellCheck={false}
            />
          </div>
        )}
      </div>

      {/* Security & Token Info Bar */}
      <div className="p-2.5 bg-slate-950/80 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1 text-slate-400">
          <ShieldCheck className="w-3 h-3 text-indigo-400" />
          Strict sandbox isolation (prevents parent token or storage exfiltration)
        </span>
        <span className="font-mono text-slate-400">
          {new Date(activeArtifact.created_at).toLocaleTimeString()}
        </span>
      </div>
    </aside>
  );
};
