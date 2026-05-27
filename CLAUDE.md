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
    SKILL.md          — v4.0: scan → document → diagnose → fix (6 layers)
  (future skills go here as new directories)
docs/
  research-perplexity-results.md  — 9 research queries that shaped every layer
  planning-layers-roadmap.md      — Detailed planning: layers, SaaS tiers, skill priorities
README.md             — GitHub landing page (install, usage, examples)
ROADMAP.md            — Vision: versions, SaaS, new skills
CLAUDE.md             — This file (repo context for Claude Code)
```

### Research foundation
The `docs/` directory contains the research and planning that justify every design
decision. 9 Perplexity research queries cover: AI branding, CTO expectations,
IT procurement, exemplary SaaS docs, vibe-coding crisis, tech debt tools gap,
"can't go back" features, scan→fix trust orchestration, and monetization.
These are the source of truth for the roadmap — read them before proposing new features.

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
| `generate-datasheet` | v4.0.0 | Scan → Document → Diagnose → Fix (6 layers) |

### Version history (generate-datasheet)
- v1.0 — 2 HTML files (sales datasheet + technical spec)
- v2.0 — + internal MD docs (12 files) + security pack (5 files)
- v2.1 — + Layer 4 evolution report (tech radar, dependency audit)
- v3.0 — + Layer 5 operational intelligence (onboarding, bus-factor, runbooks, health score)
- v4.0 — + Layer 6 assisted correction engine (scan → propose → approve → fix → verify)
