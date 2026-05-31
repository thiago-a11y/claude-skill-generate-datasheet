# claude-skill-generate-datasheet

[![GitHub stars](https://img.shields.io/github/stars/thiago-a11y/claude-skill-generate-datasheet?style=flat&color=f59e0b)](https://github.com/thiago-a11y/claude-skill-generate-datasheet/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-f59e0b?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHBhdGggZD0iTTEyIDJMMiAyMmgyMEwxMiAyeiIgZmlsbD0iI2Y1OWUwYiIvPjwvc3ZnPg==)](https://docs.anthropic.com/en/docs/claude-code)
[![Version](https://img.shields.io/badge/version-4.1.0_|_CodeDocs_v2.1-green.svg)](https://github.com/thiago-a11y/claude-skill-generate-datasheet/releases)
[![Skills](https://img.shields.io/badge/skills-4-f59e0b.svg)](#skills-catalog)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#)
[![Docs Generated](https://img.shields.io/badge/docs_generated-30+_files-purple.svg)](#what-it-generates)
[![Scan & Fix](https://img.shields.io/badge/scan_%26_fix-with_approval-f59e0b.svg)](#layer-6--assisted-correction-engine-new-in-v4)

> The cure for vibe-coding without documentation.

A Claude Code skill that scans your codebase and generates a **complete documentation pack** — evidence-based, zero hallucination. Only documents what it can prove from actual files, configs, and code.

---

## Para que serve? (PT-BR)

Transforma qualquer código em um **manual de operações completo** — com zero invenção, tudo rastreável ao código real.

**Para o dev novo que entrou no time:**
> "Leia esses 12 arquivos primeiro, rode esses comandos pra configurar, não mexa nessa pasta porque é crítica, e aqui estão 5 tarefas seguras pra você começar."

**Para o CTO que precisa avaliar um software antes de comprar:**
> "O sistema roda aqui, os dados vão pra lá, a segurança cobre isso mas falta aquilo, a API funciona assim, e esses são os riscos reais."

**Para o gerente que quer saber onde o projeto está frágil:**
> "Esse módulo só uma pessoa mexe, não tem teste, é crítico pro negócio, e se essa pessoa sair ninguém sabe como funciona."

**Para o time que precisa responder quando o sistema cai:**
> "Se o banco cair, faça isso. Se a fila travar, olhe aqui. Se o login parar, o problema provavelmente está nesse arquivo."

**Para quem precisa vender o produto:**
> "Aqui está uma ficha técnica profissional pronta pra enviar pro cliente, com tudo que o TI dele vai perguntar já respondido."

**Para quem quer evoluir o sistema:**
> "Essas 5 dependências estão velhas, esse módulo tem dívida técnica crítica, e essa migração afeta 15 arquivos com esforço estimado de 2 dias."

---

## The Problem (EN)

AI-assisted coding tools (Cursor, Claude Code, Copilot, Windsurf, Bolt) are creating a generation of **functional projects that nobody can explain, maintain, or audit**:

- 70% of AI-built projects ship with zero architecture docs ([Addy Osmani, Google](https://beyond.addy.ie))
- Significant chunks of AI-generated code ship with security vulnerabilities ([Veracode 2025](https://dev.to/incomplete_developer/vibe-coding-is-not-the-problem-ignorance-is-13fj))
- Most existing doc generators (Docusaurus, MkDocs, Sphinx) generate **sites**, not **content**
- No tool generates architecture + data dictionary + security + sales docs from code

## What It Generates

### Layer 1 — Internal Documentation (Markdown)

| File | Content |
|------|---------|
| `architecture.md` | System design, stack, modules, ASCII diagrams |
| `backend-architecture.md` | API patterns, middleware, auth flow |
| `data-dictionary.md` | Tables, columns, types from actual migrations |
| `endpoints.md` | All routes, methods, auth levels |
| `glossary.md` | Domain terms mapped to code entities |
| `CHANGELOG.md` | From git history (quotes, not summaries) |
| `security.md` | Controls matrix with status tags |
| `roadmap.md` | From TODOs, issues, PRDs found in code |
| `contributing.md` | Setup, test, PR process from configs |
| `bugs-known.md` | From FIXME/HACK/TODO in codebase |
| `backlog.md` | Planned features from PRDs and issues |
| `pendencies.md` | Blocked items and missing configs |

### Layer 2 — Sales Datasheet (HTML)

For executives, buyers, and marketing teams.

- Dark theme, responsive, print-friendly (PDF via `window.print()`)
- Persona filter chips (Executives / IT / Buyers / Marketing)
- 3-layer depth: Title → Features → Technical accordion
- Credibility metrics from real codebase numbers
- **Honest limitations section** — mandatory
- AI features branded under proprietary name (like HubSpot's "Breeze AI")

### Layer 3 — Technical Specification (HTML)

For CTOs, IT managers, and infosec teams.

- "6 answers in 60 seconds" quick-reference header
- Architecture diagrams (ASCII context + container views)
- Data residency & subprocessors table
- Security controls matrix with status tags (Implemented / Partial / Not Available)
- API reference: auth, rate limits, webhooks
- SLA with RPO/RTO
- **Known gaps section** — brutally honest

### Security Pack (Markdown)

For compliance, infosec reviews, and procurement.

| File | Content |
|------|---------|
| `security-whitepaper.md` | Complete security posture with evidence |
| `data-residency.md` | Where data lives, moves, and is processed |
| `subprocessors.md` | External services with confirmed API calls |
| `incident-response.md` | Current capabilities + gaps |
| `backup-dr-policy.md` | RPO, RTO, restore process |

### Layer 4 — Evolution Report (Markdown) `NEW`

What SonarQube and CodeClimate can't do: explain WHY you should change, not just WHAT is wrong.

| Section | Content |
|---------|---------|
| `Tech Radar` | Adopt / Trial / Assess / Hold for your current stack |
| `Dependency Audit` | Outdated packages with upgrade impact and files affected |
| `Migration Recommendations` | "Migrate from X to Y because Z" with evidence |
| `Security Gaps` | Missing controls ranked by risk |
| `Test Coverage Gaps` | Source dirs with zero tests |
| `Tech Debt Prioritized` | TODOs/FIXMEs ranked by location criticality (auth > UI) |
| `Architecture Suggestions` | Structural improvements with effort estimates |

Each recommendation includes: **what was found** (file:line) → **why change** (EOL, CVE, performance) → **files affected** (grep count) → **effort estimate** → `[VERIFY]` if uncertain.

### Layer 5 — Operational Intelligence (Markdown) `NEW in v3`

The "can't go back" layer. No other tool generates this.

| File | Content |
|------|---------|
| `onboarding-backend.md` | "Read these 12 files first, run these commands, don't touch this module" |
| `onboarding-frontend.md` | Component tree, routing, state, design system, first safe PRs |
| `onboarding-sre.md` | Deploy process, cron jobs, health checks, monitoring, backups |
| `onboarding-product.md` | Module map, user flows, feature flags, config options |
| `bus-factor-report.md` | Single-owner modules, knowledge silos, action items |
| `runbooks/*.md` | "If database fails → check this. If queue stalls → do that." |
| `health-score.md` | Explainable 0-100 score: tests, debt, bus factor, security, docs |

### Layer 6 — Assisted Correction Engine `NEW in v4`

The full cycle no other tool does: **scan → diagnose → propose → approve → fix → verify**.

```
Found 14 issues:

#1 [HIGH] 23 files with trailing whitespace
   Fix: remove spaces | Blast radius: cosmetic only
   [ ] Approve

#3 [MEDIUM] api/auth.php:45 — password compared with ==
   Fix: change to password_verify() | Blast radius: 1 file, auth flow
   [ ] Approve

#7 [LOW] express 4.x → 5.x (15 files, breaking changes)
   ⚠ Plan only — requires human planning
   
Approve which? (1,3 or "all-high" or "all")
```

**Safety guarantees:**
- Never touches main — dedicated branch `fix/datasheet-corrections`
- 1 fix = 1 commit = 1 revert
- Verification after every fix (lint + typecheck + tests)
- If verification fails → auto-revert, skip to next
- LOW confidence = plan only, never auto-applied
- Never modifies DB schemas, secrets, or env files

## Zero Hallucination

**Core differentiator.** Every claim traces to a file and line number.

```
WRONG: "The system uses microservices architecture"
RIGHT: "Monolith — single entry point at api/index.php 
       (no service discovery or container orchestration detected)"

WRONG: "Approximately 50 endpoints"  
RIGHT: "47 endpoints (find api/ -name '*.php' | wc -l)"
```

When the skill can't determine something:

| Marker | Meaning |
|--------|---------|
| `[VERIFY]` | Found something, can't confirm purpose |
| `[NOT DETECTED]` | Looked for it, didn't find it |
| `[MANUAL]` | Requires human input |
| `[PARTIAL]` | Found evidence but incomplete |

## Install

### Option A — One-liner from GitHub (recommended)

**Project-level** (this project only):
```bash
mkdir -p .claude/skills/generate-datasheet && \
curl -sL -o .claude/skills/generate-datasheet/SKILL.md \
  https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/generate-datasheet/SKILL.md
```

**Global** (all your projects):
```bash
mkdir -p ~/.claude/skills/generate-datasheet && \
curl -sL -o ~/.claude/skills/generate-datasheet/SKILL.md \
  https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/generate-datasheet/SKILL.md
```

### Option B — Clone the repo

```bash
git clone https://github.com/thiago-a11y/claude-skill-generate-datasheet.git \
  .claude/skills/generate-datasheet
```

### Option C — Manual download

1. Download [SKILL.md](https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/generate-datasheet/SKILL.md)
2. Place in `.claude/skills/generate-datasheet/SKILL.md`

> **No restart needed.** Claude Code detects new skills automatically.

### Install individual skills

Each skill can be installed separately:

```bash
# generate-api-client — Postman collection + integration guides
mkdir -p .claude/skills/generate-api-client && \
curl -sL -o .claude/skills/generate-api-client/SKILL.md \
  https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/generate-api-client/SKILL.md

# generate-compliance — CAIQ/SIG/LGPD questionnaires from code
mkdir -p .claude/skills/generate-compliance && \
curl -sL -o .claude/skills/generate-compliance/SKILL.md \
  https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/generate-compliance/SKILL.md

# health-badges — SVG badges for README
mkdir -p .claude/skills/health-badges && \
curl -sL -o .claude/skills/health-badges/SKILL.md \
  https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/health-badges/SKILL.md
```

### Install all skills at once

```bash
for skill in generate-datasheet generate-api-client generate-compliance health-badges; do
  mkdir -p .claude/skills/$skill && \
  curl -sL -o .claude/skills/$skill/SKILL.md \
    https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/$skill/SKILL.md
done
```

## Skills Catalog

### generate-datasheet (v4.1)
The main skill — 6 layers from a single codebase scan. [Full documentation above](#what-it-generates).

```
/generate-datasheet
```

### generate-api-client (v1.0) `NEW`

Generates an API integration pack from your codebase:
- **Postman Collection** (JSON) — importable, with auth, body examples, environment variables
- **Integration Guides** — per-stack "connect in 5 minutes" (React, Python, PHP, Node.js)
- **Webhook Documentation** — event types, payloads, signature verification, receiver examples
- **Auth Setup Guide** — step-by-step authentication flow with code examples

```
/generate-api-client
```

### generate-compliance (v1.0) `NEW`

Pre-fills security questionnaires from code evidence:
- **CAIQ** (Consensus Assessments Initiative Questionnaire) — 260+ controls with file:line evidence
- **SIG Lite** (Standardized Information Gathering) — vendor risk assessment
- **LGPD/GDPR Data Mapping** — personal data inventory, data flows, data subject rights status
- **Evidence Manifest** (JSON) — machine-readable mapping of every control to code proof
- **Unsupported Claims** — what code CANNOT prove (organizational policies, physical security)

```
/generate-compliance
```

### health-badges (v1.0) `NEW`

Generates SVG badges for your README from real codebase metrics:
- Health Score (0-100), Test Coverage, Dependency Freshness, Bus Factor, Doc Coverage, Tech Debt, AI Cost Awareness
- shields.io visual style, color-coded (green/yellow/red)
- Static SVG files — no external service dependency
- Auto-insert into README

```
/health-badges
```

## Usage

Each skill works standalone. Use slash commands or natural language:

```
/generate-datasheet          — Full documentation + operations pack
/generate-api-client         — Postman + integration guides
/generate-compliance         — Security questionnaires from code
/health-badges               — SVG badges for README
```

Or in natural language:

```
Generate complete documentation for this project
Create a Postman collection for my API
Fill the CAIQ questionnaire from my code
Generate health badges for the README
What should I upgrade? Generate an evolution report
```

The skills will:
1. **Scan** your codebase (endpoints, tables, integrations, auth, configs)
2. **Present** findings for your confirmation (never generates without approval)
3. **Generate** selected outputs with evidence
4. **Report** what needs human input (`[MANUAL]` markers)

## How It Works (Anti-Hallucination)

```
Phase 0: Ask what docs are needed
Phase 1: Discovery — 11 scans (identity, structure, DB, endpoints, 
         auth, integrations, tests, CI/CD, code health, git, existing docs)
Phase 2: Present inventory — user confirms before generation
Phase 3: Branding decisions — AI naming, audience, language
Phase 4: Generate internal MD docs — every fact has source citation
Phase 5: Generate security pack — controls with status tags
Phase 5.5: Generate evolution report — tech radar, migrations, debt, gaps
Phase 6: Generate sales HTML — dark theme, persona filters, metrics
Phase 7: Generate technical HTML — architecture, API, SLA, gaps
Phase 8: Validation — cross-check, count markers, report
Phase 9: Correction engine — classify issues, propose fixes, approve, apply, verify
```

## Key Principles

1. **Evidence over inference** — can't point to file:line? don't write it
2. **Uncertainty is honest** — `[NOT DETECTED]` beats a guess
3. **Humans provide context** — skill provides structure, humans verify
4. **Security by transparency** — document gaps, don't hide them
5. **No AI washing** — show what AI does, don't say "AI-powered"
6. **Docs-as-code** — markdown, versionable, diffable
7. **Built to cure vibe-coding** — code nobody can explain is a liability

## Best Practices Applied

Based on documentation from best-in-class B2B SaaS companies:

| Reference | What we learned |
|-----------|----------------|
| Salesforce | Trust docs: separate architecture/security/infrastructure |
| Rippling | Security datasheets: frameworks → plain language → crypto details |
| Databricks | "Designed for security teams to quickly review" |
| Stripe | Anticipate developer questions about security |
| 1Password | Walk through the model, don't just claim "encrypted" |
| FastAPI / Supabase / Cal.com | Well-documented open source standards |
| CAIQ / SIG | Questionnaire standards for mid-market SaaS |

## Works With Any Stack

The discovery phase adapts to your project:

| Stack | What it detects |
|-------|----------------|
| React / Vue / Angular | Components, routes, state management |
| PHP / Laravel | Endpoints, migrations, middleware |
| Node / Express | Routes, middleware, models |
| Python / Django / FastAPI | Views, models, serializers |
| Go | Handlers, models, middleware |
| Rust | Handlers, structs, configs |
| Any | Git history, configs, external APIs, TODOs |

## License

MIT — Use freely, modify as needed, no attribution required.

## Credits

Created by [Objetiva Solucao Empresarial](https://objetivasolucao.com.br) for the [SyneriumX](https://github.com/SineriumX/syneriumx) project.

Methodology based on research into B2B SaaS documentation best practices (Salesforce, Rippling, Databricks, Stripe, 1Password, Freshworks) and the vibe-coding documentation crisis (Addy Osmani/Google, Veracode 2025).
