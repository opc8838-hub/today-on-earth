"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";

export default function AdminLoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/admin-auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (res.ok) {
        router.push("/admin");
      } else {
        setError("Incorrect password");
      }
    } catch {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-earth-900">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm p-8 bg-earth-800 border border-earth-700 rounded-lg"
      >
        <h1 className="text-lg font-serif text-earth-100 text-center mb-6">
          Admin &middot; 管理
        </h1>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full px-4 py-2 rounded-md bg-earth-900 border border-earth-600 text-earth-100 text-sm placeholder:text-earth-600 focus:outline-none focus:border-earth-blue mb-4"
          autoFocus
        />
        {error && (
          <p className="text-xs text-red-400 mb-4 text-center">{error}</p>
        )}
        <Button
          type="submit"
          className="w-full"
          disabled={loading || !password}
        >
          {loading ? "Verifying…" : "Enter"}
        </Button>
      </form>
    </div>
  );
}
