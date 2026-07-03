"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  MessageSquare,
  FileText,
  Bot,
  MessagesSquare,
  ArrowLeft,
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { getDashboardStats, type DashboardStats } from "@/lib/api";

/**
 * Dashboard page showing aggregated user activity statistics.
 *
 * Redirects to /login if the user is not authenticated.
 */
export default function DashboardPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isInitialized = useAuthStore((state) => state.isInitialized);

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isInitialized) return;
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    getDashboardStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [isInitialized, isAuthenticated, router]);

  if (!isInitialized || !isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <header className="flex items-center justify-between border-b border-neutral-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <Link href="/chat" className="text-neutral-400 hover:text-white">
            <ArrowLeft size={18} />
          </Link>
          <h1 className="text-lg font-semibold">Dashboard</h1>
        </div>
        <Link
          href="/chat"
          className="flex items-center gap-1 text-sm text-neutral-400 hover:text-white"
        >
          <MessageSquare size={14} />
          Back to chat
        </Link>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        <h2 className="mb-6 text-xl font-semibold">Your Activity</h2>

        {isLoading ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="animate-pulse rounded-2xl border border-neutral-800 bg-neutral-900 p-6"
              />
            ))}
          </div>
        ) : stats ? (
          <>
            {/* Stats grid */}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard
                icon={<MessageSquare size={20} />}
                label="Conversations"
                value={stats.conversation_count}
                color="text-blue-400"
              />
              <StatCard
                icon={<MessagesSquare size={20} />}
                label="Total Messages"
                value={stats.message_count}
                color="text-purple-400"
              />
              <StatCard
                icon={<Bot size={20} />}
                label="AI Responses"
                value={stats.assistant_message_count}
                color="text-emerald-400"
              />
              <StatCard
                icon={<FileText size={20} />}
                label="Documents"
                value={stats.document_count}
                color="text-amber-400"
              />
            </div>

            {/* Activity breakdown */}
            <div className="mt-8 rounded-2xl border border-neutral-800 bg-neutral-900 p-6">
              <h3 className="mb-4 text-sm font-medium text-neutral-400">
                Activity Breakdown
              </h3>
              <div className="space-y-3">
                <ActivityBar
                  label="User messages"
                  value={stats.message_count - stats.assistant_message_count}
                  max={stats.message_count}
                  color="bg-blue-500"
                />
                <ActivityBar
                  label="AI responses"
                  value={stats.assistant_message_count}
                  max={stats.message_count}
                  color="bg-emerald-500"
                />
                <ActivityBar
                  label="Documents uploaded"
                  value={stats.document_count}
                  max={Math.max(stats.document_count, 1)}
                  color="bg-amber-500"
                />
              </div>
            </div>

            {/* Quick actions */}
            <div className="mt-8 grid grid-cols-2 gap-4">
              <Link
                href="/chat"
                className="flex items-center gap-3 rounded-2xl border border-neutral-800 bg-neutral-900 p-5 hover:border-neutral-600 transition"
              >
                <MessageSquare size={20} className="text-blue-400" />
                <div>
                  <p className="font-medium">Start chatting</p>
                  <p className="text-xs text-neutral-500">Ask anything</p>
                </div>
              </Link>
              <Link
                href="/documents"
                className="flex items-center gap-3 rounded-2xl border border-neutral-800 bg-neutral-900 p-5 hover:border-neutral-600 transition"
              >
                <FileText size={20} className="text-amber-400" />
                <div>
                  <p className="font-medium">Upload document</p>
                  <p className="text-xs text-neutral-500">Add to your knowledge base</p>
                </div>
              </Link>
            </div>
          </>
        ) : (
          <p className="text-sm text-neutral-500">Failed to load statistics.</p>
        )}
      </main>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
      <div className={`mb-3 ${color}`}>{icon}</div>
      <p className="text-2xl font-bold">{value.toLocaleString()}</p>
      <p className="mt-1 text-xs text-neutral-500">{label}</p>
    </div>
  );
}

interface ActivityBarProps {
  label: string;
  value: number;
  max: number;
  color: string;
}

function ActivityBar({ label, value, max, color }: ActivityBarProps) {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-neutral-400">
        <span>{label}</span>
        <span>{value.toLocaleString()}</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-neutral-800">
        <div
          className={`h-1.5 rounded-full ${color} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}