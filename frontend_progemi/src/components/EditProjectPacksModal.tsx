"use client";

import React, { useEffect, useState } from "react";
import { Modal } from "./ui/Modal";
import { Button } from "./ui/Button";
import {
  fetchUserPacks,
  fetchProjectPacks,
  updateProjectPacks,
} from "@/lib/projectPacks";

interface Props {
  projectName: string;
  isOpen: boolean;
  onClose: () => void;
  /** callback pour rafraîchir la liste des projets après MAJ */
  onUpdated?: () => void;
}

export const EditProjectPacksModal: React.FC<Props> = ({
  projectName,
  isOpen,
  onClose,
  onUpdated,
}) => {
  const [allPacks, setAllPacks] = useState<string[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  /* -- initial fetch -- */
  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);

    (async () => {
      const [available, current] = await Promise.all([
        fetchUserPacks(),
        fetchProjectPacks(projectName),
      ]);
      setAllPacks(available);
      setSelected(new Set(current));
      setLoading(false);
    })();
  }, [isOpen, projectName]);

  /* -- handlers -- */
  const toggle = (pack: string) => {
    setSelected((prev) => {
      const copy = new Set(prev);
      copy.has(pack) ? copy.delete(pack) : copy.add(pack);
      return copy;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    await updateProjectPacks(projectName, Array.from(selected));
    setSaving(false);
    onClose();
    onUpdated?.();
  };

  /* -- render -- */
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Lots du projet « ${projectName} »`}>
      {loading ? (
        <div className="flex justify-center py-8">
     
        </div>
      ) : (
        <div className="space-y-4">
          <ul className="max-h-64 overflow-y-auto space-y-2">
            {allPacks.map((pack) => (
              <li key={pack} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selected.has(pack)}
                  onChange={() => toggle(pack)}
                />
                <span>{pack}</span>
              </li>
            ))}
          </ul>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              label="Annuler"
              variant="outlined"
              tone="neutral"
              onClick={onClose}
            />
            <Button
              label="Enregistrer"
              variant="filled"
              tone="primary"
              disabled={saving}
              onClick={handleSave}
            />
          </div>
        </div>
      )}
    </Modal>
  );
};
