"use client";

import React from "react";
import type { Lot } from "@/types";
import { Button } from "@/components/ui/Button";
import { MenuDropdown } from "@/components/ui/MenuDropdown";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { MoreVertical, Trash2, Pencil } from "lucide-react";

interface Props {
  lot: Lot;
  onClick?: (id: string) => void; // 👈 ici
  onDuplicate: (id: string) => void;
  onEdit: (lot: Lot) => void;
  onDelete: (id: string) => void;
  onAddDevis: (lotId: string) => void;
  onEditDevis: (lotId: string, devisId: string) => void;
  onDeleteDevis: (lotId: string, devisId: string) => void;
}


export const LotCard: React.FC<Props> = ({
  lot,
  onDuplicate,
  onEdit,
  onDelete,
  onAddDevis,
  onEditDevis,
  onDeleteDevis,
}) => {
  const menuItems = [
    { label: "Modifier", onClick: () => onEdit(lot) },
    { label: "Dupliquer", onClick: () => onDuplicate(lot.id) },
    { label: "Supprimer", onClick: () => onDelete(lot.id) },
  ];

  return (
    <div className="w-[80%] mx-auto">
    <div
      className="bg-white border border-[var(--color-border)] rounded-2xl p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-semibold text-[var(--color-foreground)]">
            {lot.intitule}
          </h3>
          <p className="text-sm text-[var(--color-neutral-60)]">{lot.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            label="Ajouter un devis"
            variant="filled"
            tone="primary"
            onClick={() => onAddDevis(lot.id)}
          />
          <MenuDropdown items={menuItems} />
        </div>
      </div>

      {/* Liste des devis */}
      <div className="overflow-x-auto border border-[var(--color-border)] rounded-lg">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-[var(--color-neutral-99)] text-[var(--color-neutral-60)]">
            <tr>
              <th className="px-4 py-3 font-medium">Devis</th>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Montant</th>
              <th className="px-4 py-3 font-medium">Statut</th>
              <th className="px-4 py-3 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {lot.devis.map((devis) => (
              <tr
                key={devis.id}
                className="border-t border-[var(--color-border)] hover:bg-[var(--color-neutral-98)]"
              >
                <td className="px-4 py-3 flex items-center gap-2">
                  <img src="/file-icon.svg" alt="" className="w-6 h-6" />
                  {devis.fileName}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div>{devis.uploadDate.toLocaleDateString("fr-FR")}</div>
                  <div className="text-xs text-[var(--color-neutral-60)]">
                    {devis.uploadDate.toLocaleTimeString("fr-FR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </td>
                <td className="px-4 py-3">
                  {devis.data
                    ? new Intl.NumberFormat("fr-FR", {
                        style: "currency",
                        currency: "EUR",
                        minimumFractionDigits: 0,
                      }).format(devis.data.devis_total_ttc)
                    : "-"}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={devis.validationStatus as any} />
                </td>
                <td className="px-4 py-3 flex justify-end gap-2">
                  <button
                    onClick={() => onEditDevis(lot.id, devis.id)}
                    className="p-2 rounded hover:bg-[var(--color-neutral-95)] transition"
                  >
                    <Pencil className="w-4 h-4 text-[var(--color-neutral-70)]" />
                  </button>
                  <button
                    onClick={() => onDeleteDevis(lot.id, devis.id)}
                    className="p-2 rounded hover:bg-[var(--color-neutral-95)] transition"
                  >
                    <Trash2 className="w-4 h-4 text-[var(--color-error)]" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
    </div>
  );
};
