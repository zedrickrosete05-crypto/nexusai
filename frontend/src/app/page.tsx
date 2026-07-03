"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

/**
 * Root page: redirects to /chat if authenticated, or /login otherwise.
 *
 * Waits for auth state to be rehydrated from storage before redirecting,
 * to avoid briefly redirecting a logged-in user to /login.
 */
export default function Home() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isInitialized = useAuthStore((state) => state.isInitialized);

  useEffect(() => {
    if (!isInitialized) return;
    router.replace(isAuthenticated ? "/chat" : "/login");
  }, [isInitialized, isAuthenticated, router]);

  return null;
}