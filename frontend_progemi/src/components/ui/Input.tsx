// src/components/ui/Input.tsx
import React from "react";
import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "w-full rounded-md border border-[var(--color-border)] bg-white px-3 py-2 text-sm text-[var(--color-foreground)] placeholder-[var(--color-neutral-60)] shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-30)] focus:border-transparent transition",
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";
