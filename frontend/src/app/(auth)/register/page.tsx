"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";

/**
 * Registration page allowing new users to create an account.
 *
 * On success, redirects to the login page so the user can sign in
 * with their new credentials.
 */
export default function RegisterPage() {
  const router = useRouter();
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const error = useAuthStore((state) => state.error);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      await register(email, password, fullName);
      router.push("/login");
    } catch {
      // Error is already captured in the auth store; nothing more to do.
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-950 px-4">
      <div className="w-full max-w-sm rounded-2xl border border-neutral-800 bg-neutral-900 p-8 shadow-xl">
        <h1 className="mb-1 text-2xl font-semibold text-white">Create your account</h1>
        <p className="mb-6 text-sm text-neutral-400">Get started with NexusAI</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="mb-1 block text-sm text-neutral-300">
              Full name
            </label>
            <input
              id="fullName"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-white placeholder-neutral-500 outline-none focus:border-neutral-500"
              placeholder="Jane Doe"
            />
          </div>

          <div>
            <label htmlFor="email" className="mb-1 block text-sm text-neutral-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-white placeholder-neutral-500 outline-none focus:border-neutral-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm text-neutral-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-white placeholder-neutral-500 outline-none focus:border-neutral-500"
              placeholder="At least 8 characters"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-white py-2 font-medium text-neutral-900 transition hover:bg-neutral-200 disabled:opacity-50"
          >
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-neutral-400">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-white hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}