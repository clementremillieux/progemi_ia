import React from "react";
import clsx from "clsx";
import type { LucideIcon } from "lucide-react";

export type Variant = "filled" | "tonal" | "outlined";
export type Flavor = "primary" | "neutral";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  flavor?: Flavor;
  icon: LucideIcon;
}

export const IconButton: React.FC<IconButtonProps> = ({
  variant = "filled",
  flavor = "primary",
  icon: Icon,
  className,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center w-9 h-9 rounded-[6px] focus:outline-none focus:ring-2";

  const styles: Record<Variant, Record<Flavor, string>> = {
    filled: {
      primary:
        "bg-[var(--color-primary-40)] text-white hover:bg-[var(--color-primary-50)] active:bg-[var(--color-primary-60)] focus:ring-[var(--color-primary-50)]",
      neutral:
        "bg-[var(--color-neutral-40)] text-white hover:bg-[var(--color-neutral-50)] active:bg-[var(--color-neutral-60)] focus:ring-[var(--color-neutral-50)]",
    },
    tonal: {
      primary:
        "bg-[var(--color-primary-99)] text-[var(--color-primary-30)] hover:bg-[var(--color-primary-90)] active:bg-[var(--color-primary-95)] focus:ring-[var(--color-primary-90)]",
      neutral:
        "bg-[var(--color-neutral-99)] text-[var(--color-neutral-10)] hover:bg-[var(--color-neutral-90)] active:bg-[var(--color-neutral-95)] focus:ring-[var(--color-neutral-90)]",
    },
    outlined: {
      primary:
        "border border-[var(--color-primary-40)] text-[var(--color-primary-40)] hover:border-[var(--color-primary-50)] hover:text-[var(--color-primary-50)] active:border-[var(--color-primary-60)] active:text-[var(--color-primary-60)] focus:ring-[var(--color-primary-50)]",
      neutral:
        "border border-[var(--color-neutral-40)] text-[var(--color-neutral-40)] hover:border-[var(--color-neutral-50)] hover:text-[var(--color-neutral-50)] active:border-[var(--color-neutral-60)] active:text-[var(--color-neutral-60)] focus:ring-[var(--color-neutral-50)]",
    },
  };

  const variantStyles = styles[variant][flavor];
  const combined = clsx(baseStyles, variantStyles, className);

  return (
    <button className={combined} {...props}>
      <Icon className="w-5 h-5" />
    </button>
  );
};
