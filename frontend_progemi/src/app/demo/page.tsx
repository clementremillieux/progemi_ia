"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { IconButton } from "@/components/ui/IconButton";
import { SideDrawer } from "@/components/ui/SideDrawer";
import { DrawerFooter } from "@/components/ui/DrawerFooter";
import { DrawerHeader } from "@/components/ui/DrawerHeader";
import { LotCard } from "@/components/LotCard";
import { DevisTable } from "@/components/DevisTable";
import { Input } from "@/components/ui/Input";
import { DevisEditor } from "@/components/DevisEditor";

import type { Lot, Devis, DevisData, DevisItem } from "@/types";
import { Home, FileText, Archive } from "lucide-react";


export default function DemoPage() {
  const [open, setOpen] = useState(true);

  const demoLots: Lot[] = [
    {
      id: "lot1",
      numero: 1,
      intitule: "Lot A",
      description: "Description A",
      responsable: "Alice",
      status: "non_demarre",
      budgetPrevisionnel: 5000,
      depensesEngagees: 1200,
      devis: [],
    },
    {
      id: "lot2",
      numero: 2,
      intitule: "Lot B",
      description: "Description B",
      responsable: "Bob",
      status: "en_cours",
      budgetPrevisionnel: 8000,
      depensesEngagees: 3000,
      devis: [],
    },
    {
      id: "lot3",
      numero: 3,
      intitule: "Lot C",
      description: "Description C",
      responsable: "Charlie",
      status: "termine",
      budgetPrevisionnel: 10000,
      depensesEngagees: 10000,
      devis: [],
    },
  ];

const demoDevis: Devis = {
  id: "devis-001",
  fileName: "devis_maçonnerie.pdf",
  status: "completed",
  validationStatus: "en_attente",
  uploadDate: new Date("2024-06-01"),
  fournisseur: "Entreprise MaçonPro",
  data: {
    devis_id: "D-2024-001",
    devis_date: "2024-05-30",
    devis_total_ht: 5000,
    devis_total_tva: 1000,
    devis_total_ttc: 6000,
    devis_produits: [
      {
        label: "Fondations",
        description: "Coulage de fondations en béton armé",
        quantite: 20,
        unitee_quantite: "m³",
        price_unitaire_ht: 100,
        tva: "20%",
        lot: "lot1",
        sous_produits: [
          {
            label: "Ciment",
            description: "Sac de ciment 35kg",
            quantite: 40,
            unitee_quantite: "sac",
            price_unitaire_ht: 8,
            tva: "20%",
            lot: "lot1",
          },
        ],
      },
      {
        label: "Murs porteurs",
        description: "Élévation des murs en parpaing",
        quantite: 100,
        unitee_quantite: "m²",
        price_unitaire_ht: 30,
        tva: "20%",
        lot: "lot1",
        sous_produits: null,
      },
    ],
    devis_items: [
      {
        label: "Fondations",
        prixUnitaire: 100,
        quantite: 20,
      },
      {
        label: "Murs porteurs",
        prixUnitaire: 30,
        quantite: 100,
      },
    ],
  },
};




  return (
    <main className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">Démonstration des composants UI</h1>

      {/* Buttons */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Buttons</h2>
        <div className="flex items-center gap-4">
          <Button label="Filled Primary" variant="filled" tone="primary" />
          <Button label="Outlined Neutral" variant="outlined" tone="neutral" />
          <Button label="Tonal Primary" variant="tonal" tone="primary" />
          <Button label="Text Neutral" variant="text" tone="neutral" />
        </div>
      </section>

      {/* IconButtons */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">IconButtons</h2>
        <div className="flex items-center gap-4">
          <IconButton icon={Home} variant="filled" flavor="primary" />
          <IconButton icon={FileText} variant="tonal" flavor="primary" />
          <IconButton icon={Archive} variant="outlined" flavor="primary" />
        </div>
      </section>

      {/* LotCard */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">LotCard</h2>
        <div className="grid grid-cols-3 gap-6">
          {demoLots.map((lot) => (
            <LotCard
              key={lot.id}
              lot={lot}
              onClick={() => {}}
              onDuplicate={() => {}}
              onEdit={() => {}}
              onDelete={() => {}}
              onAddDevis={() => {}}
              onEditDevis={() => {}}
              onDeleteDevis={() => {}}
            />
          ))}
        </div>
      </section>

      {/* DevisTable */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">DevisTable</h2>
        <div className="overflow-auto">
          <DevisTable data={demoDevis.data as DevisData} />
        </div>
      </section>

      {/* SideDrawer */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">SideDrawer</h2>
        <Button
          label="Ouvrir Drawer"
          variant="filled"
          tone="primary"
          onClick={() => setOpen(true)}
        />
        <SideDrawer
          isOpen={open}
          onClose={() => setOpen(false)}
          title="Exemple Drawer"
          showBackArrow
          headerActions={<Button label="Action" variant="text" tone="neutral" />}
          secondaryFooterAction={{ label: "Annuler", onClick: () => setOpen(false) }}
          primaryFooterAction={{ label: "Valider", onClick: () => alert("Validé") }}
        >
          <div className="p-6">
            <h3 className="text-lg font-semibold">Contenu du Drawer</h3>
            <p>Voici un aperçu de votre SideDrawer personnalisé.</p>
          </div>
        </SideDrawer>
      </section>

      {/* DrawerFooter seul */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">DrawerFooter seul</h2>
        <div className="relative border p-4">
          <DrawerHeader title="Footer seul" onClose={() => {}} showBackArrow={false} actions={null} />
          <div style={{ minHeight: 100 }} />
          <DrawerFooter
            secondary={{ label: "Retour", onClick: () => alert("Retour") }}
            primary={{ label: "Suivant", onClick: () => alert("Suivant") }}
          />
        </div>
        {/* DevisItemEditor */}
<section className="space-y-4">
  <h2 className="text-xl font-semibold">DevisItemEditor</h2>
  <SideDrawer
    isOpen={open}
    onClose={() => setOpen(false)}
    title="Édition des lignes de devis"
    showBackArrow
    secondaryFooterAction={{ label: "Fermer", onClick: () => setOpen(false) }}
    primaryFooterAction={{
      label: "Sauvegarder",
      onClick: () => alert("Sauvegardé !"),
    }}
  >
    <div className="p-6 space-y-4">
      {demoDevis.data?.devis_items.map((item, idx) => (
        <DevisEditor
  devis={demoDevis.data!}
  onUpdate={(updated: DevisData) => {
    demoDevis.data = updated;
  }}
/>

      ))}
    </div>
  </SideDrawer>
</section>

      </section>
    </main>
  );
}
