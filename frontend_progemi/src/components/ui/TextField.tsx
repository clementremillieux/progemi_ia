"use client";

import { cn } from "@/lib/utils";
import { ReactNode } from "react";

export type TextFieldStatus = "default" | "error" | "warning" | "success";

interface TextFieldProps {
  label: string;
  id: string;
  placeholder?: string;
  icon?: ReactNode;
  helperText?: string;
  status?: TextFieldStatus;
  value: string;
  onChange: (value: string) => void;
}

export const TextField = ({
  id,
  label,
  placeholder,
  icon,
  helperText,
  status = "default",
  value,
  onChange,
}: TextFieldProps) => {
  const borderStyles: Record<TextFieldStatus, string> = {
    default: "border-[var(--color-neutral-90)]",
    error: "border-[var(--color-error-60)]",
    warning: "border-[var(--color-warning-60)]",
    success: "border-[var(--color-success-60)]",
  };

  const bgStyles: Record<TextFieldStatus, string> = {
    default: "bg-white",
    error: "bg-[var(--color-error-99)]",
    warning: "bg-[var(--color-warning-99)]",
    success: "bg-[var(--color-success-99)]",
  };

  const textStyles: Record<TextFieldStatus, string> = {
    default: "text-[var(--color-foreground)]",
    error: "text-[var(--color-error-60)]",
    warning: "text-[var(--color-warning-60)]",
    success: "text-[var(--color-success-60)]",
  };

  const helperTextStyles: Record<TextFieldStatus, string> = {
    default: "text-[var(--color-neutral-70)]",
    error: "text-[var(--color-error-60)]",
    warning: "text-[var(--color-warning-60)]",
    success: "text-[var(--color-success-60)]",
  };

  return (
    <div className="space-y-1">
      <label htmlFor={id} className="text-sm font-medium text-[var(--color-foreground)] block">
        {label}
      </label>
      <div
        className={cn(
          "flex items-center border rounded-lg px-3 py-2 text-sm",
          borderStyles[status],
          bgStyles[status],
          textStyles[status]
        )}
      >
        {icon && <span className="mr-2 text-inherit">{icon}</span>}
        <input
          id={id}
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={cn(
            "w-full bg-transparent focus:outline-none text-inherit placeholder:text-[var(--color-neutral-70)]"
          )}
        />
      </div>
      {helperText && (
        <p className={cn("text-xs", helperTextStyles[status])}>{helperText}</p>
      )}
    </div>
  );
};