import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="markdown-body text-xs leading-relaxed text-slate-200">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const codeString = String(children).replace(/\n$/, '');

            if (!inline && (match || codeString.includes('\n'))) {
              return <CodeBlock language={match ? match[1] : ''} code={codeString} />;
            }

            return (
              <code className="font-mono text-xs bg-slate-800 text-indigo-300 px-1.5 py-0.5 rounded border border-slate-700/60" {...props}>
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="overflow-x-auto my-3 rounded-xl border border-slate-800 shadow-sm">
                <table className="w-full text-left border-collapse text-xs">
                  {children}
                </table>
              </div>
            );
          },
          th({ children }) {
            return (
              <th className="bg-slate-800/90 text-slate-200 font-semibold p-2.5 border-b border-slate-700 text-xs tracking-wide">
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td className="p-2.5 border-b border-slate-800/80 text-slate-300 text-xs">
                {children}
              </td>
            );
          },
          blockquote({ children }) {
            return (
              <blockquote className="border-l-4 border-indigo-500 pl-4 py-1.5 my-3 bg-indigo-950/20 rounded-r-lg text-slate-200 italic">
                {children}
              </blockquote>
            );
          },
          h1({ children }) {
            return (
              <h1 className="text-lg font-bold text-white mt-5 mb-2.5 border-b border-slate-800 pb-2">
                {children}
              </h1>
            );
          },
          h2({ children }) {
            return (
              <h2 className="text-base font-bold text-white mt-4 mb-2">
                {children}
              </h2>
            );
          },
          h3({ children }) {
            return (
              <h3 className="text-sm font-semibold text-slate-100 mt-3 mb-1.5">
                {children}
              </h3>
            );
          },
          ul({ children }) {
            return <ul className="list-disc list-outside pl-5 my-2.5 space-y-1 text-slate-300">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal list-outside pl-5 my-2.5 space-y-1 text-slate-300">{children}</ol>;
          },
          li({ children }) {
            return <li className="leading-relaxed">{children}</li>;
          },
          strong({ children }) {
            return <strong className="font-semibold text-white">{children}</strong>;
          },
          p({ children }) {
            return <p className="my-2.5 leading-relaxed text-slate-300">{children}</p>;
          },
          hr() {
            return <hr className="my-4 border-slate-800" />;
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

const CodeBlock: React.FC<{ language: string; code: string }> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-3 rounded-xl border border-slate-800 bg-slate-950 overflow-hidden group shadow-lg">
      <div className="flex items-center justify-between px-3.5 py-1.5 bg-slate-900 border-b border-slate-800 text-[11px] font-mono text-slate-400">
        <span className="uppercase font-semibold text-indigo-400">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-white transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400 font-sans">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span className="font-sans">Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-[11px] font-mono text-slate-200 leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
};
