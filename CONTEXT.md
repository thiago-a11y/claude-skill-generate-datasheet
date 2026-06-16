# Project Context — Claude Skills Factory + CodeDocs

> Este documento e o ponto de entrada para qualquer IA, LLM, ou humano que precise
> entender o projeto completo. Cole este arquivo em qualquer chat com Claude, GPT,
> Gemini, ou outra IA para obter feedback, ideias, e sugestoes informadas.
>
> This document is the entry point for any AI, LLM, or human who needs to understand
> the full project. Paste this file into any chat with Claude, GPT, Gemini, or another
> AI for informed feedback, ideas, and suggestions.

---

## What is this project? / O que e este projeto?

This repository is a **documentation tools factory** with three products:

### Product 1: Claude Skills Factory (MIT, free)
A collection of 4 Claude Code skills (instruction files) that scan any codebase and
generate evidence-based documentation. Skills are `.md` files — no code, no dependencies.
Claude Code reads the instructions and executes them.

### Product 2: CodeDocs CLI (BSL, commercial)
An offline Python CLI tool (v3.0) that does the same scanning but **without any AI, internet,
or data egress**. Pure Python scanner (no grep/find/wc — works on Windows, Mac, Linux).
Designed for air-gapped environments, compliance-heavy industries
(finance, healthcare, defense, industrial), and codebases that cannot be sent to LLMs.

### Product 3: CodeDocs Desktop (BSL, commercial)
An Electron + React desktop application with a Python sidecar. Drag-and-drop folder scanning,
tabbed results viewer, PDF export, freemium licensing (Ed25519 signed keys), auto-update.
Installers available: `.exe` (Windows) and `.dmg` (Mac).

**Tested on SyneriumX CRM** (1071 source files, 341 endpoints, 54 tables, 771 commits) —
15+ scanner bugs fixed through 4 Perplexity review cycles. Final verdict from Perplexity:
"Pronto para piloto com cliente real exigente."

---

## Who built it? / Quem construiu?

- **Creator**: Thiago Xavier — Objetiva Solucao Empresarial (Brazil)
- **Contact**: thiago@objetivasolucao.com.br
- **GitHub**: https://github.com/thiago-a11y/claude-skill-generate-datasheet
- **Built in**: 3 weeks (May 27 — Jun 16, 2026), ~60 commits, with Claude Code assistance

---

## Architecture / Arquitetura

```
+-------------------------------------------------------------+
|                     GitHub Repository                        |
+----------------------------+--------------------------------+
|   SKILLS (MIT, free)       |   CODEDOCS CLI (BSL)           |
|                            |                                |
|   Instruction files that   |   Python CLI (stdlib only)     |
|   Claude Code reads and    |   Pure Python scanner.         |
|   executes. Requires       |   Zero AI, zero internet,      |
|   Claude Code + internet.  |   zero data egress.            |
|                            |   i18n: PT-BR + EN-US          |
|   skills/                  |                                |
|   +- generate-datasheet/   |   codedocs/                    |
|   +- generate-api-client/  |   +- scanner.py    (28 funcs)  |
|   +- generate-compliance/  |   +- renderer.py   (25 funcs)  |
|   +- health-badges/        |   +- migration.py  (9 funcs)   |
|                            |   +- md_renderer.py(14 funcs)  |
|   Output: 30+ MD files,    |   +- sap_detection.py          |
|   2 HTML files, fixes      |   +- cli.py        (6 funcs)   |
|   applied with approval    |   +- i18n/ (PT-BR + EN-US)     |
|                            |                                |
|                            |   Output: 5 HTML + 11 MD files |
|                            |   (scan, sales, tech spec,     |
|                            |   migration, decision brief,   |
|                            |   + full docs pack)            |
+----------------------------+--------------------------------+
|   CODEDOCS DESKTOP (BSL, commercial)                        |
|   Electron + React + Vite + TailwindCSS                     |
|   Python sidecar (JSON stdio protocol)                      |
|   Drag-and-drop, tabbed viewer, PDF export                  |
|   Freemium licensing (Ed25519), auto-update                 |
|   Installers: .exe (Windows) + .dmg (Mac)                   |
+-------------------------------------------------------------+
|   docs/           — 7 Perplexity research + 25 generated    |
|   tests/          — pytest: i18n + migration targets        |
|   README.md       — GitHub landing page with install        |
|   ROADMAP.md      — v4->v5->v6->SaaS vision                |
|   CLAUDE.md       — Repo context for AI tools               |
|   CONTEXT.md      — This file (full project context)        |
+-------------------------------------------------------------+
```

---

## Skills Detail / Detalhe das Skills

### generate-datasheet v4.1 (flagship)
Scans any codebase and generates **6 layers** of documentation:

| Layer | What it generates | For whom |
|-------|------------------|----------|
| 1 — Internal Docs | 12 MD files (architecture, data dictionary, endpoints, glossary, changelog, security, roadmap, contributing, bugs, backlog, pendencies) | Dev team |
| 2 — Sales Datasheet | Dark theme HTML with persona filters, 3-layer depth, honest limitations | Executives, buyers |
| 3 — Technical Spec | "6 answers in 60 seconds", security controls matrix, known gaps | CTOs, IT managers |
| 4 — Evolution Report | Tech radar, dependency audit, migration recommendations, AI API cost audit | Tech leads |
| 5 — Operational Intelligence | Role-based onboarding (4 roles), bus-factor report, incident runbooks, risk score 0-100 | Ops, SRE, product |
| 6 — Correction Engine | Scan -> diagnose -> propose -> approve -> fix -> verify. Branch-based, 1 fix = 1 commit | All (with approval) |

Plus: Security Pack (whitepaper, data-residency, subprocessors, incident-response, backup-dr).

**Core differentiator**: Anti-hallucination protocol — every claim traces to file:line.
Uncertainty markers: `[VERIFY]`, `[NOT DETECTED]`, `[MANUAL]`, `[PARTIAL]`.

### generate-api-client v1.0
Generates Postman collection (JSON), integration guides per stack (React, Python, PHP, Node),
webhook documentation, and auth setup guide. All endpoints traced to code.

### generate-compliance v1.0
Pre-fills CAIQ and SIG Lite security questionnaires from code evidence. Generates
LGPD/GDPR data mapping, evidence manifest (JSON), and unsupported claims report.
Confidence levels: PROVEN / PARTIAL / UNVERIFIABLE.

### health-badges v1.0
Generates SVG badges for README from real codebase metrics: health score, test coverage,
dependency freshness, bus factor, doc coverage, tech debt. shields.io visual style.

---

## CodeDocs CLI Detail / Detalhe do CodeDocs CLI

### Version: v3.0 (installed globally at /usr/local/bin/codedocs)

### How it works / Como funciona
```bash
codedocs /path/to/project                                        # basic scan (PT-BR default)
codedocs /path --lang en-US                                      # scan in English
codedocs /path --target react+fastapi --erp SAP TOTVS             # with migration plan + target
codedocs /path --full-docs                                        # generate 11 MD files
codedocs /path --target sap-fiori-ui5                             # SAP Fiori migration target
```

### Scanner (scanner.py — 28 functions, 1426 LOC)
**Pure Python implementation** — no grep, find, or wc. Works on Windows, Mac, Linux without shell tools.
Uses `os.walk()`, file reading, `re` module. Supports `.codedocsignore` for custom exclusions.

Detects:
- Languages (Python, PHP, C#, Java, Go, Rust, TypeScript, Delphi, VB6)
- Endpoints (REST routes, MVC controllers, Flask/FastAPI decorators) + **endpoint criticality**
- Database (CREATE TABLE, migrations, EF/Prisma/Eloquent models)
- Authentication (JWT, OAuth, sessions, API keys, MFA, RBAC)
- Security (CORS, CSRF, rate limiting, encryption, headers, audit logging)
- Integrations (external APIs, SAP, TOTVS, Oracle, Stripe, etc.)
- Tests (test files count vs source files)
- Git history (commits, contributors, churn)
- Code health (TODOs, FIXMEs, LOC)
- Dependencies (npm, composer, pip, NuGet, go mod, cargo)
- Migration blockers (COM Interop, P/Invoke, System.Web, EDMX, BDE, ActiveX)
- Frameworks (Spring MVC, Laravel, Symfony, CodeIgniter, WinForms, WPF, Web Forms)
- **Ghost features** (code behind feature flags, commented-out blocks)
- **Bus factor by module** (single-owner modules from git blame)
- **Deprecated functions** (marked @deprecated, obsolete attributes)
- **SAP ecosystem** (B1, Fiori, CAP, HANA, ABAP via sap_detection.py)
- **Service classification** (monolith vs microservices detection)

### MD Renderer (md_renderer.py — 14 functions, 389 LOC) `NEW in v3.0`
Generates 11 Markdown documentation files from scan data:
- `render_architecture(data)` — system design, stack, modules
- `render_data_dictionary(data)` — tables, columns, types
- `render_endpoints(data)` — all routes with criticality
- `render_glossary(data)` — domain terms mapped to code
- `render_changelog(data)` — from git history
- `render_security(data)` — controls matrix with status tags
- `render_bugs_known(data)` — from FIXME/HACK/TODO
- `render_contributing(data)` — setup, test, PR process
- `render_health_score(data)` — explainable 0-100 score
- `render_bus_factor(data)` — single-owner modules, knowledge silos
- `render_evolution_report(data)` — tech radar, dependency audit
- `render_all_md(data)` — orchestrator for all 11 files

### SAP Detection (sap_detection.py — 1 function, 125 LOC) `NEW in v3.0`
Detects SAP ecosystem presence: SAP B1, Fiori/SAPUI5, CAP, HANA, ABAP.

### i18n (i18n/ — ~200 keys, 2 locales) `NEW in v3.0`
Full internationalization with PT-BR and EN-US. ~200 translation keys covering all
HTML outputs (scan report, sales datasheet, technical spec, migration plan, decision brief).
CLI flag: `--lang pt-BR` (default) or `--lang en-US`.

### Migration Planner (migration.py — 9 functions, 1158 LOC)
Key functions:
- `_recommend_target(data)` — opinionated recommendation based on detected stack
- `analyze_migration(data, target, erps)` — full migration analysis orchestrator
- `_resolve_target(target_input)` — alias resolution for 7 targets + aliases
- `_build_equivalence_map(data, target_key)` — cross-stack technology mapping
- `_build_package_map(target_key)` — 20 package equivalences per target
- `_build_module_inventory(data)` — module list from scan data
- `_calc_complexity(module, data)` — complexity scoring with hour estimates
- `_calc_priority(module)` — priority ranking for migration order
- `_generate_phases(modules, data)` — 5-phase Strangler Fig roadmap

Capabilities:
- **7 target platforms**: React+FastAPI, React+Express, Angular+NestJS, Blazor, Vue+FastAPI, Go+React, **SAP Fiori/UI5**
- **Target aliases**: react-node -> react+express, net-blazor -> blazor, sap-fiori-ui5
- **30+ technology equivalences**: MVC->FastAPI, EF->Prisma, Razor->React, WinForms->SPA, etc.
- **20 package mappings**: auth, ORM, logging, testing, email, PDF, Excel, image, scheduling, etc.
- **3 ERP integration plans**: SAP (OData/RFC), TOTVS (REST/iPaaS), Oracle (REST)
- **Accuracy labels**: GREEN (90%+ safe), YELLOW (70-85%), RED (50-70% manual)
- **Source languages**: C#, Java, PHP (Laravel/Symfony/CI/procedural), Delphi, VB6
- **5-phase Strangler Fig roadmap** with effort estimates (story points -> hours)
- **Target-specific recommendations** in sales datasheet and technical spec

### Renderer (renderer.py — 25 functions, 1390 LOC)
Key functions:
- `_risk_score(data)` — weighted composite with brutal test/bus-factor penalties
- `_risk_narrative(score, data, lang)` — contextual narrative for risk level
- `_executive_verdict(score, data, lang)` — **Executive Verdict** with ROI projections
- `_audit_readiness(data, lang)` — **Audit Readiness** assessment
- `render_scan_report(data, lang)` — full inventory with risk score
- `render_sales_datasheet(data, lang, target)` — metrics bar, modules, honest limitations
- `render_technical_spec(data, lang, target)` — "6 answers in 60 seconds", security matrix
- `render_migration_plan(data, plan, lang)` — target selector, equivalences, phased roadmap
- `render_decision_brief(data, plan, lang)` — **Decision Brief** (NEW — 1-page executive summary)

All render functions accept `lang` parameter for i18n support.

Risk Score formula (renderer.py):
- Test Coverage: 35% weight, cap at 30 if 0 tests + 50+ files
- Bus Factor: 25% weight, cap at 35 if 1 contributor + 50+ files
- Security Controls: 15% weight
- Tech Debt Density: 10% weight
- Documentation: 8% weight
- Dependency Management: 7% weight

### CLI (cli.py — 6 functions, 244 LOC)
- `main()` — argument parsing, orchestration, browser open
- `_calc_health_score(data)` — console health score (30% test weight)
- `_print_summary(data)` — terminal summary
- `_progress(step, total, label)` — progress bar
- Smart stack detection for target recommendations

### Key Design Decisions
1. **Zero dependencies** — only Python stdlib (no pip install)
2. **Zero internet** — all scans are pure Python file operations
3. **Zero AI** — intelligence is lookup tables and scoring formulas
4. **Deterministic** — same input = same output, auditable
5. **BSL license** — free for internal use, commercial for resale/hosting
6. **Risk Score not Health Score** — renamed after Perplexity review; brutal weighting
7. **Opinionated recommendations** — `_recommend_target()` picks best-fit based on stack
8. **Contextual copy** — placeholders replaced with industry-standard suggestions
9. **Pure Python scanner** — no shell dependencies (grep/find/wc), works on Windows
10. **i18n from day 1** — PT-BR + EN-US with ~200 keys
11. **.codedocsignore** — custom directory exclusion (like .gitignore)

---

## CodeDocs Desktop Detail / Detalhe do CodeDocs Desktop

### Version: v1.0.0

### Stack
- **Frontend**: Electron 35 + React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: Python sidecar (JSON stdio protocol)
- **Licensing**: Ed25519 signed keys (freemium: Free tier + Pro tier)
- **Auto-update**: electron-updater
- **Packaging**: electron-builder (Windows .exe + Mac .dmg)

### Architecture
```
codedocs-desktop/
+- electron/
|  +- main.ts        — Electron main process
|  +- preload.ts     — IPC bridge (contextBridge)
|  +- sidecar.ts     — Python process manager (spawn + JSON stdio)
|  +- license.ts     — Ed25519 license verification
|  +- updater.ts     — Auto-update via electron-updater
+- src/
|  +- App.tsx         — React app with routing
|  +- pages/          — DropZone, Progress, Results
|  +- components/     — UI components
|  +- hooks/          — useScan (IPC communication)
|  +- types/          — TypeScript interfaces
+- python/            — Python wrapper (JSON stdio protocol)
+- scripts/           — Build scripts (PyInstaller)
+- release/           — Built installers (.exe, .dmg)
+- tests/             — Vitest tests
```

### Features
- **Drag-and-drop** folder scanning (no CLI needed)
- **Tabbed viewer** for all generated outputs (HTML + MD)
- **PDF export** via window.print()
- **Freemium licensing**: Free tier (scan report + sales + tech spec) / Pro tier (migration + decision brief + full docs)
- **Auto-update** via GitHub Releases
- **Python sidecar**: spawns CodeDocs CLI as subprocess with JSON stdio protocol
- **Windows + Mac installers**: .exe (97 MB) + .dmg (107 MB)

---

## Perplexity Review Cycles (4 rounds)

| Round | Key Finding | Fix Applied |
|-------|------------|-------------|
| 1 | 7 critical issues: optimistic health score, "no gaps detected" lie, generic placeholders, sales = scan dump | Health Score brutalized, gaps always shown, copy rewritten |
| 2 | "Ferrari com painel de Gol 96" — motor great, copy amateur | 3 surgical cuts: Risk Score, contextual copy, opinionated recs |
| 3 | Copy polish needed — executive summary, risk narrative, unified messaging | v2.1: executive summary, risk narrative function, consistent voice |
| 4 | Final verdict: "Pronto para piloto com cliente real exigente" | No further changes needed |

---

## Research Foundation / Base de Pesquisa

11 Perplexity research sessions documented in `docs/`:

| Research | Key Finding | Impact |
|----------|------------|--------|
| AI branding in SaaS | Proprietary names (HubSpot "Breeze AI"), never list providers in sales | Layer 2 sales datasheet design |
| CTO expectations | "6 questions in <10 min", concrete security, not adjectives | Layer 3 technical spec |
| IT procurement | CAIQ/SIG required, SOC2, architecture proof | Security Pack + generate-compliance |
| Vibe-coding crisis | 70% of AI-built projects ship with zero docs | Core motivation for the project |
| Tech debt tools gap | No tool combines doc + detection + correction | Layer 4 + Layer 6 |
| "Can't go back" features | Onboarding packs, bus-factor, runbooks, health score | Layer 5 |
| Scan->Fix trust | Branch-based, per-item approval, confidence labels | Layer 6 correction engine |
| AI API cost audit | No tool does static analysis for LLM cost optimization | Layer 4 section 5.5.8 |
| Offline doc tool | No tool generates sales + tech + security docs offline | CodeDocs product |
| Migration planning | No tool does cross-stack migration offline (Razor->React, EF->Prisma) | CodeDocs migration planner |
| Migration equivalences | Complete tables C#/Java/PHP/Delphi/VB6 -> 6 target platforms | migration.py lookup tables |

---

## Current State / Estado Atual

### What's done / O que esta feito
- 4 Claude Code skills (generate-datasheet v4.1, generate-api-client v1.0, generate-compliance v1.0, health-badges v1.0)
- CodeDocs v3.0 (offline CLI with pure Python scanner, i18n, Decision Brief, 7 targets, SAP detection, full docs pack)
- CodeDocs Desktop v1.0.0 (Electron + React app with drag-and-drop, PDF export, freemium licensing, auto-update)
- CodeDocs installed globally at /usr/local/bin/codedocs
- Tested on SyneriumX CRM (1071 files, 341 endpoints, 54 tables) — 15+ bugs fixed
- 4 Perplexity review cycles completed — final verdict: production-ready
- Pure Python scanner — works on Windows, Mac, Linux (no grep/find/wc)
- i18n: PT-BR + EN-US with ~200 translation keys
- 7 migration targets including SAP Fiori/UI5
- 5 HTML outputs: scan report, sales datasheet, tech spec, migration plan, Decision Brief
- 11 Markdown full docs pack (architecture, data-dictionary, endpoints, glossary, changelog, security, bugs-known, contributing, health-score, bus-factor, evolution-report)
- .codedocsignore support for custom directory exclusion
- Windows (.exe) + Mac (.dmg) installers built
- pytest tests for i18n and migration targets
- ~60 commits over 3 weeks

### Risk Score: 45/100

Renamed from "Health Score" after Perplexity review #2. Brutal weighting:
- Test Coverage: 35% weight (was 20%). Zero tests cap score at 30.
- Bus Factor: 25% weight (was 15%). Single contributor caps at 35.
- Security Controls: 15%
- Tech Debt Density: 10%
- Documentation: 8%
- Dependency Management: 7%

| Dimension | Score | Why |
|-----------|-------|-----|
| Test Coverage | 15/100 | 2 test files (i18n + targets) for 5769 LOC |
| Security Posture | 90/100 | Zero deps (CLI), HTML escaping, Ed25519 signing |
| Tech Debt | 95/100 | 0 TODOs in source code |
| Documentation | 100/100 | 25+ markdown files |
| Bus Factor | 20/100 | 1 contributor on all modules |
| Dependency Health | 100/100 | Zero dependencies (CLI) |

### Known Gaps / Lacunas
1. **Low test coverage** — 2 pytest files (i18n + targets), no scanner/renderer tests
2. **Bus factor = 1** — single contributor, no external testers
3. **CodeDocs tested on 1 real project** — SyneriumX only, needs DiamondOne
4. **CodeDocs regex-based** — no AST parsing (tree-sitter planned for future)
5. **No CI/CD pipeline** — no .github/workflows/
6. **Reddit post not yet published** — script ready, credentials not configured
7. **Windows scan needs Git in PATH** — git-based features (history, contributors) require Git installed
8. **PDF export limited** — uses window.print(), content may be truncated on complex reports
9. **Desktop app not code-signed** — Windows SmartScreen / macOS Gatekeeper warnings

### Pendencies / Pendencias
1. Clone DiamondOne from BitBucket -> run CodeDocs (first commercial use case)
2. Create Reddit App -> configure credentials -> publish launch post
3. Add pytest tests for scanner + renderer + md_renderer
4. Create GitHub Actions workflow (lint + test)
5. Tag releases (v4.1.0 for skills, v3.0 for CodeDocs CLI, v1.0.0 for Desktop)
6. Code-sign Desktop app (Apple Developer ID + Windows Authenticode)
7. Publish Desktop app to GitHub Releases for auto-update

---

## Business Model / Modelo de Negocio

### Strategy (validated by research)
1. **Skills (MIT, free)** -> adoption + GitHub stars + reputation
2. **Consultoria (short-term revenue)** -> "I run CodeDocs on your codebase and deliver the pack" (R$ 2-8K per project)
3. **CodeDocs Desktop (BSL, mid-term)** -> freemium desktop app (Free tier + Pro tier with license key)
4. **CodeDocs commercial license** -> for resale/hosting
5. **SaaS (long-term)** -> hosted scans, team dashboard, history, exports

### Target Market
- **Skills**: indie devs, startups, open source projects
- **CodeDocs**: enterprise, industrial, regulated industries (finance, healthcare, defense)
- **Consultoria**: Brazilian SMEs with legacy systems (C#, Delphi, VB6, PHP)
- **First client**: Objetiva's own DiamondOne (industrial module, C# MVC, BitBucket)

### Competitive Advantage
| Dimension | Competitors | This Project |
|-----------|------------|-------------|
| Target platforms | Same-language upgrades | Cross-stack (Razor->React, EF->Prisma) |
| Deployment | Cloud/AI required | 100% offline, zero data egress |
| Price | $100K-500K/year (CAST Highlight) | $5K-20K one-time or free (skills) |
| Output | PDF assessment | Markdown + HTML + migration plan + Decision Brief |
| Desktop | N/A | Electron app with drag-and-drop, no CLI needed |
| i18n | English only | PT-BR + EN-US (extensible) |
| Trust | Black-box AI | Deterministic rules, file:line evidence |

---

## Roadmap / Roadmap

### v5.0 (planned for generate-datasheet)
- Layer 7: SDK & Integration Pack (Postman + integration guides per stack)
- Compliance Questionnaire Engine (CAIQ/SIG auto-fill)
- Live Health Badges (SVG for README)

### v6.0 (future)
- Layer 8: Observability Pack (Grafana/Datadog dashboards from code)
- Demo & Walkthrough Pack
- Training Pack per role

### CodeDocs (planned)
- Desktop app code signing (Apple Developer ID + Windows Authenticode)
- pip install codedocs (PyPI distribution)
- Docker image for CI/CD
- Tree-sitter parsing for higher accuracy
- Quality gates (block merge if doc score drops)
- More i18n locales (ES, DE, FR)

### SaaS (vision)
- Free: CLI/skill (everything today) + Desktop Free tier
- Pro: Desktop Pro tier + hosted scans, dashboard, badges
- Team: multiple repos, approval workflows, templates
- Enterprise: SSO/SAML, evidence retention, CI/CD integration

Note: Desktop app is the first commercial product (freemium model).
SaaS is a future evolution, not immediate priority.

---

## How to Help / Como Ajudar

If you're an AI reading this, here's what the creator needs help with:

1. **Code review** — is the Python code in codedocs/ well-structured? Any bugs?
2. **Missing equivalences** — are there technology mappings we missed in migration.py?
3. **Marketing** — how to position this for maximum adoption?
4. **Monetization** — is the BSL + Desktop freemium model realistic?
5. **Architecture** — should CodeDocs be restructured as the feature set grows?
6. **Testing** — scanner + renderer + md_renderer need pytest coverage
7. **Distribution** — Desktop app is built, needs code signing + GitHub Releases
8. **Competition** — are there new tools we should know about?
9. **i18n** — review EN-US translations (~200 keys), add more locales?
10. **Desktop UX** — is the drag-and-drop + tabbed viewer intuitive?

If you're a human reading this:
- **Star the repo** if you find it useful
- **Open an issue** if something doesn't work
- **Run `/generate-datasheet`** on your codebase and tell us what's missing
- **Try `codedocs /your/project`** and report the results
