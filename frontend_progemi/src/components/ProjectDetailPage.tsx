"use client";

import React, { useEffect, useState } from "react";
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

/* ------------------------------------------------------------------ */
/* Types locaux                                                       */
/* ------------------------------------------------------------------ */

interface ProposalInfos {
  title: string;
  status: "pending" | "processed" | "accepted";
  pdf_id?: string | null;
}

interface Proposal extends ProposalInfos {
  id: string;                 // uuid local
  pdfUrl: string;             // blob URL
  extractedObject?: DevisData | null;
  validationReport?: ValidationReport | null;
}

interface ValidationReport {
  computed_total_ht: number;
  computed_total_tva: number;
  computed_total_ttc: number;
  computed_total_cout_additionnel: number;
  logs: string[];
  errors: ValidationError[];
}

/* ------------------------------------------------------------------ */
/* Helpers API                                                        */
/* ------------------------------------------------------------------ */

async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${res.status}`);

  if (res.status === 204 || res.status === 205) return null as unknown as T;

  const txt = await res.text();
  if (!txt) return null as unknown as T;

  try {
    return JSON.parse(txt) as T;
  } catch {
    return txt as unknown as T;
  }
}

async function fetchAllProposalsInfos(
  email: string,
  projectName: string,
): Promise<ProposalInfos[]> {
  return apiFetch<ProposalInfos[]>(
    `${process.env.NEXT_PUBLIC_API_BASE}/api/users/get_all_proposals_infos`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_email: email,
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

  /* rectangle rouge */
type Highlight = { polygon: number[]; page: number };
const [highlight, setHighlight] = useState<Highlight | null>(null);

  /* ----------------- charge la liste initiale ----------------- */
  useEffect(() => {
    (async () => {
      try {
        const infos = await fetchAllProposalsInfos("test_email@test.fr", project.title);
        setProposals(
          infos.map((inf) => ({
            ...inf,
            id: crypto.randomUUID(),
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
            <ul className="space-y-2">
              {proposals.map((p) => (
                <li key={p.id}>
                  <button
                    onClick={() => handleSelect(p.id)}
                    className={`w-full flex items-center justify-between rounded-lg p-2 text-left ${
                      p.id === selectedId
                        ? "bg-primary-50 text-primary-700"
                        : "hover:bg-neutral-100"
                    }`}
                  >
                    <span className="truncate pr-2">{p.title}</span>
                    {p.status === "pending"   && <CircleDot   className="w-4 h-4 text-neutral-400" />}
                    {p.status === "processed" && <Scan        className="w-4 h-4 text-amber-500" />}
                    {p.status === "accepted"  && <CheckCircle className="w-4 h-4 text-green-600" />}
                  </button>
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

