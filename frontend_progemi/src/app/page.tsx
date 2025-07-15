"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/ui/Header";
import { Modal } from "@/components/ui/Modal";
import { TextField } from "@/components/ui/TextField";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ProjectCard } from "@/components/ProjectCard";
import type { Project } from "@/types";
import { Plus } from "lucide-react";

/** ----------------------------------------------------------------
 *  Constantes & helpers
 *  ---------------------------------------------------------------- */
const STORAGE_KEY = "mes_projets";

async function fetchProjectNames(userEmail: string): Promise<string[]> {
  const res = await fetch(
    process.env.NEXT_PUBLIC_API_BASE + "/api/users/get_all_projects",
    {
      method: "POST",                       // ⬅️  POST, plus GET
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_email: "test_email@test.fr" }),
    },
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function toProject(name: string): Project {
  return {
    id: name,                 // l’API ne renvoie qu’un nom ; on l’utilise comme id
    title: name,
    description: "",
    status: "en_attente",
    devisCount: 0,
  };
}

/** ----------------------------------------------------------------
 *  Composant
 *  ---------------------------------------------------------------- */
interface Props {
  /** Email de l’utilisateur (nécessaire pour appeler l’API) */
  userEmail: string;
}

export default function HomePage({ userEmail }: Props) {
  const router = useRouter();

  const [projects, setProjects] = useState<Project[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [packs, setPacks] = useState<string[]>([""]); // au moins 1 champ

  const addPack    = () => setPacks((p) => [...p, ""]);
  const deletePack = (idx: number) =>
    setPacks((p) => p.filter((_, i) => i !== idx));
  const changePack = (idx: number, val: string) =>
    setPacks((p) => p.map((v, i) => (i === idx ? val : v)));

  /** ------------------------- chargement initial ------------------------ */
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const names = await fetchProjectNames(userEmail);
        if (cancelled) return;
        const list = names.map(toProject);
        setProjects(list);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
      } catch {
        // fallback sur le cache local si l’API tombe
        const cache = localStorage.getItem(STORAGE_KEY);
        if (cache && !cancelled) {
          try {
            setProjects(JSON.parse(cache));
          } catch {
            localStorage.removeItem(STORAGE_KEY);
          }
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [userEmail]);

  /** --------------------------- helpers (cache) ------------------------- */
  const saveProjects = (list: Project[]) =>
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));

  /** ----------------------------- handlers ------------------------------ */
  const handleAdd = async () => {
    if (!newTitle.trim() || packs.some((l) => !l.trim())) return;

    /* 1. appel backend */
    await fetch(process.env.NEXT_PUBLIC_API_BASE + "/api/users/new_project", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_email: "test_email@test.fr",
        project_name: newTitle.trim(),
        packs: packs.map((l) => l.trim()),
      }),
    });

    /* 2. mise à jour locale + navigation */
    const id = crypto.randomUUID();
    const proj: Project = {
      id,
      title: newTitle.trim(),
      description: newDesc.trim(),
      status: "en_attente",
      devisCount: 0,
    };
    const updated = [...projects, proj];
    setProjects(updated);
    saveProjects(updated);
    setShowForm(false);
    setNewTitle("");
    setNewDesc("");
    setPacks([""]);
    router.push(`/projects/${id}?title=${encodeURIComponent(proj.title)}&status=${proj.status}`);
  };

  const handleDuplicateProject = (id: string) => {
    const orig = projects.find((p) => p.id === id);
    if (!orig) return;
    const newProj = { ...orig, id: crypto.randomUUID(), title: `${orig.title} (copie)` };
    const updated = [...projects, newProj];
    setProjects(updated);
    saveProjects(updated);
  };

  const handleDeleteProject = async (id: string) => {
    
    const proj = projects.find((p) => p.id === id);
    if (!proj) return;
   
    try {
      await fetch(
        process.env.NEXT_PUBLIC_API_BASE + "/api/users/delete_project",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_email: "test_email@test.fr",       
            project_name: proj.title,    
          }),
      },
     );
    } catch (err) {
      console.error("Erreur suppression backend :", err);

    }


    const updated = projects.filter((p) => p.id !== id);
    setProjects(updated);
    saveProjects(updated);
  };
  /** ------------------------------ render ------------------------------- */
  return (
    <div className="min-h-screen bg-[var(--color-neutral-99)]">
      {/* barre supérieure */}
      <Header
        title="Mes projets"
        actionLabel="Nouveau projet"
        onAction={() => setShowForm(true)}
      />

      {/* contenu principal */}
      <main className="p-6 space-y-6">
        {/* ---------- modal création ---------- */}
        <Modal isOpen={showForm} onClose={() => setShowForm(false)}>
          <div className="p-4 space-y-6">
            <h2 className="text-xl font-semibold text-[var(--color-foreground)]">
              Nouveau projet
            </h2>

            {/* ---- Nom + description ---- */}
            <div className="space-y-4">
              <TextField
                id="new-project-title"
                label="Titre du projet"
                value={newTitle}
                onChange={setNewTitle}
              />
              <TextField
                id="new-project-description"
                label="Description"
                value={newDesc}
                onChange={setNewDesc}
              />
            </div>

            {/* ---- Liste de lots ---- */}
            <div className="space-y-2">
              <h3 className="font-medium">Lots du projet</h3>

              {packs.map((lot, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <TextField
                    id={`lot-${idx}`}
                    value={lot}
                    placeholder={`Lot #${idx + 1}`}
                    onChange={(v) => changePack(idx, v)}
                    className="flex-1"
                  />
                  {packs.length > 1 && (
                    <Button
                      size="icon"
                      variant="text"
                      tone="neutral"
                      onClick={() => deletePack(idx)}
                      label="Supprimer"
                    >
                      ✕
                    </Button>
                  )}
                </div>
              ))}

              <Button
                variant="text"
                tone="primary"
                onClick={addPack}
                label="Ajouter un lot"
              >
                + Ajouter un lot
              </Button>
            </div>

            {/* ---- Actions ---- */}
            <div className="flex justify-end gap-2 pt-4">
              <Button
                label="Annuler"
                variant="outlined"
                tone="neutral"
                onClick={() => setShowForm(false)}
              />
              <Button label="Créer" variant="filled" tone="primary" onClick={handleAdd} />
            </div>
          </div>
        </Modal>


        {/* ---------- liste de projets / empty state ---------- */}
        {projects.length === 0 ? (
          <EmptyState
            illustration={<img src="/Files.svg" alt="Aucun projet" className="w-40 h-40" />}
            title="Aucun projet créé"
            description="Créez un nouveau projet pour démarrer votre planification."
            actionLabel="Nouveau projet"
            actionIcon={Plus}
            onAction={() => setShowForm(true)}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p) => (
              <ProjectCard
                key={p.id}
                projectId={p.id}
                title={p.title}
                status={p.status}
                devisCount={p.devisCount}

                onDuplicate={handleDuplicateProject}
                onDelete={handleDeleteProject}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
