"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Login() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const response = await fetch(api + "/api/v1/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: form.get("username"),
        password: form.get("password"),
      }),
    });
    const data = await response.json();
    setLoading(false);
    if (!response.ok) {
      setError(data.non_field_errors?.[0] ?? "Unable to sign in");
      return;
    }
    localStorage.setItem("dragonfly_token", data.token);
    router.push("/instruments");
  }

  return <section className="mx-auto max-w-md py-12">
    <p className="text-xs font-black tracking-[.22em] text-[#50f2a7]">ACCOUNT ACCESS</p><h1 className="mt-3 text-5xl font-black tracking-[-.04em]">Sign in</h1>
    <form onSubmit={submit} className="mt-8 grid gap-5 rounded-2xl border border-[#1c312b] bg-[#091210] p-7">
      <label className="grid gap-2 text-sm text-[#9eb3aa]">Username<input className="rounded-xl border border-[#29473e] bg-[#050b0a] px-4 py-3 text-white outline-none focus:border-[#50f2a7]" name="username" autoComplete="username" required /></label>
      <label className="grid gap-2 text-sm text-[#9eb3aa]">Password<input className="rounded-xl border border-[#29473e] bg-[#050b0a] px-4 py-3 text-white outline-none focus:border-[#50f2a7]" name="password" type="password" autoComplete="current-password" required /></label>
      {error && <p className="text-sm text-rose-400">{error}</p>}
      <button className="rounded-xl bg-[#50f2a7] px-5 py-3 font-black text-[#04110b] disabled:opacity-60" disabled={loading}>{loading ? "Signing in…" : "Sign in"}</button>
    </form>
  </section>;
}
