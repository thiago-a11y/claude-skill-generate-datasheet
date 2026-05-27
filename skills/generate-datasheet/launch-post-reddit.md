# I built a Claude Code skill that turns any codebase into 30+ docs, health score, runbooks, and fixes your code with approval — all evidence-based, zero hallucination

I've been building a B2B SaaS CRM and realized my project had 770+ commits, 116 database migrations, 19 integrations... and almost zero documentation. Sound familiar?

So I built a Claude Code skill that scans a codebase and generates a **complete documentation + operations pack** — but with a strict rule: **every claim must trace to a file and line number.** If the skill can't prove it from the code, it marks it as `[VERIFY]` instead of guessing.

## What it generates (6 layers)

**Layer 1 — Internal docs (Markdown)**
Architecture, data dictionary, glossary, changelog, endpoints, security overview, roadmap, contributing guide, known bugs, backlog, pendencies. All extracted from actual code: migrations become data-dictionary tables, git log becomes changelog, grep results become endpoint maps.

**Layer 2 — Sales datasheet (HTML)**
Dark theme, persona filter chips (executives/IT/buyers/marketing), 3-layer progressive disclosure per module (title → features → technical accordion). One standalone HTML file, zero dependencies, print-friendly for PDF export.

**Layer 3 — Technical specification (HTML)**
"6 answers in 60 seconds" header for CTOs. Architecture diagrams, data residency, API reference, security controls matrix with status tags (Implemented / Partial / Not Available), SLA with RPO/RTO, and a brutally honest Known Gaps section.

**Layer 4 — Evolution report**
Tech radar (Adopt/Trial/Assess/Hold), dependency audit from `npm outdated`, migration recommendations ("migrate from X to Y because Z — 15 files affected, ~2 days effort"), security gaps, test coverage gaps, tech debt prioritized by location criticality.

**Layer 5 — Operational intelligence**
Role-based onboarding packs ("read these 12 files first, don't touch this module, here are 5 safe first PRs"), bus-factor report from git blame + churn + test coverage, incident runbooks generated from error handling patterns in code, and a project health score (0-100) with 8 explainable dimensions.

**Layer 6 — Assisted correction**
This is the one that surprised me. After scanning and documenting, the skill presents a correction plan:

```
Found 14 issues:

#1 [HIGH] 23 files with trailing whitespace
   Blast radius: cosmetic only
   [ ] Approve

#3 [MEDIUM] api/auth.php:45 — password compared with ==
   Fix: password_verify() | Blast radius: 1 file, auth flow
   [ ] Approve

#7 [LOW] express 4.x → 5.x (15 files, breaking changes)
   ⚠ Plan only — won't auto-fix, too risky

Approve which? (1,3 or "all-high" or "all")
```

Safety: dedicated branch (never main), 1 fix = 1 commit = 1 revert, post-fix verification (lint + typecheck + tests), auto-revert if verification fails. LOW confidence items are plan-only — never auto-applied.

**Plus: Security Pack**
Security whitepaper, data residency statement, subprocessors list, incident response capabilities, backup/DR policy. All with status tags and evidence.

## The anti-hallucination protocol

This is the core differentiator. The skill follows strict rules:

```
WRONG: "The system uses microservices architecture"
RIGHT: "Monolith — single entry point at api/index.php 
       (no service discovery or orchestration detected)"

WRONG: "Approximately 50 endpoints"
RIGHT: "47 endpoints (find api/ -name '*.php' | wc -l)"
```

When it can't determine something: `[VERIFY]` (needs confirmation), `[NOT DETECTED]` (looked, didn't find), `[MANUAL]` (requires human input). It also presents a full inventory of what it found and asks for confirmation before generating anything.

## Why I built this

The vibe-coding era is creating thousands of projects that work but nobody can explain. 70% of AI-built projects ship with zero architecture docs. Most doc generators (Docusaurus, MkDocs, Sphinx) generate **sites**, not **content**. SonarQube and CodeClimate find issues but can't explain WHY or generate a fix plan with blast radius.

I wanted one command that answers: "How does this system really work, where is it fragile, who knows it, what will break if I change it, and what should I do next?"

## Install (one command)

```bash
mkdir -p .claude/skills/generate-datasheet && \
curl -sL -o .claude/skills/generate-datasheet/SKILL.md \
  https://raw.githubusercontent.com/thiago-a11y/claude-skill-generate-datasheet/main/skills/generate-datasheet/SKILL.md
```

Then in Claude Code:
```
/generate-datasheet
```

No restart needed. Works with any stack (React, PHP, Python, Go, Rust — adapts to what it finds).

## What's next

The skill is MIT licensed and free. I'm considering adding SDK/Postman generation, observability pack (dashboard + alert configs from code), and security questionnaire auto-fill (CAIQ/SIG) in future versions.

Would love feedback. What would make you actually use this on your project?

**Repo:** https://github.com/thiago-a11y/claude-skill-generate-datasheet
