// src/components/ui/DrawerHeader.tsx
"use client";

import React from "react";
import { X, ArrowLeft } from "lucide-react";

interface DrawerHeaderProps {
  title: string;
  onClose: () => void;
  showBackArrow?: boolean;
  actions?: React.ReactNode;
}

export const DrawerHeader: React.FC<DrawerHeaderProps> = ({
  title,
  onClose,
  showBackArrow = false,
  actions,
}) => {
  return (
    <div className="flex items-center justify-between h-14 px-6 border-b border-[var(--color-border)] bg-white">
      {/* Partie gauche : bouton fermer/retour + titre */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onClose}
          className="flex-shrink-0 p-2 -ml-2 rounded-lg hover:bg-[var(--color-neutral-99)] transition-colors"
          aria-label={showBackArrow ? "Retour" : "Fermer"}
        >
          {showBackArrow ? (
            <ArrowLeft className="w-5 h-5 text-[var(--color-foreground)]" />
          ) : (
            <X className="w-5 h-5 text-[var(--color-foreground)]" />
          )}
        </button>
        <h2 className="text-lg font-semibold text-[var(--color-foreground)] truncate">
          {title}
        </h2>
      </div>

      {/* Partie droite : actions */}
      {actions && (
        <div className="flex items-center gap-2 flex-shrink-0 ml-4">
          {actions}
        </div>
      )}
    </div>
  );
};