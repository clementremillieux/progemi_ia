// src/components/ui/SideDrawer.tsx
"use client";

import React, { useEffect } from "react";
import { DrawerHeader } from "./DrawerHeader";
import { DrawerFooter, Action as DrawerAction } from "./DrawerFooter";

interface SideDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  showBackArrow?: boolean;
  onBack?: () => void;
  headerActions?: React.ReactNode;
  secondaryFooterAction?: DrawerAction;
  primaryFooterAction?: DrawerAction;
}

/**
 * SideDrawer component: a sliding panel from the right with header, content and optional footer.
 */
export const SideDrawer: React.FC<SideDrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  showBackArrow = false,
  onBack,
  headerActions,
  secondaryFooterAction,
  primaryFooterAction,
}) => {
  // Block body scroll when open
  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : "unset";
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/40 z-40" onClick={onClose} />

      {/* Drawer panel */}
      <div
        className={`fixed right-0 top-0 h-full w-full max-w-[440px] bg-white z-50 shadow-xl transform transition-transform duration-300 flex flex-col ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <DrawerHeader
          title={title}
          onClose={onClose}
          showBackArrow={showBackArrow}
          actions={headerActions}
        />

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {children}
        </div>

        {/* Footer */}
        {(primaryFooterAction || secondaryFooterAction) && (
          <DrawerFooter
            primary={primaryFooterAction}
            secondary={secondaryFooterAction}
          />
        )}
      </div>
    </>
  );
};
