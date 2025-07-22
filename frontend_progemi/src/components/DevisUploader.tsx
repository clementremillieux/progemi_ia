"use client";

import React from "react";
import { Uploader } from "./Uploader";      // drag‑and‑drop ou input

interface Props {
  userEmail: string;
  projectName: string;
  onDone: (file: File) => void;
}

export const DevisUploader: React.FC<Props> = ({
  userEmail,
  projectName,
  onDone,
}) => {
  const handleFile = async (file: File) => {
    const form = new FormData();
    form.append("user_email", userEmail);
    form.append("project_name", projectName);
    form.append("file", file);

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE}/api/users/upload_proposal`,
      {
        method: "POST",
        body: form,
        credentials: "include",   // ← indispensable
      },
    );

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    onDone(file);                 // ProjectDetailPage met à jour l’état
  };

  return <Uploader onFileSelect={handleFile} accept=".pdf" />;
};
