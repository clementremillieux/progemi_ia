// 🗂 src/app/projects/[projectId]/page.tsx
"use client";    // <- impératif pour useSearchParams et useParams en client

import React from "react";
import { useParams, useSearchParams } from "next/navigation";
import ProjectDetailPage from "@/components/ProjectDetailPage";
import type { ProjectStatus } from "@/types";

export default function ProjectPageWrapper() {
  let { projectId } = useParams();
  if (!projectId) return <p>Projet introuvable.</p>;
  if (Array.isArray(projectId)) projectId = projectId[0];

  const sp = useSearchParams();
  const initialTitle  = sp.get("title")  || "";            // vaudra ce que tu as encodé dans le push
  const initialStatus = (sp.get("status") as ProjectStatus) || "en_cours";

  // Debug : affiche en console pour vérifier
  console.log("Wrapper ▶︎ projectId:", projectId);
  console.log("Wrapper ▶︎ title:", initialTitle);
  console.log("Wrapper ▶︎ status:", initialStatus);

  return (
    <ProjectDetailPage
      projectId={projectId}
      initialTitle={initialTitle}
      initialStatus={initialStatus}
    />
  );
}
