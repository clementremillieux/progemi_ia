// components/ui/Modal.tsx
import { ReactNode } from "react";

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
};

export const Modal = ({ isOpen, onClose, children }: ModalProps) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onClose}
      style={{
        backgroundColor: "rgba(10, 34, 92, 0.4)", // var(--color-neutral-10) en rgba + opacité 40%
        height: "100vh",
        width: "100vw",
      }}
    >
      <div
        className="bg-white rounded-2xl p-4 w-full max-w-md shadow-xl text-[var(--color-foreground)] border border-[var(--color-border)]"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
};
