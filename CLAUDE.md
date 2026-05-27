## Project: claude-skill-generate-datasheet

This repo contains a single Claude Code skill (SKILL.md) that generates
documentation + operational intelligence + assisted corrections for any codebase.

### What this repo IS
- A Claude Code skill file (SKILL.md)
- A README with install instructions and documentation
- MIT licensed, open source

### What this repo is NOT
- Not a Node.js project — no package.json, no dependencies, no build step
- Not an app — it's a skill file that Claude Code loads and follows
- Not SyneriumX-specific — works with any stack (React, PHP, Python, Go, Rust)

### Rules for contributing
- SKILL.md is the entire product — every instruction the AI follows lives there
- README.md is the GitHub landing page — install instructions, examples, badges
- Do NOT add dependencies, build tools, or frameworks — the skill is one file
- Do NOT add code that runs — the skill instructs Claude Code what to do
- Keep language in English (README has a PT-BR section for Brazilian users)
- Version follows semver in the SKILL.md frontmatter `version:` field
- Every new layer or major feature = major version bump
- Every improvement to existing layer = minor version bump
- Every fix = patch version bump

### Anti-hallucination is non-negotiable
The skill's core value is evidence-based documentation. When editing SKILL.md:
- Every scan command must be a real, runnable shell command
- Every template must include `<!-- source: {file}:{line} -->` comments
- Uncertainty markers ([VERIFY], [NOT DETECTED], [MANUAL]) must never be removed
- The correction engine (Layer 6) must never bypass the approval step
- Phase 2 (inventory presentation) must always happen before generation

### Current structure
```
SKILL.md    — The skill (all instructions for Claude Code)
README.md   — GitHub landing page (install, usage, examples)
CLAUDE.md   — This file (repo context for Claude Code)
```

### Version history
- v1.0 — 2 HTML files (sales datasheet + technical spec)
- v2.0 — + internal MD docs (12 files) + security pack (5 files)
- v2.1 — + Layer 4 evolution report (tech radar, dependency audit)
- v3.0 — + Layer 5 operational intelligence (onboarding, bus-factor, runbooks, health score)
- v4.0 — + Layer 6 assisted correction engine (scan → propose → approve → fix → verify)
