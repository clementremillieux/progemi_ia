// src/components/ProjectHeader.tsx
"use client";

import React from "react";
import { ArrowLeft, Plus, Check } from "lucide-react";
import { Button } from "@/components/ui/Button";
import type { ProjectStatus } from "@/types";
import { StatusBadge } from "./ui/StatusBadge";
import { MenuDropdown } from "./ui/MenuDropdown";

interface Props {
  projectName: string;
  status: ProjectStatus;
  onBack: () => void;
  onImport: () => void;
  onValidate: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

export const ProjectHeader: React.FC<Props> = ({
  projectName,
  status,
  onBack,
  onImport,
  onValidate,
  onEdit,
  onDelete,
}) => {
  const menuItems = [
    {
      label: "Modifier le projet",
      onClick: onEdit,
    },
    {
      label: "Supprimer",
      onClick: onDelete,
    },
  ];

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)] bg-white">
      {/* Groupe gauche : back + titre + badge */}
      <div className="flex items-center gap-4">
        <button
          onClick={onBack}
          className="p-2 rounded-lg hover:bg-[var(--color-neutral-99)] transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-[var(--color-foreground)]" />
        </button>
        <h1 className="text-xl font-semibold text-[var(--color-foreground)] truncate">
          {projectName}
        </h1>
        <StatusBadge status={status} />
      </div>

      {/* Actions : Ajouter un lot / Valider / Menu */}
      <div className="flex gap-2 items-center">
       
        <Button
          label="Valider le projet"
          variant="filled"
          tone="primary"
          icon={<Check className="w-4 h-4" />}
          onClick={onValidate}
        />
        <MenuDropdown items={menuItems} />
      </div>
    </div>
  );
};
