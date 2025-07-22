import { apiFetch } from "@/lib/apiFetch";

const API = process.env.NEXT_PUBLIC_API_BASE!;   // ← lève une erreur si absent

/** Tous les packs disponibles pour l’utilisateur */
export async function fetchUserPacks(): Promise<string[]> {
  const data = await apiFetch<{ packs_names: string[] }>(
    `${API}/api/users/get_user_packs_names`,
  );
  return data.packs_names;
}

/** Packs déjà affectés au projet (POST + body JSON) */
export async function fetchProjectPacks(projectName: string): Promise<string[]> {
  return apiFetch<string[]>(
    `${API}/api/users/get_project_packs_names`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_name: projectName }),
    },
  );
}

/** Mise à jour des packs */
export async function updateProjectPacks(projectName: string, packs: string[]) {
  return apiFetch(
    `${API}/api/users/update_project_packs`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_name: projectName, packs_name: packs }),
    },
  );
}
