// src/lib/projectProposals.ts
import { apiFetch } from "@/lib/apiFetch";

export async function deleteProposal(
  projectName: string,
  proposalTitle: string,
) {
  await apiFetch(
    `${process.env.NEXT_PUBLIC_API_BASE}/api/users/delete_proposal`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name:   projectName,
        proposal_title: proposalTitle,
      }),
    },
  );
}
