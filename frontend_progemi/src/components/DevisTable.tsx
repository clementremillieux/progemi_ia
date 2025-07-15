// src/components/DevisTable.tsx
import React from "react";
import type { DevisData, Produit } from "@/types";

interface DevisTableProps {
  data: DevisData;
}

export function DevisTable({ data }: DevisTableProps) {
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[var(--color-border)]">
            <th className="text-left py-3 px-2 font-medium text-[var(--color-neutral-60)]">
              Description
            </th>
            <th className="text-right py-3 px-2 font-medium text-[var(--color-neutral-60)]">
              Qté
            </th>
            <th className="text-right py-3 px-2 font-medium text-[var(--color-neutral-60)]">
              PU HT
            </th>
            <th className="text-right py-3 px-2 font-medium text-[var(--color-neutral-60)]">
              Total HT
            </th>
          </tr>
        </thead>
        <tbody>
          {data.devis_produits.map((p: Produit, i: number) => (
            <tr key={i} className="border-b border-[var(--color-border)]">
              <td className="py-3 px-2 text-[var(--color-foreground)]">
                {p.description}
              </td>
              <td className="text-right py-3 px-2 text-[var(--color-foreground)]">
                {p.quantite}
              </td>
              <td className="text-right py-3 px-2 text-[var(--color-foreground)]">
                {formatAmount(p.price_unitaire_ht)}
              </td>
              <td className="text-right py-3 px-2 font-medium text-[var(--color-foreground)]">
                {formatAmount(p.price_unitaire_ht * p.quantite)}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-[var(--color-border)]">
            <td colSpan={3} className="text-right py-3 px-2 text-[var(--color-neutral-60)]">
              Total HT
            </td>
            <td className="text-right py-3 px-2 font-medium text-[var(--color-foreground)]">
              {formatAmount(data.devis_total_ht)}
            </td>
          </tr>
          <tr>
            <td colSpan={3} className="text-right py-3 px-2 text-[var(--color-neutral-60)]">
              TVA
            </td>
            <td className="text-right py-3 px-2 font-medium text-[var(--color-foreground)]">
              {formatAmount(data.devis_total_tva)}
            </td>
          </tr>
          <tr className="font-semibold text-lg border-t border-[var(--color-border)]">
            <td colSpan={3} className="text-right py-3 px-2 text-[var(--color-foreground)]">
              Total TTC
            </td>
            <td className="text-right py-3 px-2 text-[var(--color-primary-50)]">
              {formatAmount(data.devis_total_ttc)}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}