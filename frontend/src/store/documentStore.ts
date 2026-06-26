/**
 * Global document state store using Zustand.
 *
 * Manages the list of uploaded documents and actions for uploading
 * and deleting them.
 */

import { create } from "zustand";
import {
  deleteDocument,
  listDocuments,
  uploadDocument,
  type DocumentMeta,
} from "@/lib/api";

interface DocumentState {
  documents: DocumentMeta[];
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;

  loadDocuments: () => Promise<void>;
  upload: (file: File) => Promise<void>;
  remove: (documentId: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  isLoading: false,
  isUploading: false,
  error: null,

  loadDocuments: async () => {
    set({ isLoading: true, error: null });
    try {
      const documents = await listDocuments();
      set({ documents, isLoading: false });
    } catch {
      set({ isLoading: false, error: "Failed to load documents." });
    }
  },

  upload: async (file: File) => {
    set({ isUploading: true, error: null });
    try {
      const document = await uploadDocument(file);
      set((state) => ({ documents: [document, ...state.documents], isUploading: false }));
    } catch {
      set({ isUploading: false, error: "Upload failed. Check file type and size." });
      throw new Error("Upload failed");
    }
  },

  remove: async (documentId: string) => {
    await deleteDocument(documentId);
    set((state) => ({
      documents: state.documents.filter((d) => d.id !== documentId),
    }));
  },
}));