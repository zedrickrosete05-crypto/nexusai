"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FileText, Trash2, Upload, MessageSquare, ArrowLeft } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useDocumentStore } from "@/store/documentStore";

const STATUS_STYLES: Record<string, string> = {
  completed: "text-emerald-400 bg-emerald-500/10",
  pending: "text-amber-400 bg-amber-500/10",
  processing: "text-amber-400 bg-amber-500/10",
  failed: "text-red-400 bg-red-500/10",
};

/**
 * Document management page: upload new files and view/delete existing ones.
 *
 * Redirects to /login if the user is not authenticated.
 */
export default function DocumentsPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const { documents, isLoading, isUploading, error, loadDocuments, upload, remove } =
    useDocumentStore();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    loadDocuments();
  }, [isAuthenticated, router, loadDocuments]);

  async function handleFileSelect(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await upload(file);
    } catch {
      // Error already captured in the store.
    }
    e.target.value = "";
  }

  async function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    try {
      await upload(file);
    } catch {
      // Error already captured in the store.
    }
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <header className="flex items-center justify-between border-b border-neutral-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <Link href="/chat" className="text-neutral-400 hover:text-white">
            <ArrowLeft size={18} />
          </Link>
          <h1 className="text-lg font-semibold">Documents</h1>
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
        {/* Upload zone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition ${
            dragActive
              ? "border-white bg-neutral-900"
              : "border-neutral-700 hover:border-neutral-500"
          }`}
        >
          <Upload size={28} className="mb-3 text-neutral-400" />
          <p className="text-sm text-neutral-300">
            {isUploading ? "Uploading and processing..." : "Click or drag a file to upload"}
          </p>
          <p className="mt-1 text-xs text-neutral-500">PDF, DOCX, or TXT — max 10MB</p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {error && <p className="mt-3 text-sm text-red-400">{error}</p>}

        {/* Document list */}
        <div className="mt-8">
          <h2 className="mb-3 text-sm font-medium text-neutral-400">
            Your documents {documents.length > 0 && `(${documents.length})`}
          </h2>

          {isLoading ? (
            <p className="text-sm text-neutral-500">Loading...</p>
          ) : documents.length === 0 ? (
            <p className="text-sm text-neutral-500">No documents uploaded yet.</p>
          ) : (
            <ul className="space-y-2">
              {documents.map((doc) => (
                <li
                  key={doc.id}
                  className="flex items-center justify-between rounded-xl border border-neutral-800 bg-neutral-900 px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <FileText size={18} className="text-neutral-400" />
                    <div>
                      <p className="text-sm font-medium">{doc.filename}</p>
                      <p className="text-xs text-neutral-500">
                        {doc.chunk_count} chunk{doc.chunk_count === 1 ? "" : "s"} ·{" "}
                        {doc.file_type.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        STATUS_STYLES[doc.status] || "text-neutral-400 bg-neutral-800"
                      }`}
                    >
                      {doc.status}
                    </span>
                    <button
                      onClick={() => remove(doc.id)}
                      className="text-neutral-500 hover:text-red-400"
                      title="Delete document"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}