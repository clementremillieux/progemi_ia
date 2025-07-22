export interface SousProduit {
  label: string;
  description: string;
  quantite: number;
  unitee_quantite: string;
  price_unitaire_ht: number;
  tva: string;
  lot: string;
}

export interface Produit {
  label: string;
  description: string;
  quantite: number;
  unitee_quantite: string;
  price_unitaire_ht: number;
  tva: string;
  lot: string;
  sous_produits?: SousProduit[] | null;
}

export interface DevisData {
  devis_id: string;
  devis_date: string;
  devis_total_ht: number;
  devis_total_ttc: number;
  devis_total_tva: number;
  devis_produits: Produit[];
  devis_items: {
    label: string;
    prixUnitaire: number;
    quantite: number;
  }[];
}

export type DevisStatus = "uploading" | "processing" | "completed" | "error";

export type DevisValidationStatus = "accepte" | "en_attente" | "refuse";

export interface Devis {
  id: string;
  fileName: string;
  status: DevisStatus;
  validationStatus: DevisValidationStatus;
  uploadDate: Date;
  data?: DevisData;
  error?: string;
  fournisseur?: string;
}

export interface DevisItem {
  label: string;
  prixUnitaire: number;
  quantite: number;
}

export type LotStatus = "non_demarre" | "en_cours" | "termine";

export interface Lot {
  id: string;
  numero: number;
  intitule: string;
  description: string;
  responsable: string;
  status: LotStatus;
  devis: Devis[];
  budgetPrevisionnel: number;
  depensesEngagees: number;
}

export type ProjectStatus = "valide" | "en_cours" | "en_attente";

export interface Project {
  id: string;
  title: string;
  packsCount: number;
  isPackToChoose: boolean;
  description: string;
  status: ProjectStatus
  devisCount: number;
}

/** Réponse brute de l’API */
export interface UserProjectOutput {
  project_name: string;
  packs_names: string[];
  is_pack_to_choose: boolean;
}