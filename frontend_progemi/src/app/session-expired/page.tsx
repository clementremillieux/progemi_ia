"use client";

import { useEffect } from "react";
import { Header } from "@/components/ui/Header";
import { useRouter } from "next/navigation";

export default function SessionExpired() {
  const router = useRouter();

  useEffect(() => {
    const id = setInterval(() => {
      if (document.cookie.includes("access_token=")) router.replace("/");
    }, 3_000);                 // vérifie toutes les 3 s
    return () => clearInterval(id);
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-8 bg-[var(--color-neutral-99)]">
      <Header title="Session expirée" hideAction />
      <div className="space-y-4 text-center max-w-md">
        <h2 className="text-2xl font-semibold text-[var(--color-foreground)]">
          La session est expirée
        </h2>
        <p className="text-[var(--color-foreground-muted)]">
          Veuillez vous reconnecter depuis l’application&nbsp;<b>PROGEMI</b>.
        </p>
      </div>
    </div>
  );
}
