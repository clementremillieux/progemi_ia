// src/components/ui/DrawerFooter.tsx
"use client";

import React from "react";
import { Button } from "./Button";

export interface Action {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: "filled" | "outlined" | "text" | "tonal";
  tone?: "primary" | "neutral";
  icon?: React.ReactNode;
}

export interface DrawerFooterProps {
  primary?: Action;
  secondary?: Action;
}

export const DrawerFooter: React.FC<DrawerFooterProps> = ({
  primary,
  secondary,
}) => {
  return (
    <div className="w-full min-h-[80px] p-4 flex flex-col items-stretch gap-2 border-t border-[var(--color-border)] bg-white z-50">
      {secondary && (
        <Button
          label={secondary.label}
          onClick={secondary.onClick}
          disabled={secondary.disabled}
          variant={secondary.variant ?? "outlined"}
          tone={secondary.tone ?? "neutral"}
          icon={secondary.icon}
        />
      )}
      {primary && (
        <Button
          label={primary.label}
          onClick={primary.onClick}
          disabled={primary.disabled}
          loading={primary.loading}
          variant={primary.variant ?? "filled"}
          tone={primary.tone ?? "primary"}
          icon={primary.icon}
        />
      )}
    </div>
  );
};
