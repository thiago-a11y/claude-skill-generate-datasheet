# Roadmap — Claude Skills Factory

> Based on 9 Perplexity research queries (see `docs/research-perplexity-results.md`)
> and detailed planning in `docs/planning-layers-roadmap.md`.

---

## generate-datasheet

### v4.1 — Current (Shipped)

Six layers from a single codebase scan:

| Layer | What | Output |
|-------|------|--------|
| 1 — Internal Docs | Architecture, data dictionary, endpoints, glossary, changelog, security, roadmap, contributing, bugs, backlog, pendencies | 12 MD files |
| 2 — Sales Datasheet | Dark theme HTML, persona filters, 3-layer depth, credibility metrics, honest limitations | 1 HTML file |
| 3 — Technical Spec | "6 answers in 60 seconds", architecture diagrams, security controls matrix, API reference, SLA, known gaps | 1 HTML file |
| 4 — Evolution Report | Tech radar, dependency audit, migrations, security gaps, test gaps, tech debt, architecture suggestions, **AI API cost audit** (callsite inventory, model mapping, downgrade recommendations) | 1 MD file |
| 5 — Operational Intelligence | Role-based onboarding (backend, frontend, SRE, product), bus-factor report, incident runbooks, health score 0-100 | 7+ MD files |
| 6 — Correction Engine | Scan → diagnose → propose → approve → fix → verify. Branch-based safety, per-item approval, confidence labels, 1 fix = 1 commit | Commits on branch |

Plus: Security Pack (whitepaper, data-residency, subprocessors, incident-response, backup-dr-policy).

Zero hallucination protocol: every claim traces to file:line. Uncertainty markers for anything unverifiable.

**Research that shaped v4.0:**
- Pesquisa 1: AI branding in SaaS — proprietary names over provider names (HubSpot "Breeze AI", Salesforce "Einstein")
- Pesquisa 2: CTO expectations for technical datasheets — "6 questions in <10 min"
- Pesquisa 3: IT procurement requirements — CAIQ/SIG, SOC2, DPA, architecture proof
- Pesquisa 4: Exemplary SaaS docs — Stripe, Rippling, Databricks, 1Password patterns
- Pesquisa 5: Vibe-coding documentation crisis — 70% ship with zero architecture docs
- Pesquisa 6: Tech debt tools gap — no tool combines doc + detection + correction
- Pesquisa 7: "Can't go back" features — onboarding packs, bus-factor, runbooks, health score
- Pesquisa 8: Scan → Fix with approval — trust orchestration gap in existing tools
- Pesquisa 9: Enrichment & monetization — layer stacking, SaaS model, distribution

---

### v5.0 — Shipped as Standalone Skills

All v5.0 features shipped as standalone skills (not layers in generate-datasheet):

#### Layer 7: SDK & Integration Pack — `SHIPPED as generate-api-client v1.0`
- Postman collection generated from detected endpoints
- Integration guide per stack (React, Python, PHP, Node)
- Webhook recipes with payload examples
- Auth setup guide (step-by-step authentication flow)

#### Compliance Questionnaire Engine — `SHIPPED as generate-compliance v1.0`
- CAIQ pre-filled with code evidence
- SIG / SIG-Lite pre-filled from security scan results
- Evidence manifest (JSON)
- "Unsupported claims" section

#### Live Health Badges — `SHIPPED as health-badges v1.0`
- Dynamic badges for README based on real health score
- shields.io compatible SVG

---

### v6.0 — Future: Observability, Demo & Training

#### Layer 8: Observability Pack
- Dashboard configs (Grafana JSON / Datadog YAML) generated from health endpoints
- Alert rules based on error patterns in code
- SLI/SLO suggestions for uptime/latency/error rate
- Each alert linked to its corresponding runbook
- Source: health endpoints + error handling + cron jobs + external calls

#### Demo & Walkthrough Pack
- Demo script discovered from routes and user flows
- CLI walkthrough script (commands to demonstrate features)
- Feature tour with screenshot placeholders
- Seeded data suggestions for demo environment
- Source: routes + UI components + fixtures/seeds

#### Training Pack
- Training material per role (slides outline)
- Voiceover scripts for training videos
- Support playbook (frequent questions mapped from code)
- Partner enablement guide
- Source: onboarding packs + docs + glossary + API reference

---

## CodeDocs Desktop — Shipped (v1.0.0)

First commercial product. Electron + React + Vite + TailwindCSS + Python sidecar.

| Feature | Status |
|---------|--------|
| Drag-and-drop folder scanning | Shipped |
| Tabbed results viewer (HTML + MD) | Shipped |
| PDF export | Shipped |
| Freemium licensing (Ed25519 signed keys) | Shipped |
| Auto-update (electron-updater) | Shipped |
| Windows installer (.exe) | Shipped |
| Mac installer (.dmg, ARM64) | Shipped |
| Code signing (Apple Developer ID + Windows Authenticode) | Planned |
| GitHub Releases for auto-update | Planned |

## CodeDocs CLI — v3.0 (Shipped)

| Feature | Status |
|---------|--------|
| Pure Python scanner (no grep/find/wc) | Shipped |
| i18n: PT-BR + EN-US (~200 keys, --lang flag) | Shipped |
| Decision Brief (5th HTML output) | Shipped |
| SAP ecosystem detection (B1/Fiori/CAP/HANA/ABAP) | Shipped |
| .codedocsignore (custom directory exclusion) | Shipped |
| 7 migration targets (+ SAP Fiori/UI5) | Shipped |
| Full docs pack (11 Markdown files, --full-docs) | Shipped |
| Executive Verdict + Audit Readiness + ROI | Shipped |
| Smart stack detection for target recommendations | Shipped |
| Endpoint criticality + ghost features | Shipped |
| Bus factor by module + deprecated functions | Shipped |

---

## SaaS — Business Model

### Free Tier (CLI/Skill + Desktop Free)
- Everything the skill does today (Layers 1-6 + Security Pack)
- Desktop Free: scan report + sales datasheet + tech spec
- Runs locally, zero dependencies
- MIT licensed (skills) / BSL licensed (CodeDocs)

### Pro Tier (Hosted)
- Upload repo or connect GitHub
- Web dashboard with scan history
- Architectural drift comparison between versions
- Professional PDF export of HTML outputs
- Hosted dynamic badges

### Team Tier
- Multiple repos
- Approval workflows for Layer 6 (corrections)
- Custom templates per company
- Compliance questionnaire library (CAIQ, SIG, VSA, HECVAT)

### Enterprise Tier
- Private templates and branding
- Evidence retention for audits
- CI/CD integration (GitHub Actions, GitLab CI)
- SSO/SAML for dashboard
- Guaranteed SLA
- Custom export formats

**Monetization research (Pesquisa 9):** OSS free for adoption → paid tiers for collaboration, hosting, compliance, governance, history. Precedents: GitLab, Sentry, PostHog, Elastic (OSS → company). Distribution: GitHub, blogs, social (no official Claude Code skill marketplace yet). Revenue: GitHub Sponsors, Open Collective, Polar.sh, paid tiers.

---

## New Skills — Pipeline

Skills being considered for the factory. Each is a standalone SKILL.md.

| Skill | Purpose | Priority | Target |
|-------|---------|----------|--------|
| `generate-datasheet` | The main skill — docs + ops + fix | Active | v4.1 shipped |
| `generate-api-client` | SDK + Postman + integration guides | High | v5.0 |
| `generate-compliance` | CAIQ/SIG/GDPR questionnaire answers from code evidence | High | v5.0 |
| `health-badges` | Dynamic README badges from health score | High | v5.0 |
| `generate-observability` | Dashboards + alerts + SLOs from code | Medium | v6.0 |
| `generate-demo` | Demo scripts + walkthroughs + seed data | Medium | v6.0 |
| `generate-training` | Training material per role | Low | v6.0 |

### Possible additions (from research, not yet planned)

| Skill | Purpose | Research source |
|-------|---------|----------------|
| `generate-threat-model` | STRIDE threat model from architecture + data flow | Pesquisa 3 (IT procurement) |
| `generate-adr` | Architecture Decision Records from git history | Pesquisa 7 ("can't go back") |
| `generate-migration-plan` | Step-by-step migration plan for major upgrades | Pesquisa 6 (tech debt tools gap) |
| `generate-cost-estimate` | Infrastructure cost estimate from detected services | Pesquisa 7 (cost-of-change) |
| `generate-pitch-deck` | Investor/stakeholder presentation from codebase metrics | Pesquisa 9 (go-to-market) |

---

## Design Principles (all skills)

1. **One file** — each skill is a single SKILL.md, no dependencies
2. **Zero hallucination** — every claim traces to code evidence
3. **Human in the loop** — skills propose, humans approve
4. **Stack agnostic** — works with any language/framework
5. **Uncertainty is honest** — `[NOT DETECTED]` beats a guess
6. **Incremental value** — each skill is useful alone, better together
7. **Docs-as-code** — output is markdown/HTML, versionable, diffable
