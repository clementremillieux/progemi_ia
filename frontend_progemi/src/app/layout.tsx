// src/app/layout.tsx
import type { Metadata } from "next";
import "./tailwind.css"; // Changement ici
import { Poppins } from "next/font/google";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Mes projets",
  description: "Suivi des projets",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={poppins.variable}>
      <body className="font-sans bg-[var(--color-background)] text-[var(--color-foreground)]">{children}</body>
    </html>
  );
}