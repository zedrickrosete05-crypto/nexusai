"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

interface CodeBlockProps {
  language?: string;
  children: string;
}

/**
 * Renders a syntax-highlighted code block with a copy-to-clipboard button.
 *
 * Used as a custom renderer for fenced code blocks within ReactMarkdown,
 * styled via highlight.js classes applied by rehype-highlight.
 */
export function CodeBlock({ language, children }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="my-3 overflow-hidden rounded-lg border border-neutral-700">
      <div className="flex items-center justify-between bg-neutral-800 px-3 py-1.5">
        <span className="text-xs font-medium text-neutral-400">{language || "text"}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-neutral-400 hover:text-white"
        >
          {copied ? (
            <>
              <Check size={12} /> Copied
            </>
          ) : (
            <>
              <Copy size={12} /> Copy
            </>
          )}
        </button>
      </div>
      <pre className="overflow-x-auto bg-neutral-900 p-4 text-sm">
        <code className={language ? `hljs language-${language}` : "hljs"}>{children}</code>
      </pre>
    </div>
  );
}