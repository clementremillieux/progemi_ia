"use client";

import React, { useState, useRef, useEffect } from "react";
import { IconButton } from "./IconButton";
import type { LucideIcon } from "lucide-react";
import { MoreVertical } from "lucide-react";

export interface MenuItem {
  label: string;
  icon?: React.ReactNode;
  onClick: (e: React.MouseEvent) => void;
  className?: string;
}

interface Props {
  items: MenuItem[];
  className?: string;
  triggerVariant?: "filled" | "tonal" | "outlined";
  triggerFlavor?: "primary" | "neutral";
  triggerIcon?: LucideIcon;
}

export const MenuDropdown: React.FC<Props> = ({
  items,
  className = "",
  triggerVariant = "tonal",
  triggerFlavor = "neutral",
  triggerIcon = MoreVertical,
}) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const toggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setOpen((o) => !o);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <div ref={ref} className={`relative inline-block ${className}`}>
      <IconButton
        variant={triggerVariant}
        flavor={triggerFlavor}
        icon={triggerIcon}
        onClick={toggle}
      />

      {open && (
        <div
          className="absolute right-0 mt-2 max-w-[250px] bg-white border border-[var(--color-border)] rounded-lg shadow-md py-1 z-10"
          style={{ width: "max-content" }}
        >
          {items.map((item, idx) => (
            <button
              key={idx}
              onClick={(e) => {
                e.stopPropagation();
                item.onClick(e);
                setOpen(false);
              }}
              className={`flex items-start gap-2 w-full px-4 py-2 text-sm text-left hover:bg-gray-100 ${item.className ?? ""}`}
            >
              {item.icon && <span className="mt-0.5 shrink-0">{item.icon}</span>}
              <span className="break-words leading-snug">{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
