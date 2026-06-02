import { describe, it, expect } from "vitest";
import { buildScanRequest, resolvePythonPath } from "../electron/sidecar.js";

describe("buildScanRequest", () => {
  it("produces valid JSON with command, path, and options", () => {
    const json = buildScanRequest("/some/project", { lang: "en", target: "react-node" });
    const parsed = JSON.parse(json);

    expect(parsed).toHaveProperty("command", "scan");
    expect(parsed).toHaveProperty("path", "/some/project");
    expect(parsed).toHaveProperty("options");
    expect(parsed.options).toHaveProperty("lang", "en");
    expect(parsed.options).toHaveProperty("target", "react-node");
  });

  it("defaults lang to pt-BR and omits target when not provided", () => {
    const json = buildScanRequest("/another/path");
    const parsed = JSON.parse(json);

    expect(parsed.command).toBe("scan");
    expect(parsed.path).toBe("/another/path");
    expect(parsed.options.lang).toBe("pt-BR");
    expect(parsed.options).not.toHaveProperty("target");
  });
});

describe("resolvePythonPath", () => {
  it("returns path containing wrapper.py in dev mode", () => {
    const result = resolvePythonPath(false);

    expect(result.python).toBe("python3");
    expect(result.wrapper).toContain("wrapper.py");
    expect(result.wrapper).toContain("python");
    expect(result.repoRoot).toBeTruthy();
  });

  it("returns bundled path in prod mode", () => {
    const result = resolvePythonPath(true, "/app/resources");

    expect(result.python).toContain("/app/resources/python/codedocs-wrapper");
    expect(result.wrapper).toBe("");
    expect(result.repoRoot).toBeTruthy();
  });
});
