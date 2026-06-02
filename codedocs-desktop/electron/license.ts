// ── License verification module ────────────────────────────────────
// MVP: decodes JWT payload and checks app_id + expiry.
// Signature verification (Ed25519) is NOT implemented yet — see TODO below.

export interface LicensePayload {
  app_id: string;
  edition: string;
  modules: string[];
  customer_id: string;
  expires_at: string;
}

export interface LicenseResult {
  valid: boolean;
  payload?: LicensePayload;
  error?: string;
  graceRemaining?: number;
}

const GRACE_PERIOD_DAYS = 7;
const MS_PER_DAY = 86_400_000;

/** Decode a base64url string to UTF-8 */
function base64urlDecode(input: string): string {
  // Replace URL-safe chars and pad
  let base64 = input.replace(/-/g, "+").replace(/_/g, "/");
  const pad = base64.length % 4;
  if (pad === 2) base64 += "==";
  else if (pad === 3) base64 += "=";
  return Buffer.from(base64, "base64").toString("utf-8");
}

export function verifyLicense(key: string): LicenseResult {
  // ── Empty / too short ────────────────────────────────────────────
  if (!key || key.trim().length < 10) {
    return { valid: false, error: "Chave vazia ou muito curta" };
  }

  // ── Must be JWT format (header.payload.signature) ────────────────
  const parts = key.trim().split(".");
  if (parts.length !== 3) {
    return { valid: false, error: "Formato invalido — esperado JWT (3 partes)" };
  }

  // ── Decode payload ───────────────────────────────────────────────
  let payload: LicensePayload;
  try {
    const json = base64urlDecode(parts[1]);
    payload = JSON.parse(json) as LicensePayload;
  } catch {
    return { valid: false, error: "Payload JWT invalido" };
  }

  // ── Check app_id ─────────────────────────────────────────────────
  if (payload.app_id !== "codedocs-desktop") {
    return { valid: false, error: "Licenca nao pertence a este aplicativo" };
  }

  // ── Check expiry + grace period ──────────────────────────────────
  const expiresAt = new Date(payload.expires_at).getTime();
  if (Number.isNaN(expiresAt)) {
    return { valid: false, error: "Data de expiracao invalida" };
  }

  const now = Date.now();
  const daysPastExpiry = (now - expiresAt) / MS_PER_DAY;

  if (daysPastExpiry > GRACE_PERIOD_DAYS) {
    return { valid: false, payload, error: "Licenca expirada alem do periodo de graca (7 dias)" };
  }

  // TODO: Verify Ed25519 signature using parts[0] (header) + parts[1] (payload)
  // against the public key embedded in the app. Skipped for MVP — any valid-format
  // JWT with correct app_id and unexpired date will pass.

  const graceRemaining =
    daysPastExpiry > 0
      ? Math.ceil(GRACE_PERIOD_DAYS - daysPastExpiry)
      : undefined;

  return { valid: true, payload, graceRemaining };
}
