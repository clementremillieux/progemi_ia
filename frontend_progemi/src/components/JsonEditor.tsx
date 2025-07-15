/* ------------------------------------------------------------------ */
/* JsonEditor.tsx – React / Next.js (client component)                */
/* ------------------------------------------------------------------ */
"use client";

import React, {
  PropsWithChildren,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  DndContext,
  DragEndEvent,
  DragStartEvent,
  PointerSensor,
  UniqueIdentifier,
  closestCenter,
  useDroppable,
  useSensor,
  useSensors,
  DragOverlay,
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { v4 as uuid } from "uuid";
import {
  ChevronDown,
  ChevronRight,
  GripVertical,
  Plus,
  Trash2,
  CheckCircle,
  XCircle
} from "lucide-react";



/* ------------------------------------------------------------------ */
/* Types utilitaires                                                  */
/* ------------------------------------------------------------------ */
type Path = string;
export interface HoverInfo { polygon: number[]; page: number }

export interface Produit {
  _uuid?: string;
  label: string;
  description: string;
  quantite: number;
  unitee_quantite: string | null;
  price_unitaire_ht: number;
  tva: string;
  eco_participation: number | null;
  sous_produits?: Produit[];
  lot: string;
  polygon?: number[];
  page?: number;
  issue?: string;
  issue_ht?: string;
  issue_ttc?: string;
  issue_tva?: string;
  issue_additional_cost?: string;
}

/* helpers JSON-path ------------------------------------------------ */
const split = (p: Path) => p.replace(/]/g, "").split(/\.|\[/).filter(Boolean);

export const get = (obj: any, path: Path) =>
  split(path).reduce((acc: any, k) => (acc ? acc[k] : undefined), obj);

export const set = (obj: any, path: Path, val: any) => {
  if (!path) return val;
  const keys = split(path);
  const last = keys.pop()!;
  const tgt = get(obj, keys.join(".")) ?? obj;
  tgt[last] = val;
  return { ...obj };
};

export const del = (obj: any, path: Path) => {
  const keys = split(path);
  const last = keys.pop()!;
  const tgt = get(obj, keys.join(".")) ?? obj;
  Array.isArray(tgt) ? tgt.splice(+last, 1) : delete tgt[last];
  return { ...obj };
};

/* assure un _uuid sur tous les objets ------------------------------ */
const ensureUUIDs = (n: any) => {
  if (Array.isArray(n)) n.forEach(ensureUUIDs);
  if (n && typeof n === "object") {
    if (!("_uuid" in n)) n._uuid = uuid();
    Object.values(n).forEach(ensureUUIDs);
  }
};

const emptyProduct = (): Produit => ({
  _uuid: uuid(),
  label: "",
  description: "",
  quantite: 0,
  unitee_quantite: null,
  price_unitaire_ht: 0,
  tva: "TVA_20",
  eco_participation: null,
  sous_produits: [],
  lot: "",
});

const TOTAL_ISSUE_MAP: Record<string, keyof Produit> = {
  devis_total_ht            : "issue_ht",
  devis_total_ttc           : "issue_ttc",
  devis_total_tva           : "issue_tva",
  devis_eco_participation    : "issue_additional_cost",
};

/* ------------------------------------------------------------------ */
/* Composant principal                                                */
/* ------------------------------------------------------------------ */
interface Props<T> {
  value: T;
  onChange: (v: T) => void;
  onHover?: (info: HoverInfo | null) => void;
}

function hasIssue(prod: Produit): boolean {
  if (prod.issue) return true;
  return !!prod.sous_produits?.some(hasIssue);
}

/** Parcourt toute la hiérarchie et injecte un flag booléen */
function setIssueFlag(node: any): void {
  if (Array.isArray(node)) { node.forEach(setIssueFlag); return; }
  if (node && typeof node === "object") {
    (node as any)._hasIssue = hasIssue(node);      // <- flag lu par <Row>
    node.sous_produits?.forEach(setIssueFlag);
  }
}

export default function JsonEditor<T>({
  value,
  onChange,
  onHover,
}: Props<T>) {
  /* ① injection des UUID */
  useEffect(() => {         // ← remplacez l’ancien useMemo
    ensureUUIDs(value);
    setIssueFlag(value);
  }, [value]);


  /* ② configuration DnD */
  const sensors = useSensors(useSensor(PointerSensor));
  const [activeId, setActiveId] = useState<UniqueIdentifier | null>(null);

  const [openGlobal, setOpenGlobal] = useState<Path | null>(null);

  /* ③ listes ouvertes */
  const [open, setOpen] = useState<Set<Path>>(new Set());
  const toggle   = (p: Path) => setOpen(s => new Set(s.has(p) ? [...s].filter(x => x!==p) : [...s, p]));
  const forceOpen= (p: Path) => setOpen(s => new Set([...s, p]));

  /* ④ map uuid → path */
  const uuidToPath = useMemo(() => {
    const m = new Map<string, Path>();
    const walk = (node: any, p = "") => {
      if (Array.isArray(node)) node.forEach((c,i)=>walk(c,`${p}[${i}]`));
      else if (node && typeof node === "object") {
        if (node._uuid) m.set(node._uuid,p);
        Object.entries(node).forEach(([k,v])=>walk(v,p?`${p}.${k}`:k));
      }
    };
    walk(value);
    return m;
  }, [value]);

  /* ⑤ déplacement */
  const move = useCallback((src: Path, dstArr: Path, dstIdx: number)=>{
    const srcArr = src.replace(/\[\d+\]$/,"");
    const srcIdx = +src.match(/\[(\d+)\]$/)![1];
    const from   = get(value,srcArr);
    const to     = get(value,dstArr);
    if (!Array.isArray(from)||!Array.isArray(to)) return;
    const [it] = from.splice(srcIdx,1);
    to.splice(dstIdx,0,it);
    onChange({...value});
  },[value,onChange]);

  const handleDragEnd = ({active,over}:DragEndEvent)=>{
    setActiveId(null);
    if(!over) return;
    const src = uuidToPath.get(String(active.id)); if(!src) return;
    if(uuidToPath.has(String(over.id))){
      const dst = uuidToPath.get(String(over.id))!;
      move(src,dst.replace(/\[\d+\]$/,""),+dst.match(/\[(\d+)\]$/)![1]);
    }else{
      const dstArr = String(over.id);
      const arr = get(value,dstArr);
      if(Array.isArray(arr)) move(src,dstArr,arr.length);
    }
  };

  /* ------------------------------------------------------------------ */
  /* rendu récursif                                                     */
  /* ------------------------------------------------------------------ */
  const render = (node:any, path:Path, label?:string):JSX.Element => {
   
    /* primitifs ------------------------------------------------------ */
    if (typeof node !== "object" || node === null) {
      const num      = typeof node === "number";
      const issueKey = TOTAL_ISSUE_MAP[label ?? ""] as keyof Produit | undefined;
      const issueMsg = issueKey ? (get(value, issueKey) as string | undefined) : undefined;
      const hasIssue = !!issueMsg;
      const isOpen   = openGlobal === path;           // ← affiché ?
      return (
        <div key={path} className="mb-1 flex items-center gap-1 relative">
          {/* icône validation (totaux seulement) */}
          {issueKey && (
            <button
              onClick={(e) => {                   // ← toggle bulle
                e.stopPropagation();
                setOpenGlobal(isOpen ? null : path);
              }}
              className="shrink-0"
            >
              {hasIssue
                ? <XCircle   className="h-5 w-5 text-red-600"/>
                : <CheckCircle className="h-5 w-5 text-green-600"/>}
            </button>
          )}

          {/* label + input */}
          <div className="flex-1">
            {label && <label className="text-xs font-medium">{label}</label>}
            <input
              className="border rounded w-full text-xs px-1"
              type={num ? "number" : "text"}
              value={node ?? ""}
              onChange={e =>
                onChange(
                  set(
                    value,
                    path,
                    num ? +e.currentTarget.value || 0 : e.currentTarget.value,
                  ),
                )
              }
            />
          </div>

          {/* bulle erreur globale */}
          {isOpen && hasIssue && (
            <div
              className="absolute -top-6 left-8 bg-white border rounded shadow px-2 py-0.5 text-xs z-20"
              onClick={(e)=>e.stopPropagation()}  /* évite la fermeture immédiate */
            >
              {issueMsg}
            </div>
          )}
        </div>
      );
    }


    /* tableaux ------------------------------------------------------- */
    if(Array.isArray(node)){
      const opened = open.has(path);
      const ids = node.map((c,i)=>(c._uuid ?? `${path}[${i}]`) as string);
      return(
        <DroppableArray
          key={path}
          path={path}
          opened={opened}
          label={label}
          length={node.length}
          onToggle={()=>toggle(path)}
          onAutoOpen={()=>forceOpen(path)}
        >
          <SortableContext items={ids} strategy={verticalListSortingStrategy}>
            {node.map((item:Produit, i)=>(
              <Row
                key={ids[i]}
                id={ids[i]}
                product={item}
                onHover={onHover}
                onDelete={()=>onChange(del(value,`${path}[${i}]`))}
              >
                {render(item,`${path}[${i}]`, getLabel(item,i))}
              </Row>
            ))}
          </SortableContext>
          <button
            onClick={() => onChange(set(value, path, [...node, emptyProduct()]))}
            className="mt-1 text-xs text-blue-600 flex items-center gap-1"
          >
            <Plus className="w-3 h-3"/> Ajouter
          </button>
        </DroppableArray>
      );
    }

    /* objets --------------------------------------------------------- */
    const opened = open.has(path);
    const obj = node as Produit;
    return(
      <div
        key={path}
        className="border-l pl-2 ml-1"
        onMouseEnter={()=>onHover?.(obj.polygon&&obj.page?{polygon:obj.polygon,page:obj.page}:null)}
        onMouseLeave={()=>onHover?.(null)}
      >
        <div className="flex items-center cursor-pointer select-none" onClick={()=>toggle(path)}>
          {opened?<ChevronDown className="w-3 h-3"/>:<ChevronRight className="w-3 h-3"/>}
          <span className="ml-1 font-medium text-sm">{label}</span>
        </div>
        {opened && Object.entries(obj).map(([k,v])=>
          !["_uuid","polygon","page","issue"].includes(k) &&
          render(v, path?`${path}.${k}`:k, k)
        )}
      </div>
    );
  };

  return(
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={({active}:DragStartEvent)=>setActiveId(active.id)}
      onDragEnd={handleDragEnd}
    >
      {render(value,"","Devis")}
      <DragOverlay dropAnimation={null}>
        {activeId && <div className="p-1 bg-white border shadow text-xs">déplacement…</div>}
      </DragOverlay>
    </DndContext>
  );
}

/* ------------------------------------------------------------------ */
/* Sous-composants                                                    */
/* ------------------------------------------------------------------ */
function Row(
  props: PropsWithChildren<{
    id: string;
    product: Produit & { _hasIssue?: boolean };
    onDelete: () => void;
    onHover?: (h: HoverInfo | null) => void;
  }>,
) {
  const { id, product, onDelete, onHover, children } = props;
  const {
    setNodeRef, setActivatorNodeRef,
    attributes, listeners, transform, transition, isDragging,
  } = useSortable({ id });

  /* pop-up issue explicatif */
  const [open, setOpen] = useState(false);

  const hasIssue   = (product as any)._hasIssue ?? !!product.issue;
  const Icon       = hasIssue ? XCircle : CheckCircle;
  const iconColor  = hasIssue ? "text-red-600" : "text-green-600";

  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition,
               opacity: isDragging ? 0.4 : 1 }}
      className="relative border rounded bg-white mt-1 shadow-sm flex items-start gap-1 pl-1 py-1"
      onMouseEnter={() =>
        onHover?.(product.polygon && product.page ? { polygon: product.polygon, page: product.page } : null)
      }
      onMouseLeave={() => onHover?.(null)}
    >
      {/* poignée DnD */}
      <GripVertical
        ref={setActivatorNodeRef}
        {...attributes} {...listeners}
        className="h-5 w-5 cursor-grab opacity-60 shrink-0"
      />

      {/* icône validation */}
      <button
        className={`${iconColor} shrink-0`}
        onClick={(e) => { e.stopPropagation(); if (product.issue) setOpen(v => !v); }}
      >
        <Icon className="h-6 w-6" />
      </button>

      {/* contenu JSON */}
      <div className="flex-1 text-xs overflow-x-auto">{children}</div>

      {/* bouton poubelle */}
      <button
        onClick={onDelete}
        className="p-0.5 hover:bg-red-50 rounded shrink-0"
      >
        <Trash2 className="w-4 h-4 opacity-60" />
      </button>

      {/* bulle issue */}
      {open && product.issue && (
        <div className="absolute -top-6 left-12 bg-white border rounded shadow px-2 py-0.5 text-xs z-20">
          {product.issue}
        </div>
      )}
    </div>
  );
}

function DroppableArray(
  props:PropsWithChildren<{
    path:Path;
    opened:boolean;
    label?:string;
    length:number;
    onToggle:()=>void;
    onAutoOpen:()=>void;
  }>
){
  const {path,opened,label,length,onToggle,onAutoOpen,children}=props;
  const {setNodeRef,isOver}=useDroppable({id:path});

  useEffect(()=>{ if(isOver && !opened) onAutoOpen(); },[isOver,opened,onAutoOpen]);

  return(
    <div ref={setNodeRef}
      className={`relative border rounded p-1 mt-1 ${isOver?"bg-blue-50":"bg-gray-50"}`}>
      <div className="flex items-center cursor-pointer" onClick={onToggle}>
        {opened?<ChevronDown className="w-3 h-3"/>:<ChevronRight className="w-3 h-3"/>}
        <span className="ml-1 text-xs font-medium">{label} [{length}]</span>
      </div>
      {opened && <div className="pl-3">{children}</div>}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Helper d’étiquette “Produit …”                                     */
/* ------------------------------------------------------------------ */
function getLabel(item:any, idx:number){
  if(!item || typeof item!=="object") return `Produit ${idx}`;
  const label = item.label || `Produit ${idx}`;
  const total =
    item.price_total_ht ??
    (item.price_unitaire_ht ?? 0)*(item.quantite ?? 1) +
    (item.eco_participation ?? 0);
  const sp = Array.isArray(item.sous_produits)? item.sous_produits.length : 0;
  return `${label} — ${total.toFixed(2)} € — ${sp} SP`;
}
