import { describe, it, expect } from "vitest";
import { verifyLicense } from "../electron/license.js";

/** Helper: build a fake JWT with the given payload */
function fakeJWT(payload: Record<string, unknown>): string {
  const header = Buffer.from(JSON.stringify({ alg: "EdDSA", typ: "JWT" })).toString("base64url");
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const signature = "fakesignature";
  return `${header}.${body}.${signature}`;
}

describe("verifyLicense", () => {
  it("rejects empty key", () => {
    const result = verifyLicense("");
    expect(result.valid).toBe(false);
    expect(result.error).toContain("vazia");
  });

  it("rejects malformed key (not 3 parts)", () => {
    const result = verifyLicense("only-two.parts");
    expect(result.valid).toBe(false);
    expect(result.error).toContain("3 partes");
  });

  it("rejects expired key beyond grace period", () => {
    const expiredDate = new Date(Date.now() - 10 * 86_400_000).toISOString(); // 10 days ago
    const key = fakeJWT({
      app_id: "codedocs-desktop",
      edition: "pro",
      modules: ["all"],
      customer_id: "test-123",
      expires_at: expiredDate,
    });

    const result = verifyLicense(key);
    expect(result.valid).toBe(false);
    expect(result.error).toContain("expirada");
  });
});
