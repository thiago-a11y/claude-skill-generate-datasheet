## Project: Claude Skills Factory

This repo is a collection of Claude Code skills — reusable instruction files
that give Claude Code specialized capabilities for any codebase.

### What this repo IS
- A monorepo of Claude Code skill files (each in `skills/{name}/SKILL.md`)
- Each skill is a standalone file — no dependencies, no build step
- README.md is the GitHub landing page with install instructions
- MIT licensed, open source

### What this repo is NOT
- Not a Node.js project — no package.json, no dependencies, no build step
- Not an app — skills are instruction files that Claude Code loads and follows
- Not stack-specific — skills work with any language/framework

### Repo structure
```
skills/
  generate-datasheet/
    SKILL.md          — v4.1: scan → document → diagnose → fix (6 layers + AI cost audit)
  generate-api-client/
    SKILL.md          — v1.0: Postman collection + integration guides + webhooks + auth
  generate-compliance/
    SKILL.md          — v1.0: CAIQ/SIG/LGPD questionnaires from code evidence
  health-badges/
    SKILL.md          — v1.0: SVG badges for README from real metrics
codedocs/             — CodeDocs v3.0 (BSL, offline CLI)
  cli.py              — 244 LOC, argument parsing, orchestration
  scanner.py          — 1426 LOC, 28 functions, pure Python scanner (no grep/find/wc)
  scanner_shell.py    — 997 LOC, legacy shell-based scanner (kept for reference)
  renderer.py         — 1390 LOC, 25 functions, 5 HTML generators + Risk Score + i18n
  migration.py        — 1158 LOC, 9 functions, 30+ equivalences, 7 targets
  md_renderer.py      — 389 LOC, 14 functions, 11 Markdown doc generators
  sap_detection.py    — 125 LOC, SAP ecosystem detection (B1/Fiori/CAP/HANA/ABAP)
  i18n/               — ~200 keys: pt_BR.json + en_US.json
codedocs-desktop/     — CodeDocs Desktop v1.0.0 (Electron + React + Python sidecar)
  electron/           — main.ts, preload.ts, sidecar.ts, license.ts, updater.ts
  src/                — React app: pages, components, hooks, types
  python/             — Python wrapper (JSON stdio protocol)
  scripts/            — Build scripts (PyInstaller)
  release/            — Built installers (.exe + .dmg)
  tests/              — Vitest tests
tests/                — pytest: test_i18n.py, test_targets.py
docs/                 — 25 files: 7 research + 18 generated docs
  feedback-perplexity-review*.md  — 4 Perplexity review cycles
  research-*.md       — 7 research queries that shaped every layer
  planning-layers-roadmap.md      — Detailed planning: layers, SaaS tiers, skill priorities
README.md             — GitHub landing page (install, usage, examples)
ROADMAP.md            — Vision: versions, SaaS, new skills
CLAUDE.md             — This file (repo context for Claude Code)
CONTEXT.md            — Full project context for any AI/LLM (paste in external chats)
```

### Research foundation
The `docs/` directory contains the research and planning that justify every design
decision. 11 Perplexity research queries cover: AI branding, CTO expectations,
IT procurement, exemplary SaaS docs, vibe-coding crisis, tech debt tools gap,
"can't go back" features, scan→fix trust orchestration, monetization, offline doc tool,
migration planning, and migration equivalences.
These are the source of truth for the roadmap — read them before proposing new features.

### CodeDocs CLI (v3.0)
CodeDocs is an offline Python CLI (BSL licensed) that scans codebases without AI or internet.
Pure Python scanner (no grep/find/wc) — works on Windows, Mac, Linux.
i18n support: PT-BR + EN-US with ~200 keys. 7 migration targets including SAP Fiori/UI5.
5 HTML outputs + 11 Markdown full docs pack. .codedocsignore for custom exclusions.
Key modules: scanner.py (28 funcs, 1426 LOC), renderer.py (25 funcs, 1390 LOC),
migration.py (9 funcs, 1158 LOC), md_renderer.py (14 funcs, 389 LOC),
sap_detection.py (125 LOC). Installed at /usr/local/bin/codedocs.

### CodeDocs Desktop (v1.0.0)
Electron + React + Vite + TailwindCSS desktop application with Python sidecar.
Drag-and-drop folder scanning, tabbed results viewer, PDF export.
Freemium licensing with Ed25519 signed keys. Auto-update via electron-updater.
Installers: .exe (Windows) + .dmg (Mac). Located at codedocs-desktop/.

### Rules for contributing
- Each skill lives in its own directory under `skills/`
- Each skill is a single SKILL.md file — no code, no dependencies
- README.md documents all skills with install instructions
- Do NOT add dependencies, build tools, or frameworks
- Do NOT add code that runs — skills instruct Claude Code what to do
- Keep language in English (README has a PT-BR section for Brazilian users)
- Version follows semver in each SKILL.md frontmatter `version:` field
- Every new layer or major feature = major version bump
- Every improvement to existing layer = minor version bump
- Every fix = patch version bump

### Adding a new skill
1. Create `skills/{skill-name}/SKILL.md` with frontmatter (name, version, description, allowed-tools)
2. Add install instructions to README.md
3. Add the skill to the roadmap if it was planned
4. Update this structure section

### Mandatory doc updates / Atualização obrigatória de docs
When the user asks to "update docs", "atualizar docs", "sync documentation", or
"update the context", you MUST update ALL of the following files:
1. `CONTEXT.md` — full project context (architecture, features, state, gaps, roadmap)
2. `docs/architecture.md` — system design, modules, stack, diagrams
3. `docs/CHANGELOG.md` — add new entries from recent git log
4. `docs/health-score.md` — recalculate score from current state
5. `docs/bus-factor-report.md` — update contributor counts
6. `docs/backlog.md` — sync with ROADMAP.md
7. `docs/pendencies.md` — update blocked items and missing configs
8. `docs/bugs-known.md` — add/remove based on current state
9. `docs/security.md` — update controls matrix
10. `CLAUDE.md` — update skills catalog, version history, structure if changed
11. `README.md` — update version badges, install instructions if paths changed

Do NOT skip any file. Do NOT ask "which files?" — update all of them.
This ensures CONTEXT.md is always a reliable source of truth for external AIs.

### Anti-hallucination is non-negotiable (generate-datasheet)
The generate-datasheet skill's core value is evidence-based documentation. When editing it:
- Every scan command must be a real, runnable shell command
- Every template must include `<!-- source: {file}:{line} -->` comments
- Uncertainty markers ([VERIFY], [NOT DETECTED], [MANUAL]) must never be removed
- The correction engine (Layer 6) must never bypass the approval step
- Phase 2 (inventory presentation) must always happen before generation

### Skills catalog

| Skill | Version | Purpose |
|-------|---------|---------|
| `generate-datasheet` | v5.0.0 | Scan → Document → Diagnose → Fix → PRD (7 layers + AI cost audit + Reverse PRD) |
| `generate-api-client` | v1.0.0 | Postman collection + integration guides + webhook docs + auth setup |
| `generate-compliance` | v1.0.0 | CAIQ/SIG pre-filled from code evidence + LGPD/GDPR data mapping |
| `health-badges` | v1.0.0 | SVG health badges for README (test coverage, deps, bus factor, etc.) |

### Version history (generate-datasheet)
- v1.0 — 2 HTML files (sales datasheet + technical spec)
- v2.0 — + internal MD docs (12 files) + security pack (5 files)
- v2.1 — + Layer 4 evolution report (tech radar, dependency audit)
- v3.0 — + Layer 5 operational intelligence (onboarding, bus-factor, runbooks, health score)
- v4.0 — + Layer 6 assisted correction engine (scan → propose → approve → fix → verify)
- v4.1 — + AI API Cost Audit in Layer 4 (callsite inventory, model mapping, downgrade recommendations)
- v5.0 — + Layer 7 Reverse PRD (As-Is auto-generation → Gate 1 → adaptive interview → To-Be → Gate 2 → docs/prd.md + ADR files)

### Version history (CodeDocs CLI)
- v1.0 — Offline CLI with scanner + renderer (scan report, sales, tech spec)
- v1.1 — + Migration Planner + C# MVC support + ERP integration plans
- v1.2 — + Target selector + technology equivalences + package mapping
- v1.3 — + Full equivalence tables (Java, PHP, Delphi, VB6, 20 packages)
- v1.3.1 — + Full PHP support (Laravel, Symfony, CodeIgniter, CakePHP, procedural)
- v1.4 — + Migration plan by default + neutral target comparison
- v2.0 — 3 surgical cuts: Risk Score, contextual copy, opinionated recommendations
- v2.1 — Polish: executive summary, risk narrative, unified messaging. Perplexity-approved.
- v3.0 — Pure Python scanner, i18n (PT-BR + EN-US), Decision Brief, SAP detection, .codedocsignore, 7 targets, full docs pack (11 MD), Executive Verdict, Audit Readiness, ROI

### Version history (CodeDocs Desktop)
- v1.0.0 — Electron + React app, drag-and-drop, tabbed viewer, PDF export, freemium licensing (Ed25519), auto-update, Windows + Mac installers
