// src/app/api/projects/[projectId]/devis/route.ts
import { NextResponse } from "next/server";
import type { DevisData } from "@/types";

export async function POST(
  req: Request,
  { params }: { params: { projectId: string } }
) {
  const form = await req.formData();
  const file = form.get("file") as Blob;
  if (!file) {
    return NextResponse.json({ error: "Fichier manquant" }, { status: 400 });
  }

  // Appel à l’API IA (stub ou vraie selon .env)
  const USE_STUB = process.env.NEXT_PUBLIC_USE_STUBS === "true";
  if (USE_STUB) {
    const demo: DevisData = {
      devis_id: "DEMO-0001",
      devis_date: "01/01/2025",
      devis_total_ht: 1000,
      devis_total_ttc: 1200,
      devis_total_tva: 200,
      devis_produits: [
        {
          label: "Ligne démo",
          description: "Description démo",
          quantite: 1,
          unitee_quantite: "u",
          price_unitaire_ht: 1000,
          tva: "20%",
          lot: "SANITAIRE",
        },
      ],
    };
    return NextResponse.json(demo);
  }

  // Vraie API
  const IA_BASE = process.env.NEXT_PUBLIC_IA_BASE_URL!;
  const res = await fetch(`${IA_BASE}/parse-devis`, {
    method: "POST",
    headers: {
      "x-api-key": process.env.IA_API_KEY || "",
    },
    body: form,
  });
  if (!res.ok) {
    return NextResponse.json({ error: "Échec IA" }, { status: 502 });
  }
  const data: DevisData = await res.json();
  return NextResponse.json(data);
}
