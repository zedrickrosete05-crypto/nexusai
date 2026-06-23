/**
 * Centralized API client for communicating with the NexusAI backend.
 *
 * Automatically attaches the JWT access token to every request and
 * provides typed helper functions for each backend endpoint.
 */

import axios, { type AxiosInstance } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach the access token to every outgoing request, if present.
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// === Types ===

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  total_tokens: number;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface DocumentMeta {
  id: string;
  filename: string;
  file_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
}

// === Auth ===

export async function registerUser(
  email: string,
  password: string,
  fullName: string
): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/register", {
    email,
    password,
    full_name: fullName,
  });
  return data;
}

export async function loginUser(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

// === Chat ===

export async function createConversation(title = "New Conversation"): Promise<Conversation> {
  const { data } = await apiClient.post<Conversation>("/chat/conversations", { title });
  return data;
}

export async function listConversations(): Promise<Conversation[]> {
  const { data } = await apiClient.get<Conversation[]>("/chat/conversations");
  return data;
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const { data } = await apiClient.get<ConversationDetail>(
    `/chat/conversations/${conversationId}`
  );
  return data;
}

export async function sendMessage(conversationId: string, content: string): Promise<Message> {
  const { data } = await apiClient.post<Message>(
    `/chat/conversations/${conversationId}/messages`,
    { content }
  );
  return data;
}

export async function sendAgentMessage(
  conversationId: string,
  content: string
): Promise<Message> {
  const { data } = await apiClient.post<Message>(
    `/chat/conversations/${conversationId}/agent-messages`,
    { content }
  );
  return data;
}

// === Documents ===

export async function uploadDocument(file: File): Promise<DocumentMeta> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<DocumentMeta>("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listDocuments(): Promise<DocumentMeta[]> {
  const { data } = await apiClient.get<DocumentMeta[]>("/documents");
  return data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}