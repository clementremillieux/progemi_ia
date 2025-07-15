"use client";

import React from "react";
import Link from "next/link";
import { Copy, Trash2 } from "lucide-react";
import type { ProjectStatus } from "@/types";
import { StatusBadge } from "./ui/StatusBadge";
import { MenuDropdown, MenuItem } from "./ui/MenuDropdown";

interface Props {
  projectId: string;
  title: string;
  status: ProjectStatus;
  devisCount: number;
  onDuplicate?: (projectId: string) => void;
  onDelete?: (projectId: string) => void;
}

export const ProjectCard: React.FC<Props> = ({
  projectId,
  title,
  status,
  devisCount,
  onDuplicate = () => {},
  onDelete = () => {},
}) => {
  const formatAmt = (n: number) =>
    new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(n);

  const href = `/projects/${projectId}?title=${encodeURIComponent(
    title
  )}&status=${status}`;

  const menuItems: MenuItem[] = [
    {
      label: "Dupliquer le projet",
      icon: <Copy size={16} />,
      onClick: () => onDuplicate(projectId),
    },
    {
      label: "Supprimer le projet",
      icon: <Trash2 size={16} />,
      className: "text-red-600",
      onClick: () => onDelete(projectId),
    },
  ];

  return (
    <div className="relative bg-white rounded-2xl border border-[var(--color-border)] p-6 hover:shadow-sm transition">
      {/* Top: Status badge + menu dropdown */}
      <div className="flex items-center justify-between">
        <StatusBadge status={status} />
        <MenuDropdown
          items={menuItems}
          className="z-10"
          triggerVariant="tonal"
          triggerFlavor="neutral"
        />
      </div>

      {/* Main content with link */}
      <Link href={href} className="block mt-4">
        <h2 className="text-lg font-semibold text-[var(--color-foreground)] truncate">
          {title}
        </h2>
        <hr className="border-t border-[var(--color-border)] my-4 -mx-6" />
        <div className="flex justify-between">
          <div>
            <p className="text-sm text-[var(--color-neutral-60)]">Devis</p>
            <p className="text-xl font-semibold text-[var(--color-foreground)]">
              {devisCount}
            </p>
          </div>
        </div>
      </Link>
    </div>
  );
};
