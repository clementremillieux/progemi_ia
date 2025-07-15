// src/components/Uploader.tsx
"use client";

import React, { useState, useRef } from "react";
import { Upload, AlertCircle, Check, Clock } from "lucide-react";

interface Props {
  onFileSelect: (file: File) => Promise<void> | void;
  accept?: string;
  maxSize?: number;
}

export const Uploader: React.FC<Props> = ({
  onFileSelect,
  accept = ".pdf",
  maxSize = 5_000_000,
}) => {
  const [status, setStatus] = useState<"idle"|"dragover"|"uploading"|"error"|"success">("idle");
  const [errorMsg, setErrorMsg] = useState<string|null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const reset = () => { setErrorMsg(null); setStatus("idle"); };

  const handleFile = async (file: File) => {
    if (file.size > maxSize) {
      setErrorMsg("Fichier trop volumineux");
      setStatus("error");
      return;
    }
    setStatus("uploading");
    try {
      await onFileSelect(file);
      setStatus("success");
      setTimeout(reset, 2000);
    } catch (e: any) {
      setErrorMsg(e.message || "Erreur");
      setStatus("error");
    }
  };

  const getClassName = () => {
    const base = "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all";
    
    switch(status) {
      case "dragover":
        return `${base} border-[var(--color-primary-60)] bg-[var(--color-primary-99)]`;
      case "error":
        return `${base} border-[var(--color-error-60)] bg-[var(--color-error-99)]`;
      case "success":
        return `${base} border-[var(--color-success-60)] bg-[var(--color-success-99)]`;
      default:
        return `${base} border-[var(--color-border)] bg-white hover:border-[var(--color-neutral-70)] hover:bg-[var(--color-neutral-99)]`;
    }
  };

  return (
    <div
      onClick={() => status!=="uploading" && inputRef.current?.click()}
      onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
      onDragOver={(e) => { e.preventDefault(); setStatus("dragover"); }}
      onDragLeave={() => setStatus("idle")}
      className={getClassName()}
    >
      {status==="uploading" && <Clock className="animate-spin mx-auto mb-4 w-8 h-8 text-[var(--color-primary-60)]"/>}
      {status==="error"     && <AlertCircle className="mx-auto mb-4 w-8 h-8 text-[var(--color-error-60)]"/>}
      {status==="success"   && <Check className="mx-auto mb-4 w-8 h-8 text-[var(--color-success-60)]"/>}
      {(status==="idle"||status==="dragover") && <Upload className="mx-auto mb-4 w-8 h-8 text-[var(--color-neutral-60)]"/>}

      <p className="font-medium mb-1 text-[var(--color-foreground)]">
        {status==="idle"      && "Cliquez ou déposez un PDF"}
        {status==="dragover"  && "Déposez pour uploader"}
        {status==="uploading" && "Upload en cours…"}
        {status==="error"     && errorMsg}
        {status==="success"   && "Upload réussi !"}
      </p>
      {status==="idle" && <p className="text-sm text-[var(--color-neutral-60)]">PDF uniquement, max {maxSize/1e6} Mo</p>}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
      />
    </div>
  );
};