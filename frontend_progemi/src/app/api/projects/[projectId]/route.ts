// src/app/api/projects/[projectId]/route.ts
import { NextResponse } from "next/server";
import type { Project, Lot } from "@/types";

export async function GET(
  req: Request,
  { params }: { params: { projectId: string } }
) {
  // Stub : tu pourras plus tard remplacer par un vrai fetch
  const project: Project = {
    id:         params.projectId,
    title:      `Projet #${params.projectId}`,
    description:"",
    status:     "en_cours",
    devisCount: 0,
    totalAmount:0,
  };
  const lots: Lot[] = [];  // aucun lot au départ

  return NextResponse.json({ project, lots });
}
