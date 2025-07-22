"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { ProjectHeader } from "./ProjectHeader";
import JsonEditor  from "./JsonEditor";
import dynamic from "next/dynamic";
const PdfViewer = dynamic(() => import("./PdfViewer"), { ssr: false });
import { SideDrawer } from "./ui/SideDrawer";
import { DevisUploader } from "./DevisUploader";
import { EmptyState } from "./ui/EmptyState";
import { Modal } from "./ui/Modal";
import { Button } from "./ui/Button";
import { TextField } from "./ui/TextField";
import {
  FileText,
  Scan,
  CheckCircle,
  CircleDot,
  Plus,
  Upload,
} from "lucide-react";
import type { DevisData, ProjectStatus, ValidationError } from "@/types";
import { apiFetch } from "@/lib/apiFetch";
import { X, Trash2 } from "lucide-react";
import { deleteProposal } from "@/lib/projectProposals";


/* ------------------------------------------------------------------ */
/* Types locaux                                                       */
/* ------------------------------------------------------------------ */

interface ProposalInfos {
  title : string;
  status: "pending" | "processed" | "accepted";
  pdf_id?: string | null;
  packs  : string[]; 
}

interface Proposal extends ProposalInfos {
  id: string;                 // uuid local
  pdfUrl: string;             // blob URL
  extractedObject?: DevisData | null;
  validationReport?: ValidationReport | null;
  packs: string[];                 
}

interface ValidationReport {
  computed_total_ht: number;
  computed_total_tva: number;
  computed_total_ttc: number;
  computed_total_cout_additionnel: number;
  logs: string[];
  errors: ValidationError[];
}

async function fetchAllProposalsInfos(
  projectName: string,
): Promise<ProposalInfos[]> {
  return apiFetch<ProposalInfos[]>(
    `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_all_proposals_infos`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name: projectName,
      }),
    },
  );
}

/* ------------------------------------------------------------------ */
/* Composant page                                                     */
/* ------------------------------------------------------------------ */

interface Props {
  projectId: string;
  userEmail: string;
  initialTitle: string;
  initialStatus: ProjectStatus;
}





export default function ProjectDetailPage({
  projectId,
  userEmail,
  initialTitle,
  initialStatus,
}: Props) {
  const router = useRouter();

  /* ----------------- état projet & UI ----------------- */
  const [project, setProject] = useState({
    id: projectId,
    title: initialTitle,
    status: initialStatus,
  });
  const [showUploader, setShowUploader] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editedTitle, setEditedTitle] = useState(initialTitle);

  /* ----------------- devis ----------------- */
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selectedProposal = proposals.find((p) => p.id === selectedId) || null;

  const [isExtracting, setIsExtracting] = useState(false);
  const [editedObject, setEditedObject] = useState<DevisData | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const [projectPacks, setProjectPacks] = useState<string[]>([]);


  useEffect(() => {
    (async () => {
      try {
        const packs = await apiFetch<string[]>(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_project_packs_names`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_name: initialTitle }),
          },
        );
        console.log("[PACKS] reçus depuis l’API ⇒", packs); 
        setProjectPacks(packs.length ? packs : ["Autre"]);
      } catch {
        setProjectPacks(["Autre"]);
      }
    })();
  }, [initialTitle]);

  /** supprime accents, double‐espaces, casse, etc. */
  const clean = (s: string) =>
    s
      .normalize("NFD")                  // décompose les accents
      .replace(/[\u0300-\u036f]/g, "")   // enlève les accents
      .replace(/\s*\/\s*/g, "/")         // espace(s) autour du « / »
      .replace(/\s+/g, " ")              // réduit les espaces multiples
      .trim()                            // enlève début/fin
      .toLowerCase();                    // casse insensible



  const mainLot = (p: Proposal) => {
    const packs = p.packs ?? [];             // ← évite undefined
    if (packs.length) {
      for (const raw of packs) {
        const lotClean = clean(raw);
        if (projectPacks.some(lp => clean(lp) === lotClean)) {
          return lotClean;
        }
      }
      return clean(packs[0]);                // premier pack nettoyé
    }
    return "autre";                          // aucun pack
  };



  // Map clé = libellé nettoyé    valeur = { label: original, items: Proposal[] }
  /* ---------- regroupement ---------- */
  const grouped = useMemo(() => {
    const map = new Map<string, { label: string; items: Proposal[] }>();

    projectPacks.forEach(lbl => map.set(clean(lbl), { label: lbl, items: [] }));
    if (!map.has("autre")) map.set("autre", { label: "Autre", items: [] });

    proposals.forEach(p => {
      const key = mainLot(p);
      if (!map.has(key)) map.set(key, { label: p.extractedObject?.lots?.[0] ?? "Autre", items: [] });
      map.get(key)!.items.push(p);
    });

    return [...map.values()];        //  ← UN TABLEAU, plus de .entries()
  }, [proposals, projectPacks]);



  /* rectangle rouge */
type Highlight = { polygon: number[]; page: number };
const [highlight, setHighlight] = useState<Highlight | null>(null);

  /* ----------------- charge la liste initiale ----------------- */
  useEffect(() => {
    (async () => {
      try {
        const infos = await fetchAllProposalsInfos(project.title);
        console.log("[DEVIS] infos brutes:", infos);  
        setProposals(
          infos.map((inf) => ({
            ...inf,
            id: crypto.randomUUID(),
            packs: inf.packs ?? [],
            pdfUrl: "",
          })),
        );
      } catch (err) {
        console.error("Erreur chargement des devis :", err);
      }
    })();
  }, ["test_email@test.fr", project.title]);

  /* ----------------- sélection d'un devis ----------------- */
  const handleSelect = async (id: string) => {
    setSelectedId(id);
    setEditedObject(null);

    const prop = proposals.find((p) => p.id === id);
    if (!prop) return;

    const payloadBase = {
      user_email: "test_email@test.fr",
      project_name: project.title,
      title: prop.title,
    };

    /* PDF */
    let pdfUrl = prop.pdfUrl;
    if (!pdfUrl && prop.pdf_id) {
      try {
        const blob = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_proposal`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ...payloadBase, proposal_id: prop.pdf_id }),
            credentials: "include",
          },
        ).then((r) => r.blob());
        pdfUrl = URL.createObjectURL(blob);
      } catch (e) {
        console.error("Erreur PDF :", e);
      }
    }

    /* objet structuré */
    let extracted: DevisData | null = null;
    try {
      extracted = await apiFetch<DevisData>(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_proposal_extracted_object`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_email: "test_email@test.fr",
            project_name: project.title,
            proposal_title: prop.title,
          }),
        },
      );
    } catch {
      /* pas encore extrait */
    }

    /* maj locale */
    setProposals((prev) =>
      prev.map((p) =>
        p.id === id
          ? { ...p, pdfUrl: pdfUrl || p.pdfUrl, extractedObject: extracted || p.extractedObject }
          : p,
      ),
    );
    if (extracted) setEditedObject(extracted);
  };

  /* ----------------- upload ----------------- */
  const handleUploadComplete = (file: File) => {
    const url = URL.createObjectURL(file);
    const prop: Proposal = {
      id: crypto.randomUUID(),
      title: file.name,
      status: "pending",
      pdfUrl: url,
      packs: [],    
    };
    setProposals((prev) => [...prev, prop]);
    setSelectedId(prop.id);
    setShowUploader(false);
  };

  /* ----------------- extraction ----------------- */
  const handleExtract = async () => {
    if (!selectedProposal) return;
    setIsExtracting(true);

    const payload = {
      user_email: "test_email@test.fr",
      project_name: project.title,
      proposal_title: selectedProposal.title,
    };

    try {
      await apiFetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_proposal_object`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
      );

      const obj = await apiFetch<DevisData>(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_proposal_extracted_object`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
      );

      setProposals((prev) =>
        prev.map((p) => (p.id === selectedProposal.id ? { ...p, extractedObject: obj } : p)),
      );
      setEditedObject(obj);
    } finally {
      setIsExtracting(false);
    }
  };

  /* ----------------- sauvegarde ----------------- */
  /* ------------------------------------------------------------------ */
/* M-à-j du devis structuré (bouton « Mettre à jour »)                */
/* ------------------------------------------------------------------ */
const handleSave = async () => {
  /* pas de devis sélectionné ou rien à enregistrer → on sort */
  if (!selectedProposal || !editedObject) return;

  setIsSaving(true);

  try {
    /* ------------ appel API : on récupère l’objet sauvegardé -------- */
    const saved = await apiFetch<DevisData>(
      `${process.env.NEXT_PUBLIC_API_BASE}/api/users/set_proposal_extracted_object`,
      {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({
          user_email      : "test_email@test.fr",          // <— utilisez la prop
          project_name    : project.title,
          title           : selectedProposal.title,
          extracted_object: editedObject,
        }),
      },
    );

    /* ------------ ① on met à jour l’éditeur ------------------------ */
    setEditedObject(saved);

    /* ------------ ② on remplace la copie côté liste ---------------- */
    setProposals(prev =>
      prev.map(p =>
        p.id === selectedProposal.id
          ? { ...p, extractedObject: saved }
          : p,
      ),
    );

    /* (facultatif) : toast ou notif de succès */
    // toast.success("Devis enregistré !");
  }
  catch (err) {
    console.error("Erreur d’enregistrement :", err);
    // toast.error("Échec de l’enregistrement");
  }
  finally {
    setIsSaving(false);
  }
};


  /* ----------------- rendu ----------------- */
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[var(--color-neutral-99)]">
      {/* Header */}
      <div className="sticky top-0 z-10 w-full">
        <ProjectHeader
          projectName={project.title}
          status={project.status}
          onBack={() => router.back()}
          onImport={() => setShowUploader(true)}
          onValidate={() => {}}
          onEdit={() => setShowEditModal(true)}
          onDelete={() => router.back()}
        />
      </div>

      {/* Corps */}
      <div className="flex flex-1 overflow-hidden">
        {/* ---------- Aside gauche ---------- */}
        <aside className="w-[216px] shrink-0 border-r bg-white p-4 flex flex-col gap-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">Devis</h2>
            <Button
              size="icon"
              variant="text"
              tone="primary"
              label="Ajouter un devis"
              onClick={() => setShowUploader(true)}
            >
              <Plus className="w-5 h-5" />
            </Button>
          </div>

          {proposals.length === 0 ? (
            <EmptyState
              illustration={<FileText className="w-16 h-16 text-neutral-400" />}
              title="Aucun devis"
              description="Importez ou créez un devis pour commencer."
              actionLabel="Importer un devis"
              actionIcon={Upload}
              onAction={() => setShowUploader(true)}
            />
          ) : (
            <ul className="space-y-4">
              {grouped.map(({ label, items }) => (      
                <li key={label}>
                  <h3 className="text-sm font-medium text-neutral-500 flex items-center gap-1 mb-1">
                    <span className="truncate">{label}</span>
                    <span className="text-xs text-neutral-400">({items.length})</span>
                  </h3>

                {/* ── liste des devis du lot ─────────────────────────────── */}
                <ul className="space-y-2">
                  {items.map(p => (                                   // ← items, pas list
                    <li key={p.id}>
                      <div
                        className={`rounded-lg p-2 ${
                          p.id === selectedId
                            ? "bg-primary-50 text-primary-700"
                            : "hover:bg-neutral-100"
                        }`}
                      >
                        {/* bouton sélection */}
                        <button
                          onClick={() => handleSelect(p.id)}
                          className="w-full flex items-center justify-between"
                        >
                          <span className="truncate pr-2 max-w-[150px]">{p.title}</span>
                          {p.status === "pending"   && <CircleDot   className="w-4 h-4 text-neutral-400" />}
                          {p.status === "processed" && <Scan        className="w-4 h-4 text-amber-500" />}
                          {p.status === "accepted"  && <CheckCircle className="w-4 h-4 text-green-600" />}
                        </button>

                        {/* poubelle */}
                        <button
                          aria-label="Supprimer"
                          className="mt-1 ml-auto flex items-center text-neutral-400 hover:text-red-600"
                          onClick={async () => {
                            if (!confirm(`Supprimer le devis « ${p.title} » ?`)) return;
                            try {
                              await deleteProposal(project.title, p.title);
                              setProposals(prev => prev.filter(pr => pr.id !== p.id));
                              if (p.id === selectedId) {
                                setSelectedId(null);
                                setEditedObject(null);
                              }
                            } catch (err) {
                              console.error("Erreur suppression :", err);
                              alert("La suppression a échoué.");
                            }
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>

          )}
        </aside>

        {/* ---------- Viewer PDF + surbrillance ---------- */}
        <div className="shrink-0 flex flex-col bg-neutral-50 overflow-auto">
          {selectedProposal && (
            <div className="p-2 border-b bg-white flex justify-end">
              <Button
                variant="filled"
                tone="primary"
                size="sm"
                disabled={isExtracting}
                label={isExtracting ? "Extraction..." : "Extraire"}
                onClick={handleExtract}
              />
            </div>
          )}

          <div className="flex-1 overflow-auto">
            {selectedProposal && selectedProposal.pdfUrl ? (
              <div className="relative w-full h-full">
                <PdfViewer
                    file={selectedProposal.pdfUrl}
                    highlight={highlight}
                  />
              </div>
            ) : (
              <div className="h-full flex items-center justify-center">
                <EmptyState
                  illustration={<FileText className="w-20 h-20 text-neutral-400" />}
                  title="Sélectionnez un devis"
                  description="Cliquez sur un devis dans le panneau de gauche."
                />
              </div>
            )}
          </div>
        </div>

        {/* ---------- Aside droite (éditeur JSON) ---------- */}
        <aside className="flex-1 border-l bg-white flex flex-col">
          <div className="p-2 border-b flex justify-between items-center">
            <span className="font-semibold">Données extraites</span>
            {selectedProposal && (
              <Button
                size="sm"
                variant="filled"
                tone="primary"
                disabled={!editedObject || isSaving}
                label={isSaving ? "Enregistrement..." : "Mettre à jour"}
                onClick={handleSave}
              />
            )}
          </div>

          <div className="flex-1 overflow-auto p-4">
            {editedObject ? (
              <JsonEditor
                value={editedObject}
                onChange={setEditedObject}
                onHover={setHighlight}
              />
            ) : selectedProposal ? (
              <p className="text-sm text-neutral-600">
                Cliquez sur <span className="font-medium">Extraire</span> pour afficher le devis structuré.
              </p>
            ) : (
              <p className="text-sm text-neutral-600">Sélectionnez un devis à gauche.</p>
            )}
          </div>
        </aside>
      </div>

      {/* ---------- Drawer upload ---------- */}
      <SideDrawer
        isOpen={showUploader}
        onClose={() => setShowUploader(false)}
        title="Importer un devis (PDF)"
        primaryFooterAction={{ label: "Fermer", onClick: () => setShowUploader(false) }}
      >
        <DevisUploader
          userEmail="test_email@test.fr"
          projectName={project.title}
          onDone={handleUploadComplete}
        />
      </SideDrawer>

      {/* ---------- Modal édition titre ---------- */}
      <Modal isOpen={showEditModal} onClose={() => setShowEditModal(false)}>
        <div className="flex flex-col gap-4">
          <h2 className="text-lg font-semibold">Modifier le projet</h2>
          <TextField
            id="edit-title"
            label="Titre du projet"
            value={editedTitle}
            onChange={setEditedTitle}
          />
          <div className="flex justify-end gap-2">
            <Button
              label="Annuler"
              variant="text"
              tone="neutral"
              onClick={() => setShowEditModal(false)}
            />
            <Button
              label="Enregistrer"
              variant="filled"
              tone="primary"
              onClick={() => {
                setProject((p) => ({ ...p, title: editedTitle }));
                setShowEditModal(false);
              }}
            />
          </div>
        </div>
      </Modal>
    </div>
  );
}

