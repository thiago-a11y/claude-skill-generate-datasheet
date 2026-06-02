import { useState, useEffect, useCallback } from "react";
import type { LicenseResult } from "../types/codedocs";

const STORAGE_KEY = "codedocs-license-key";

interface UseLicenseResult {
  isPro: boolean;
  graceRemaining: number | undefined;
  error: string | undefined;
  activate: (key: string) => Promise<void>;
  deactivate: () => void;
  showModal: boolean;
  setShowModal: (show: boolean) => void;
}

export default function useLicense(): UseLicenseResult {
  const [isPro, setIsPro] = useState(false);
  const [graceRemaining, setGraceRemaining] = useState<number | undefined>();
  const [error, setError] = useState<string | undefined>();
  const [showModal, setShowModal] = useState(false);

  // On mount: check stored key
  useEffect(() => {
    const storedKey = localStorage.getItem(STORAGE_KEY);
    if (!storedKey) return;

    window.codedocs
      .verifyLicenseKey(storedKey)
      .then((result: LicenseResult) => {
        if (result.valid) {
          setIsPro(true);
          setGraceRemaining(result.graceRemaining);
        } else {
          // Stored key is no longer valid — clear it
          localStorage.removeItem(STORAGE_KEY);
          setError(result.error);
        }
      })
      .catch(() => {
        // IPC failure — stay in free mode silently
      });
  }, []);

  const activate = useCallback(async (key: string) => {
    setError(undefined);
    try {
      const result: LicenseResult = await window.codedocs.verifyLicenseKey(key);
      if (result.valid) {
        localStorage.setItem(STORAGE_KEY, key);
        setIsPro(true);
        setGraceRemaining(result.graceRemaining);
        setShowModal(false);
      } else {
        setError(result.error);
      }
    } catch {
      setError("Erro ao verificar licenca");
    }
  }, []);

  const deactivate = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setIsPro(false);
    setGraceRemaining(undefined);
    setError(undefined);
  }, []);

  return { isPro, graceRemaining, error, activate, deactivate, showModal, setShowModal };
}
