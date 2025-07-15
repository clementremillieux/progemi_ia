"use client";

import React from "react";
import { Button } from "@/components/ui/Button";

interface HeaderProps {
  title: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ title, actionLabel, onAction }) => {
  return (
    <div className="w-full h-[69px] flex items-center justify-between border-b border-[var(--color-border)] bg-white">
      {/* Logo + titre */}
      <div className="flex items-center gap-4 pl-6">
        <img
          src="/Logo.jpeg"
          alt="Logo"
          className="w-[40x] h-[40px] rounded-[8px] object-cover"
        />
        <h1 className="text-2xl font-medium text-[var(--color-foreground)]">
          {title}
        </h1>
      </div>

      {/* Action (ex: bouton "Nouveau projet") */}
      {actionLabel && onAction && (
        <div className="pr-6">
          <Button
            label={actionLabel}
            variant="filled"
            tone="primary"
            onClick={onAction}
          />
        </div>
      )}
    </div>
  );
};
