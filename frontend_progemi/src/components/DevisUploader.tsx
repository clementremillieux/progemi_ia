"use client";

import React from "react";
import { Uploader } from "./Uploader";         // ton composant drag & drop

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
      { method: "POST", body: form },
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    onDone(file);                 // on laisse ProjectDetailPage gérer l’état
  };

  return <Uploader onFileSelect={handleFile} accept=".pdf" />;
};
