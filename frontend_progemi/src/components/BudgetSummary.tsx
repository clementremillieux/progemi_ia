// src/components/BudgetSummary.tsx
"use client";

import React from "react";
import { Euro } from "lucide-react";

interface Props {
  totalBudget: number;
  totalDepenses: number;
}

export const BudgetSummary: React.FC<Props> = ({
  totalBudget,
  totalDepenses,
}) => {
  const fmt = (n: number) =>
    new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(n);

  const items = [
    {
      key: "budget",
      label: "Budget Prévisionnel",
      value: totalBudget,
      bg: "bg-[var(--color-primary-99)]",
      iconColor: "text-[var(--color-primary-30)]",
    },
    {
      key: "depenses",
      label: "Dépenses Engagées",
      value: totalDepenses,
      bg: "bg-[var(--color-warning-99)]",
      iconColor: "text-[var(--color-warning-30)]",
    },
    {
      key: "ecart",
      label: "Écart",
      value: totalBudget - totalDepenses,
      bg: "bg-[var(--color-error-99)]",
      iconColor: "text-[var(--color-error-30)]",
    },
  ];

  return (
    <div className="w-[80%] mx-auto flex flex-col md:flex-row gap-6 py-6">
      {items.map(({ key, label, value, bg, iconColor }) => (
        <div
          key={key}
          className="flex items-center gap-4 bg-white rounded-2xl p-4 flex-1 border border-[var(--color-border)]"
        >
          <div className={`flex-shrink-0 ${bg} ${iconColor} rounded-full p-3`}>
            <Euro className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[12px] text-[var(--color-neutral-60)]">
              {label}
            </p>
            <p className="text-[24px] font-bold text-[var(--color-foreground)]">
              {fmt(value)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

