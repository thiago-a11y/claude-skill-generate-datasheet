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

This repository is a **documentation tools factory** with two products:

### Product 1: Claude Skills Factory (MIT, free)
A collection of 4 Claude Code skills (instruction files) that scan any codebase and
generate evidence-based documentation. Skills are `.md` files — no code, no dependencies.
Claude Code reads the instructions and executes them.

### Product 2: CodeDocs (BSL, commercial)
An offline Python CLI tool (v2.1) that does the same scanning but **without any AI, internet,
or data egress**. Designed for air-gapped environments, compliance-heavy industries
(finance, healthcare, defense, industrial), and codebases that cannot be sent to LLMs.

**Tested on SyneriumX CRM** (1071 source files, 341 endpoints, 54 tables, 771 commits) —
15+ scanner bugs fixed through 4 Perplexity review cycles. Final verdict from Perplexity:
"Pronto para piloto com cliente real exigente."

---

## Who built it? / Quem construiu?

- **Creator**: Thiago Xavier — Objetiva Solucao Empresarial (Brazil)
- **Contact**: thiago@objetivasolucao.com.br
- **GitHub**: https://github.com/thiago-a11y/claude-skill-generate-datasheet
- **Built in**: 5 days (May 27-31, 2026), ~30 commits, with Claude Code assistance

---

## Architecture / Arquitetura

```
+-------------------------------------------------------------+
|                     GitHub Repository                        |
+----------------------------+--------------------------------+
|   SKILLS (MIT, free)       |   CODEDOCS (BSL, commercial)   |
|                            |                                |
|   Instruction files that   |   Python CLI (stdlib only)     |
|   Claude Code reads and    |   that runs 100% offline.      |
|   executes. Requires       |   Zero AI, zero internet,      |
|   Claude Code + internet.  |   zero data egress.            |
|                            |                                |
|   skills/                  |   codedocs/                    |
|   +- generate-datasheet/   |   +- scanner.py  (18 funcs)   |
|   +- generate-api-client/  |   +- renderer.py (10 funcs)   |
|   +- generate-compliance/  |   +- migration.py (9 funcs)   |
|   +- health-badges/        |   +- cli.py      (4 funcs)    |
|                            |                                |
|   Output: 30+ MD files,    |   Output: 4 HTML files         |
|   2 HTML files, fixes      |   (scan report, sales,         |
|   applied with approval    |   tech spec, migration plan)   |
+----------------------------+--------------------------------+
|   docs/           — 7 Perplexity research + 25 generated    |
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

## CodeDocs Detail / Detalhe do CodeDocs

### Version: v2.1 (installed globally at /usr/local/bin/codedocs)

### How it works / Como funciona
```bash
codedocs /path/to/project                                      # basic scan
codedocs /path --migration --target react+fastapi --erp SAP TOTVS  # with migration plan
```

### Scanner (scanner.py — 18 functions, 787 LOC)
Uses `grep`, `find`, `git log` via `subprocess`. Detects:
- Languages (Python, PHP, C#, Java, Go, Rust, TypeScript, Delphi, VB6)
- Endpoints (REST routes, MVC controllers, Flask/FastAPI decorators)
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

### Migration Planner (migration.py — 9 functions, 1086 LOC)
Key functions:
- `_recommend_target(data)` — opinionated recommendation based on detected stack
- `analyze_migration(data, target, erps)` — full migration analysis orchestrator
- `_resolve_target(target_input)` — alias resolution for 6 targets
- `_build_equivalence_map(data, target_key)` — cross-stack technology mapping
- `_build_package_map(target_key)` — 20 package equivalences per target
- `_build_module_inventory(data)` — module list from scan data
- `_calc_complexity(module, data)` — complexity scoring with hour estimates
- `_calc_priority(module)` — priority ranking for migration order
- `_generate_phases(modules, data)` — 5-phase Strangler Fig roadmap

Capabilities:
- **6 target platforms**: React+FastAPI, React+Express, Angular+NestJS, Blazor, Vue+FastAPI, Go+React
- **30+ technology equivalences**: MVC->FastAPI, EF->Prisma, Razor->React, WinForms->SPA, etc.
- **20 package mappings**: auth, ORM, logging, testing, email, PDF, Excel, image, scheduling, etc.
- **3 ERP integration plans**: SAP (OData/RFC), TOTVS (REST/iPaaS), Oracle (REST)
- **Accuracy labels**: GREEN (90%+ safe), YELLOW (70-85%), RED (50-70% manual)
- **Source languages**: C#, Java, PHP (Laravel/Symfony/CI/procedural), Delphi, VB6
- **5-phase Strangler Fig roadmap** with effort estimates (story points -> hours)

### Renderer (renderer.py — 10 functions, 775 LOC)
Key functions:
- `_risk_score(data)` — weighted composite with brutal test/bus-factor penalties
- `_risk_narrative(score, data)` — contextual narrative for risk level
- `render_scan_report(data)` — full inventory with risk score
- `render_sales_datasheet(data)` — metrics bar, modules, honest limitations
- `render_technical_spec(data)` — "6 answers in 60 seconds", security matrix
- `render_migration_plan(data, plan)` — target selector, equivalences, phased roadmap

Risk Score formula (renderer.py):
- Test Coverage: 35% weight, cap at 30 if 0 tests + 50+ files
- Bus Factor: 25% weight, cap at 35 if 1 contributor + 50+ files
- Security Controls: 15% weight
- Tech Debt Density: 10% weight
- Documentation: 8% weight
- Dependency Management: 7% weight

### CLI (cli.py — 4 functions, 223 LOC)
- `main()` — argument parsing, orchestration, browser open
- `_calc_health_score(data)` — console health score (30% test weight)
- `_print_summary(data)` — terminal summary
- `_progress(step, total, label)` — progress bar

### Key Design Decisions
1. **Zero dependencies** — only Python stdlib (no pip install)
2. **Zero internet** — all scans are local grep/find/git
3. **Zero AI** — intelligence is lookup tables and scoring formulas
4. **Deterministic** — same input = same output, auditable
5. **BSL license** — free for internal use, commercial for resale/hosting
6. **Risk Score not Health Score** — renamed after Perplexity review; brutal weighting
7. **Opinionated recommendations** — `_recommend_target()` picks best-fit based on stack
8. **Contextual copy** — placeholders replaced with industry-standard suggestions

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
- CodeDocs v2.1 (offline CLI with full migration planner, Risk Score, contextual copy, opinionated recommendations)
- CodeDocs installed globally at /usr/local/bin/codedocs
- Tested on SyneriumX CRM (1071 files, 341 endpoints, 54 tables) — 15+ bugs fixed
- 4 Perplexity review cycles completed — final verdict: production-ready
- 25 docs files + 7 research docs
- ~30 commits over 5 days

### Risk Score: 42/100

Renamed from "Health Score" after Perplexity review #2. Brutal weighting:
- Test Coverage: 35% weight (was 20%). Zero tests cap score at 30.
- Bus Factor: 25% weight (was 15%). Single contributor caps at 35.
- Security Controls: 15%
- Tech Debt Density: 10%
- Documentation: 8%
- Dependency Management: 7%

| Dimension | Score | Why |
|-----------|-------|-----|
| Test Coverage | 0/100 | 0 test files for 2876 LOC |
| Security Posture | 90/100 | Zero deps, zero network, HTML escaping |
| Tech Debt | 95/100 | 0 TODOs in source code |
| Documentation | 100/100 | 25+ markdown files |
| Bus Factor | 20/100 | 1 contributor on all modules |
| Dependency Health | 100/100 | Zero dependencies |

### Known Gaps / Lacunas
1. **Zero tests** — no pytest, no smoke tests, no CI
2. **Bus factor = 1** — single contributor, no external testers
3. **CodeDocs tested on 1 real project** — SyneriumX only, needs DiamondOne
4. **CodeDocs regex-based** — no AST parsing (tree-sitter planned for future)
5. **No CI/CD pipeline** — no .github/workflows/
6. **Reddit post not yet published** — script ready, credentials not configured
7. **4 copy adjustments remaining** from Perplexity review (minor)

### Pendencies / Pendencias
1. Clone DiamondOne from BitBucket -> run CodeDocs (first commercial use case)
2. Create Reddit App -> configure credentials -> publish launch post
3. Apply 4 remaining copy adjustments from Perplexity review
4. Add pytest smoke tests for CodeDocs scanner + renderer
5. Create GitHub Actions workflow (lint + test)
6. Tag releases (v4.1.0 for skills, v2.1 for CodeDocs)

---

## Business Model / Modelo de Negocio

### Strategy (validated by research)
1. **Skills (MIT, free)** -> adoption + GitHub stars + reputation
2. **Consultoria (short-term revenue)** -> "I run CodeDocs on your codebase and deliver the pack" (R$ 2-8K per project)
3. **CodeDocs (BSL, mid-term)** -> commercial license for resale/hosting
4. **SaaS (long-term)** -> hosted scans, team dashboard, history, exports

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
| Output | PDF assessment | Markdown + HTML + CSV + migration plan |
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
- PyInstaller single binary distribution
- pip install codedocs
- Docker image for CI/CD
- Tree-sitter parsing for higher accuracy
- Quality gates (block merge if doc score drops)

### SaaS (vision)
- Free: CLI/skill (everything today)
- Pro: hosted scans, dashboard, PDF export, badges
- Team: multiple repos, approval workflows, templates
- Enterprise: SSO/SAML, evidence retention, CI/CD integration

---

## How to Help / Como Ajudar

If you're an AI reading this, here's what the creator needs help with:

1. **Code review** — is the Python code in codedocs/ well-structured? Any bugs?
2. **Missing equivalences** — are there technology mappings we missed in migration.py?
3. **Marketing** — how to position this for maximum adoption?
4. **Monetization** — is the BSL + consultoria model realistic?
5. **Architecture** — should CodeDocs be restructured as the feature set grows?
6. **Testing** — what should the first pytest tests cover?
7. **Distribution** — PyInstaller vs pip vs Docker — what first?
8. **Competition** — are there new tools we should know about?

If you're a human reading this:
- **Star the repo** if you find it useful
- **Open an issue** if something doesn't work
- **Run `/generate-datasheet`** on your codebase and tell us what's missing
- **Try `codedocs /your/project`** and report the results
