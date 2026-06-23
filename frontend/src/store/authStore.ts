/**
 * Global authentication state store using Zustand.
 *
 * Persists the access token to localStorage and exposes login/logout
 * actions and the current user to any component in the app.
 */

import { create } from "zustand";
import { loginUser, registerUser, type User } from "@/lib/api";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  initializeFromStorage: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = await loginUser(email, password);
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      set({
        accessToken: tokens.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err) {
      set({
        isLoading: false,
        error: "Invalid email or password.",
      });
      throw err;
    }
  },

  register: async (email: string, password: string, fullName: string) => {
    set({ isLoading: true, error: null });
    try {
      await registerUser(email, password, fullName);
      set({ isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: "Registration failed. Email may already be in use.",
      });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  initializeFromStorage: () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      set({ accessToken: token, isAuthenticated: true });
    }
  },
}));