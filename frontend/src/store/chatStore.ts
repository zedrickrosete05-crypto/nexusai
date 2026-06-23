/**
 * Global chat state store using Zustand.
 *
 * Manages the list of conversations, the currently active conversation's
 * messages, and actions for creating conversations and sending messages.
 */

import { create } from "zustand";
import {
  createConversation,
  getConversation,
  listConversations,
  sendMessage,
  sendAgentMessage,
  type Conversation,
  type Message,
} from "@/lib/api";

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  isLoadingConversations: boolean;
  isSending: boolean;

  loadConversations: () => Promise<void>;
  selectConversation: (conversationId: string) => Promise<void>;
  startNewConversation: () => Promise<string>;
  send: (content: string, useAgent: boolean) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  messages: [],
  isLoadingConversations: false,
  isSending: false,

  loadConversations: async () => {
    set({ isLoadingConversations: true });
    const conversations = await listConversations();
    set({ conversations, isLoadingConversations: false });
  },

  selectConversation: async (conversationId: string) => {
    const detail = await getConversation(conversationId);
    set({ activeConversationId: conversationId, messages: detail.messages });
  },

  startNewConversation: async () => {
    const conversation = await createConversation();
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      activeConversationId: conversation.id,
      messages: [],
    }));
    return conversation.id;
  },

  send: async (content: string, useAgent: boolean) => {
    const { activeConversationId } = get();
    if (!activeConversationId) return;

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      total_tokens: 0,
      created_at: new Date().toISOString(),
    };
    set((state) => ({ messages: [...state.messages, userMessage], isSending: true }));

    try {
      const assistantMessage = useAgent
        ? await sendAgentMessage(activeConversationId, content)
        : await sendMessage(activeConversationId, content);
      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isSending: false,
      }));
    } catch (err) {
      set({ isSending: false });
      throw err;
    }
  },
}));