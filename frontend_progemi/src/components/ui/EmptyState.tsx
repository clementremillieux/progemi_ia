// src/components/ui/EmptyState.tsx
"use client";

import React, { ReactNode } from "react";
import clsx from "clsx";
import type { LucideIcon } from "lucide-react";
import { Button } from "./Button";

export interface EmptyStateProps {
  illustration: ReactNode;
  title: string;
  description?: string;
  actionLabel: string;
  actionIcon?: LucideIcon;
  onAction: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  illustration,
  title,
  description,
  actionLabel,
  actionIcon: Icon,
  onAction,
  className,
}) => (
  <div
    className={clsx(
      "flex flex-col items-center justify-center text-center py-12",
      className
    )}
  >
    <div className="flex-shrink-0 mb-6">{illustration}</div>

    <h2 className="text-xl font-semibold text-[var(--color-foreground)] mb-2">
      {title}
    </h2>

    {description && (
      <p className="text-sm text-[var(--color-neutral-60)] max-w-sm mb-4">
        {description}
      </p>
    )}

    <Button
      icon={Icon ? <Icon /> : undefined}
      label={actionLabel}
      variant="tonal"
      tone="neutral"
      onClick={onAction}
    />
  </div>
);
