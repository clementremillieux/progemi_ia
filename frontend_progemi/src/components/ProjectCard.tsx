"use client";

import React from "react";
import Link from "next/link";
import { StatusBadge } from "./ui/StatusBadge";
import { MenuDropdown, MenuItem } from "./ui/MenuDropdown";
import { Edit2 } from "lucide-react";

interface Props {
  projectId: string;
  title: string;
  packsCount: number;
  isPackToChoose: boolean;
  status: string;
  devisCount: number;
  onEditPacks: (projectId: string) => void;
}

export const ProjectCard: React.FC<Props> = ({
  projectId,
  title,
  packsCount,
  isPackToChoose,
  status,
  devisCount,
  onEditPacks,              // ✅ extrait maintenant
}) => {
  const href = `/projects/${projectId}?title=${encodeURIComponent(
    title,
  )}&status=${status}`;

  const lotsLabel = packsCount === 1 ? "Lot" : "Lots";

  const menuItems: MenuItem[] = [
    {
      label: "Modifier les lots",
      icon: <Edit2 className="w-4 h-4" /> ,
      onClick: () => onEditPacks(projectId),
    },
  ];

  return (
    <article className="relative bg-white rounded-2xl border border-[var(--color-border)] p-6 hover:shadow-sm transition">
      {/* En‑tête : badge + menu */}
      <div className="flex justify-between">
        <StatusBadge status={status} />
        <MenuDropdown items={menuItems} triggerVariant="tonal" triggerFlavor="neutral" />
      </div>

      {/* Contenu cliquable */}
      <Link href={href} className="block mt-4 space-y-4">
        {/* Titre */}
        <h2 className="text-lg font-semibold text-[var(--color-foreground)] truncate">
          {title}
        </h2>

        <hr className="border-t border-[var(--color-border)] -mx-6" />

        {/* Infos devis / lots */}
        <div className="flex justify-between text-sm text-[var(--color-neutral-60)]">
          <div className="space-y-1">
            <p>Devis</p>
            <p className="text-xl font-semibold text-[var(--color-foreground)]">
              {devisCount}
            </p>
          </div>

          <div className="space-y-1 text-right">
            <p>{lotsLabel}</p>
            <p className="text-xl font-semibold text-[var(--color-foreground)]">
              {packsCount}
            </p>
          </div>
        </div>

        {/* Badge “Lot(s) à configurer” */}
        {isPackToChoose && (
          <span className="inline-block rounded-full bg-orange-100 text-orange-800 text-xs px-3 py-0.5">
            {packsCount === 1 ? "Lot à configurer" : "Lots à configurer"}
          </span>
        )}
      </Link>
    </article>
  );
};
