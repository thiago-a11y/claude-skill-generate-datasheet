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
codedocs/             — CodeDocs v2.1 (BSL, offline CLI)
  cli.py              — 223 LOC, argument parsing, orchestration
  scanner.py          — 787 LOC, 18 scan functions (grep/find/git)
  renderer.py         — 775 LOC, 10 functions, 4 HTML generators + Risk Score
  migration.py        — 1086 LOC, 9 functions, 30+ equivalences, 6 targets
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

### CodeDocs (v2.1)
CodeDocs is an offline Python CLI (BSL licensed) that scans codebases without AI or internet.
Tested on SyneriumX CRM (1071 files, 341 endpoints, 54 tables) through 4 Perplexity review cycles.
Key modules: scanner.py (18 functions), renderer.py (10 functions, Risk Score),
migration.py (9 functions, 30+ equivalences, 6 targets). Installed at /usr/local/bin/codedocs.

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
| `generate-datasheet` | v4.1.0 | Scan → Document → Diagnose → Fix (6 layers + AI cost audit) |
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

### Version history (CodeDocs)
- v1.0 — Offline CLI with scanner + renderer (scan report, sales, tech spec)
- v1.1 — + Migration Planner + C# MVC support + ERP integration plans
- v1.2 — + Target selector + technology equivalences + package mapping
- v1.3 — + Full equivalence tables (Java, PHP, Delphi, VB6, 20 packages)
- v1.3.1 — + Full PHP support (Laravel, Symfony, CodeIgniter, CakePHP, procedural)
- v1.4 — + Migration plan by default + neutral target comparison
- v2.0 — 3 surgical cuts: Risk Score, contextual copy, opinionated recommendations
- v2.1 — Polish: executive summary, risk narrative, unified messaging. Perplexity-approved.
