// components/DevisEditor.tsx
import React from "react";
import { Input } from "@/components/ui/Input";
import { Edit3, Hash, ShoppingCart, Tag } from "lucide-react";
import type { DevisData } from "@/types";

interface Props {
  devis: DevisData;
  onUpdate: (updated: DevisData) => void;
}

export const DevisEditor: React.FC<Props> = ({ devis, onUpdate }) => {
  const handleItemChange = (
    index: number,
    key: keyof DevisData["devis_items"][0],
    value: string | number
  ) => {
    const newItems = [...devis.devis_items];
    newItems[index] = { ...newItems[index], [key]: value };
    onUpdate({ ...devis, devis_items: newItems });
  };

  return (
    <div className="space-y-8 p-4">
      <h3 className="text-xl font-semibold text-[var(--color-foreground)]">
        Éditer les lignes du devis
      </h3>

      {devis.devis_items.map((item, index) => (
        <div key={index} className="space-y-4 border-b pb-6">
          <div className="flex items-center gap-2 text-sm font-medium text-[var(--color-neutral-70)]">
            <Tag className="w-4 h-4" />
            Ligne {index + 1}
          </div>

          <div className="space-y-3">
            {/* Label */}
            <div className="flex justify-between items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-[var(--color-neutral-70)]">
                <Edit3 className="w-4 h-4" />
                <span>Label</span>
              </div>
              <Input
                value={item.label}
                onChange={(e) =>
                  handleItemChange(index, "label", e.target.value)
                }
                className="w-2/3"
              />
            </div>

            {/* Quantité */}
            <div className="flex justify-between items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-[var(--color-neutral-70)]">
                <Hash className="w-4 h-4" />
                <span>Quantité</span>
              </div>
              <Input
                type="number"
                value={item.quantite}
                onChange={(e) =>
                  handleItemChange(index, "quantite", parseFloat(e.target.value))
                }
                className="w-2/3"
              />
            </div>

            {/* Prix unitaire */}
            <div className="flex justify-between items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-[var(--color-neutral-70)]">
                <ShoppingCart className="w-4 h-4" />
                <span>Prix unitaire</span>
              </div>
              <Input
                type="number"
                value={item.prixUnitaire}
                onChange={(e) =>
                  handleItemChange(index, "prixUnitaire", parseFloat(e.target.value))
                }
                className="w-2/3"
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
