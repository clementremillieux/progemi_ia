"use client";

import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "filled" | "outlined" | "text" | "tonal";
type Tone = "primary" | "neutral";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  variant?: Variant;
  tone?: Tone;
  icon?: ReactNode;
  loading?: boolean;
}

export const Button = ({
  label,
  variant = "filled",
  tone = "primary",
  icon,
  loading = false,
  disabled,
  className,
  ...props
}: ButtonProps) => {
  const isDisabled = disabled || loading;

  // Hauteur fixe à 36px avec h-9, on garde px-6 pour le padding horizontal
  const baseStyles =
    "inline-flex items-center justify-center h-9 px-6 rounded-lg text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed gap-2";

  const filledStyles = {
    primary: "bg-[var(--color-primary-50)] text-white hover:bg-[var(--color-primary-60)] disabled:bg-[var(--color-neutral-90)] disabled:text-[var(--color-neutral-60)]",
    neutral: "bg-[var(--color-neutral-60)] text-white hover:bg-[var(--color-neutral-70)] disabled:bg-[var(--color-neutral-90)] disabled:text-[var(--color-neutral-60)]",
  };

  const tonalStyles = {
    primary:
      "bg-[var(--color-primary-99)] text-[var(--color-primary-30)] hover:bg-[var(--color-primary-90)] active:bg-[var(--color-primary-95)] focus-visible:ring-[var(--color-primary-90)]",
    neutral:
      "bg-[var(--color-neutral-95)] text-[var(--color-neutral-10)] hover:bg-[var(--color-neutral-90)] active:bg-[var(--color-neutral-95)] focus-visible:ring-[var(--color-neutral-90)]",
  };

  const outlinedStyles = {
    primary:
      "border border-[var(--color-primary-50)] text-[var(--color-primary-50)] hover:bg-[var(--color-primary-99)] active:bg-[var(--color-primary-95)] focus-visible:ring-[var(--color-primary-50)] disabled:border-[var(--color-neutral-90)] disabled:text-[var(--color-neutral-60)]",
    neutral:
      "border border-[var(--color-neutral-70)] text-[var(--color-neutral-950)] hover:bg-[var(--color-neutral-99)] active:bg-[var(--color-neutral-95)] focus-visible:ring-[var(--color-neutral-70)] disabled:border-[var(--color-neutral-90)] disabled:text-[var(--color-neutral-60)]",
  };

  const textStyles = {
    primary:
      "text-[var(--color-primary-50)] hover:bg-[var(--color-primary-99)] active:bg-[var(--color-primary-95)] focus-visible:ring-[var(--color-primary-50)] disabled:text-[var(--color-neutral-60)]",
    neutral:
      "text-[var(--color-neutral-950)] hover:bg-[var(--color-neutral-99)] active:bg-[var(--color-neutral-95)] focus-visible:ring-[var(--color-neutral-70)] disabled:text-[var(--color-neutral-60)]",
  };

  const variants = {
    filled: filledStyles,
    tonal: tonalStyles,
    outlined: outlinedStyles,
    text: textStyles,
  };

  return (
    <button
      className={cn(baseStyles, variants[variant][tone], className)}
      disabled={isDisabled}
      {...props}
    >
      {loading ? <Loader2 className="animate-spin w-4 h-4" /> : icon}
      {label}
    </button>
  );
};
