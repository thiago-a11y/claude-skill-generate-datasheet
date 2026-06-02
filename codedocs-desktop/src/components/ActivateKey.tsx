import { useState } from "react";

interface ActivateKeyProps {
  onActivate: (key: string) => void;
  onClose: () => void;
  error?: string;
}

export default function ActivateKey({ onActivate, onClose, error }: ActivateKeyProps) {
  const [key, setKey] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-bg2 border border-bg3 rounded-xl shadow-2xl p-6 w-full max-w-md mx-4">
        <h2 className="text-lg font-semibold text-fg mb-1">Ativar Licenca Pro</h2>
        <p className="text-sm text-fg2 mb-4">
          Cole sua chave de licenca abaixo para desbloquear todos os documentos.
        </p>

        <textarea
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="eyJhbGciOiJFZERTQSIs..."
          rows={4}
          className="w-full bg-bg border border-bg3 rounded-lg px-3 py-2 text-sm text-fg font-mono placeholder:text-fg2/40 focus:outline-none focus:ring-1 focus:ring-accent resize-none mb-3"
        />

        {error && (
          <p className="text-sm text-red-400 mb-3">{error}</p>
        )}

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-fg2 hover:text-fg rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => onActivate(key)}
            disabled={key.trim().length === 0}
            className={`px-5 py-2 text-sm font-semibold rounded-lg transition-colors ${
              key.trim().length === 0
                ? "bg-bg3 text-fg2/50 cursor-not-allowed"
                : "bg-accent text-bg hover:bg-accent/90"
            }`}
          >
            Ativar
          </button>
        </div>
      </div>
    </div>
  );
}
