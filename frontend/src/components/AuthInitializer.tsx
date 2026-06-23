"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";

/**
 * Rehydrates authentication state from localStorage on initial app load.
 *
 * Renders nothing visible; must be mounted once near the root layout
 * so auth state is ready before any page renders.
 */
export function AuthInitializer() {
  const initializeFromStorage = useAuthStore((state) => state.initializeFromStorage);

  useEffect(() => {
    initializeFromStorage();
  }, [initializeFromStorage]);

  return null;
}