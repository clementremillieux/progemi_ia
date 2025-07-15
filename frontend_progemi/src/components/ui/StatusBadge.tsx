// src/components/ui/StatusBadge.tsx
"use client";

import React from "react";
import type { Lot } from "@/types";
import type { ProjectStatus } from "@/types";

export type Status = ProjectStatus | Lot["status"];

interface StatusBadgeProps {
  status: Status;
}

const styles: Record<Status, string> = {
  // statuts de Projet
  valide:      "bg-[var(--color-success-95)] text-[var(--color-success-30)]",
  en_cours:    "bg-[var(--color-neutral-95)] text-[var(--color-neutral-30)]",
  en_attente:  "bg-[var(--color-primary-95)] text-[var(--color-primary-30)]",
  // statuts de Lot
  non_demarre: "bg-[var(--color-neutral-99)] text-[var(--color-neutral-30)]",
  termine:     "bg-[var(--color-success-99)] text-[var(--color-success-30)]",
};

const labels: Record<Status, string> = {
  // Projet
  valide:     "Validé",
  en_cours:   "En cours",
  en_attente: "En attente",
  // Lot
  non_demarre: "Non démarré",
  termine:     "Terminé",
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => (
  <span
    className={`inline-block px-3 py-1 rounded text-sm font-medium ${styles[status]}`}
  >
    {labels[status]}
  </span>
);
