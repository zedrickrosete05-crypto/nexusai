"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Send, Plus, MessageSquare, Bot } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CodeBlock } from "@/components/chat/CodeBlock";
import "highlight.js/styles/github-dark.css";
import { useAuthStore } from "@/store/authStore";
import { useChatStore } from "@/store/chatStore";
import Link from "next/link";
import { FileText } from "lucide-react";

/**
 * Main chat dashboard: conversation sidebar, message thread, and input.
 *
 * Redirects to /login if the user is not authenticated.
 */
export default function ChatPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const logout = useAuthStore((state) => state.logout);

  const {
    conversations,
    activeConversationId,
    messages,
    isSending,
    loadConversations,
    selectConversation,
    startNewConversation,
    send,
  } = useChatStore();

  const [input, setInput] = useState("");
  const [useAgent, setUseAgent] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    loadConversations();
  }, [isAuthenticated, router, loadConversations]);

  async function handleNewConversation() {
    await startNewConversation();
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const content = input.trim();
    if (!content) return;

    if (!activeConversationId) {
      await startNewConversation();
    }
    setInput("");
    await send(content, useAgent);
  }

  if (!isAuthenticated) return null;

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-neutral-800 bg-neutral-900">
        <div className="p-4">
          <button
            onClick={handleNewConversation}
            className="flex w-full items-center gap-2 rounded-lg border border-neutral-700 px-3 py-2 text-sm hover:bg-neutral-800"
          >
            <Plus size={16} />
            New chat
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-2">
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => selectConversation(c.id)}
              className={`flex w-full items-center gap-2 truncate rounded-lg px-3 py-2 text-left text-sm ${
                c.id === activeConversationId
                  ? "bg-neutral-800 text-white"
                  : "text-neutral-400 hover:bg-neutral-800/50"
              }`}
            >
              <MessageSquare size={14} className="shrink-0" />
              <span className="truncate">{c.title}</span>
            </button>
          ))}
        </nav>

        <div className="border-t border-neutral-800 p-4 space-y-1">
          <Link
            href="/documents"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-neutral-400 hover:bg-neutral-800"
          >
            <FileText size={14} />
            Documents
          </Link>
          <button
            onClick={logout}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-neutral-400 hover:bg-neutral-800"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main chat area */}
      <div className="flex flex-1 flex-col">
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-neutral-500">
              Start a conversation
            </div>
          ) : (
            <div className="mx-auto max-w-2xl space-y-6">
              {messages.map((m) => (
                <div key={m.id} className={m.role === "user" ? "text-right" : ""}>
                  <div
                    className={`inline-block max-w-[80%] rounded-2xl px-4 py-2 text-left ${
                      m.role === "user"
                        ? "bg-white text-neutral-900"
                        : "bg-neutral-800 text-neutral-100"
                    }`}
                  >
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          code(props) {
                            const { className, children, ...rest } = props;
                            const match = /language-(\w+)/.exec(className || "");
                            const isInline = !match;

                            if (isInline) {
                              return (
                                <code
                                  className="rounded bg-neutral-700 px-1 py-0.5 text-sm"
                                  {...rest}
                                >
                                  {children}
                                </code>
                              );
                            }

                            return (
                              <CodeBlock language={match[1]}>
                                {String(children).replace(/\n$/, "")}
                              </CodeBlock>
                            );
                          },
                        }}
                      >
                        {m.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))}
              {isSending && (
                <div className="text-sm text-neutral-500">NexusAI is thinking...</div>
              )}
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="border-t border-neutral-800 p-4">
          <div className="mx-auto flex max-w-2xl items-center gap-2">
            <button
              type="button"
              onClick={() => setUseAgent((v) => !v)}
              title="Toggle agent mode"
              className={`flex items-center gap-1 rounded-lg border px-3 py-2 text-xs ${
                useAgent
                  ? "border-emerald-500 text-emerald-400"
                  : "border-neutral-700 text-neutral-400"
              }`}
            >
              <Bot size={14} />
              Agent
            </button>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message NexusAI..."
              className="flex-1 rounded-lg border border-neutral-700 bg-neutral-900 px-4 py-2 text-white placeholder-neutral-500 outline-none focus:border-neutral-500"
            />
            <button
              type="submit"
              disabled={isSending || !input.trim()}
              className="rounded-lg bg-white p-2 text-neutral-900 disabled:opacity-40"
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}