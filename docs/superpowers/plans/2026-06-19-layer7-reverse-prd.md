# Layer 7 — Reverse PRD: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Layer 7 (Reverse PRD) to the generate-datasheet skill — Phase 9 (9.1–9.8), a new section in "What this skill produces", Phase 0 menu option 10, updated frontmatter, and CLAUDE.md sync.

**Architecture:** Single-file edit — all changes go into `skills/generate-datasheet/SKILL.md` plus one update to `CLAUDE.md`. No new dependencies, no new files other than what the skill itself generates at runtime. The plan works entirely through markdown edits to the skill instruction file.

**Tech Stack:** Markdown (SKILL.md), Edit tool, Bash for verification.

## Global Constraints

- File to edit: `skills/generate-datasheet/SKILL.md` (currently 1381 lines, v4.1.0)
- New version: `5.0.0` (new layer = major bump per CLAUDE.md versioning rules)
- Anti-hallucination rules must be as strict as Layers 1-6 — no loosening
- Every new scan command must be a real, runnable shell command
- `[INFERRED]` and `[USER-PROVIDED]` are new markers — must be defined in the markers table
- ADRs are immutable by design — this must be explicit in the instructions
- Max 10 interview questions total — this constraint must be enforced in the skill text
- "Skip" answer from user must result in `[MANUAL]`, never block flow
- Gate 1 and Gate 2 must be explicit approval steps before advancing
- CLAUDE.md must stay in sync: skills catalog version + version history entry

---

### Task 1: Update frontmatter — version + description + trigger phrases

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md:1-34`

**What changes:**
- `version: 4.1.0` → `version: 5.0.0`
- Description block: "6 layers" → "7 layers", add Layer 7 line
- `Use when:` list: add new trigger phrases for PRD generation

- [ ] **Step 1: Edit frontmatter version and description**

In `skills/generate-datasheet/SKILL.md`, replace the frontmatter block (lines 1-34).

Old:
```
---
name: generate-datasheet
version: 4.1.0
description: |
  Turns any codebase into operational understanding + fixes it with your approval.
  Scans → Documents → Diagnoses → Proposes fixes → You approve → It corrects.
  Every claim traced to code. Zero hallucination. Zero unauthorized changes.
  
  6 layers:
  Layer 1 (Internal/MD): architecture, data-dictionary, glossary, changelog, 
    endpoints, security, roadmap, contributing, bugs-known, backlog, pendencies
  Layer 2 (External/HTML): Sales datasheet — persona filters, 3-layer depth
  Layer 3 (External/HTML): Technical specification — for CTOs/IT
  Layer 4 (Evolution/MD): Tech radar, dependency audit, migrations, gaps, AI API cost audit
  Layer 5 (Operational/MD): Onboarding packs, runbooks, bus-factor, health score
  Layer 6 (Correction): Scan → diagnose → propose → approve → fix → verify.
    Branch-based safety. Per-item approval. Confidence labels. Post-fix verification.
    Never touches main. Every fix = 1 commit = 1 revert.
  
  Plus: Security Pack (whitepaper, data-residency, subprocessors, 
    incident-response, backup-dr-policy)
  
  Use when: "generate docs", "document this project", "fix issues", "scan and fix",
  "onboarding guide", "runbook", "bus factor", "project health", "tech debt",
  "evolution report", "security docs", "ficha técnica", "corrigir problemas",
  "AI cost", "LLM audit", "model optimization", "custo de IA".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Agent
  - AskUserQuestion
---
```

New:
```
---
name: generate-datasheet
version: 5.0.0
description: |
  Turns any codebase into operational understanding + fixes it with your approval.
  Scans → Documents → Diagnoses → Proposes fixes → You approve → It corrects.
  Every claim traced to code. Zero hallucination. Zero unauthorized changes.
  
  7 layers:
  Layer 1 (Internal/MD): architecture, data-dictionary, glossary, changelog, 
    endpoints, security, roadmap, contributing, bugs-known, backlog, pendencies
  Layer 2 (External/HTML): Sales datasheet — persona filters, 3-layer depth
  Layer 3 (External/HTML): Technical specification — for CTOs/IT
  Layer 4 (Evolution/MD): Tech radar, dependency audit, migrations, gaps, AI API cost audit
  Layer 5 (Operational/MD): Onboarding packs, runbooks, bus-factor, health score
  Layer 6 (Correction): Scan → diagnose → propose → approve → fix → verify.
    Branch-based safety. Per-item approval. Confidence labels. Post-fix verification.
    Never touches main. Every fix = 1 commit = 1 revert.
  Layer 7 (Reverse PRD): Reconstruct product requirements from existing codebase.
    As-Is → approval gate → adaptive interview → To-Be → approval gate → PRD + ADRs.
    Evidence-based. Two approval gates. Max 10 questions. Zero hallucination.
  
  Plus: Security Pack (whitepaper, data-residency, subprocessors, 
    incident-response, backup-dr-policy)
  
  Use when: "generate docs", "document this project", "fix issues", "scan and fix",
  "onboarding guide", "runbook", "bus factor", "project health", "tech debt",
  "evolution report", "security docs", "ficha técnica", "corrigir problemas",
  "AI cost", "LLM audit", "model optimization", "custo de IA",
  "generate PRD", "reverse PRD", "reconstruct requirements", "gerar PRD",
  "requisitos do produto", "o que esse projeto faz", "PRD do projeto".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Agent
  - AskUserQuestion
---
```

- [ ] **Step 2: Verify the edit**

```bash
head -40 skills/generate-datasheet/SKILL.md
```

Expected: version shows `5.0.0`, description shows "7 layers", trigger phrases include "gerar PRD".

- [ ] **Step 3: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): bump to v5.0.0, add Layer 7 trigger phrases to frontmatter"
```

---

### Task 2: Add Layer 7 to "What this skill produces"

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — section after Layer 6, before Security Pack

**What changes:**
- Update title line "Six layers from a single codebase scan" → "Seven layers..."
- Add Layer 7 subsection block

- [ ] **Step 1: Update section title**

Replace:
```
Six layers from a single codebase scan — from documentation to correction:
```

With:
```
Seven layers from a single codebase scan — from documentation to correction:
```

- [ ] **Step 2: Add Layer 7 subsection**

Find the block that starts `### Security Pack (Markdown)` and insert the following **before** it:

```markdown
### Layer 7 — Reverse PRD (Markdown + ADR files)

For founders, PMs, tech leads, and anyone inheriting an undocumented project.

| File | Content |
|------|---------|
| `docs/prd.md` | Reverse PRD — problem, personas, As-Is capabilities, To-Be vision, ADR summary |
| `docs/decisions/ADR-001-*.md` | Architecture Decision Records — one per significant architectural decision (max 5-7) |

Two-gate flow: As-Is auto-generated → approval gate → adaptive interview (max 10 questions) → To-Be draft → approval gate → PRD + ADRs generated.

Every claim is traced to code evidence, git history, or explicit user input. Markers distinguish:
- Code-proven facts (no marker)
- `[INFERRED]` — reconstructed from code patterns
- `[USER-PROVIDED]` — came from the interview
- `[MANUAL]` — requires human input, cannot be extracted from code

```

- [ ] **Step 3: Verify**

```bash
grep -n "Layer 7\|Seven layers\|Reverse PRD\|docs/prd.md" skills/generate-datasheet/SKILL.md | head -20
```

Expected: Layer 7 appears in "What this skill produces" section and frontmatter description.

- [ ] **Step 4: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): add Layer 7 to 'What this skill produces' section"
```

---

### Task 3: Update Phase 0 menu

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — Phase 0 section

**What changes:**
- Option 1 updated to mention Layer 7
- Add option 10 for Reverse PRD

- [ ] **Step 1: Edit Phase 0 menu**

Find the Phase 0 `Ask the user what they need:` block and replace it:

Old:
```
What do you need?

1. Full pack (all 6 layers + security pack) — recommended for first run
2. Document only (Layers 1-5: all docs, no corrections)
3. Internal only (Layer 1: MD files for the dev team)
4. External only (Layer 2+3: sales + technical HTML)
5. Evolution report (Layer 4: tech debt, migrations, dependency audit)
6. Operational pack (Layer 5: onboarding, bus-factor, runbooks, health score)
7. Scan & fix only (Layer 6: diagnose + propose + fix with approval)
8. Security pack only
9. Specific files (I'll tell you which)
```

New:
```
What do you need?

1. Full pack (all 7 layers + security pack) — recommended for first run
2. Document only (Layers 1-5: all docs, no corrections)
3. Internal only (Layer 1: MD files for the dev team)
4. External only (Layer 2+3: sales + technical HTML)
5. Evolution report (Layer 4: tech debt, migrations, dependency audit)
6. Operational pack (Layer 5: onboarding, bus-factor, runbooks, health score)
7. Scan & fix only (Layer 6: diagnose + propose + fix with approval)
8. Security pack only
9. Specific files (I'll tell you which)
10. Reverse PRD (Layer 7: reconstruct product requirements from existing codebase)
    → docs/prd.md + docs/decisions/ADR-*.md
```

- [ ] **Step 2: Verify**

```bash
grep -n "option 10\|Reverse PRD\|all 7 layers" skills/generate-datasheet/SKILL.md | head -10
```

Expected: "all 7 layers" in option 1, "Reverse PRD" in option 10.

- [ ] **Step 3: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): add option 10 (Reverse PRD) to Phase 0 menu"
```

---

### Task 4: Renumber Correction Engine to Phase 10, then add Phase 9.1–9.2

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — Correction Engine section + new Phase 9 block

**Why:** The existing Correction Engine is currently labeled "Phase 9" with sub-phases 9.1–9.7. The Reverse PRD also needs Phase 9 (9.1–9.8). To avoid collision, rename the Correction Engine to Phase 10 first.

- [ ] **Step 1: Rename Correction Engine section header**

Replace:
```
### Phase 9 — Correction Engine (Layer 6)
```
With:
```
### Phase 10 — Correction Engine (Layer 6)
```

- [ ] **Step 2: Rename Correction Engine internal sub-phases 9.x → 10.x**

Run these replacements inside the Correction Engine section only (the section that starts with "Only runs if user selected Layer 6"):

```
**9.1 — Compile issue list from previous phases**  →  **10.1 — Compile issue list from previous phases**
**9.2 — Classify each issue**                      →  **10.2 — Classify each issue**
**9.3 — Present correction plan**                  →  **10.3 — Present correction plan**
**9.4 — Create safety branch**                     →  **10.4 — Create safety branch**
**9.5 — Apply approved fixes**                     →  **10.5 — Apply approved fixes**
**9.6 — Post-fix actions**                         →  **10.6 — Post-fix actions**
**9.7 — Rules the correction engine MUST follow**  →  **10.7 — Rules the correction engine MUST follow**
```

Also update any references to "Phase 9.x" within that section to "Phase 10.x".

- [ ] **Step 3: Verify rename**

```bash
grep -n "Phase 9\|Phase 10" skills/generate-datasheet/SKILL.md | head -20
```

Expected: "Phase 10 — Correction Engine" appears, "Phase 9 — Correction Engine" does NOT appear. "Phase 9 — Reverse PRD" does NOT appear yet (we add it next).

- [ ] **Step 4: Insert Phase 9.1–9.2 before the Phase 10 block**

Find this exact line (now renamed):
```
### Phase 10 — Correction Engine (Layer 6)
```

Insert the following block **directly before** that line:

```markdown
### Phase 9 — Reverse PRD (Layer 7)

Only runs if user selected Layer 7 (option 10 in Phase 0) or "Full pack" (option 1).

Reuses all data from Phase 1 — no re-scan needed. If Phase 1 has not run yet, run it first.

#### 9.1 — Build As-Is

Consolidate Phase 1 evidence into structured As-Is sections.

**Persona reconstruction:**
```bash
# Roles and permission levels
grep -rn "role\|permission\|admin\|manager\|operator\|viewer\|owner" \
  --include="*.ts" --include="*.php" --include="*.py" --include="*.go" 2>/dev/null | head -20

# UI labels that reveal audience
grep -rn "admin\|dashboard\|portal\|backoffice\|customer\|client\|partner" \
  --include="*.tsx" --include="*.jsx" --include="*.html" --include="*.blade.php" 2>/dev/null | head -20

# Enum values for roles
grep -rn "enum.*[Rr]ole\|ROLE_\|UserType\|AccountType" \
  --include="*.ts" --include="*.php" --include="*.py" 2>/dev/null | head -15
```

**User journey reconstruction:**
- For each detected route group: identify entry point → core action → output
- Pattern: `GET /login` → `POST /login` → redirect to dashboard = auth journey
- Pattern: `GET /api/v1/resource` → `POST` → `PUT` → `DELETE` = CRUD journey
- Group journeys by persona (admin journeys vs end-user journeys)

**Implicit constraint detection:**
```bash
# Hosting/deployment constraints
ls Dockerfile docker-compose.yml fly.toml vercel.json netlify.toml railway.json 2>/dev/null

# Scale/performance constraints
grep -rn "max_connections\|pool_size\|MAX_FILE\|rate_limit\|timeout\|memory_limit" \
  --include="*.ts" --include="*.php" --include="*.py" --include="*.env*" 2>/dev/null | head -10

# Architecture pattern
ls src/services/ src/modules/ src/domain/ api/ app/ microservices/ 2>/dev/null
```

**Decision archaeology:**
```bash
# Git messages indicating architectural decisions
git log --all --oneline | grep -iE "chose|decided|instead of|replaced|migrated|switched to|moved to|refactor|rewrote" 2>/dev/null | head -20

# Code comments with explicit intent
grep -rn "// Note:\|// Reason:\|// Because\|// workaround\|// intentionally\|# NOTE:\|# HACK:\|# DECISION:" \
  --include="*.ts" --include="*.php" --include="*.py" --include="*.go" 2>/dev/null | head -30
```

For each significant decision candidate found, record:
- What was decided (framework, pattern, data structure, integration)
- Evidence (file:line or git hash)
- Confidence: DOCUMENTED (explicit comment/git) or [INFERRED] (pattern only)

#### 9.2 — Gate 1: Present As-Is + Approval

Present the As-Is summary to the user before asking any interview questions.

```
## As-Is Summary — {Project Name}
<!-- Layer 7 · Gate 1 · generate-datasheet v5 -->

### Personas detected
| Persona | Evidence | Confidence |
|---------|----------|------------|
| {role from enum/code} | {file:line} | HIGH / [INFERRED] |

### Core capabilities (from Phase 1 endpoints + components)
| Module | Capabilities | Evidence |
|--------|-------------|----------|

### User journeys reconstructed
**{Persona 1}:**
1. Entry: {route or action}
2. Core action: {what they do}
3. Output: {what they get}

**{Persona 2}:** (if detected)
...

### Architectural constraints
| Constraint | Value | Evidence |
|------------|-------|----------|
| Deployment | {Dockerfile / cPanel / Vercel / [NOT DETECTED]} | {file} |
| Auth pattern | {JWT / Sessions / OAuth / [NOT DETECTED]} | {file:line} |
| Database | {MySQL / Postgres / MongoDB / [NOT DETECTED]} | {file:line} |
| Scale model | {Single server / Containers / Serverless / [NOT DETECTED]} | {evidence} |

### ADR candidates (decisions found in code or git)
| Decision | Evidence | Confidence |
|----------|----------|------------|
| {e.g. JWT vs Sessions} | {auth.php:12} | [INFERRED] |

---
Isso reflete com precisão o que o sistema faz?
O que está errado ou faltando? (Digite correções ou "está correto")
```

Use `AskUserQuestion` with open-ended text input. Incorporate any corrections before Phase 9.3.

Only advance to Phase 9.3 after the user confirms.

```

- [ ] **Step 5: Verify Phase 9.1–9.2 inserted**

```bash
grep -n "9\.1\|9\.2\|Gate 1\|Build As-Is\|Decision archaeology\|Persona reconstruction" skills/generate-datasheet/SKILL.md | head -20
```

Expected: Phase 9.1 and 9.2 present with their headers. Phase 10 (Correction Engine) still present.

- [ ] **Step 6: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): rename Correction Engine Phase 9→10, add Phase 9.1-9.2 (Reverse PRD As-Is + Gate 1)"
```

---

### Task 5: Add Phase 9.3 — Adaptive Interview

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — inside Phase 9 block, after 9.2

- [ ] **Step 1: Insert Phase 9.3 after the 9.2 block**

Append the following after the Phase 9.2 block (inside the Phase 9 section):

```markdown
#### 9.3 — Adaptive Interview

Ask fixed questions first, then conditional questions based on Phase 1 findings.

**Rules (enforce strictly):**
- One question at a time — use `AskUserQuestion` for each
- Maximum 10 questions total: 4 fixed + up to 6 conditional (most relevant first)
- If a fixed question's answer already addresses a conditional question, skip that conditional
- Answer of "pular", "skip", or blank → record as `[MANUAL]` in the PRD, never block the flow
- Ask conditional questions in priority order (highest architectural impact first)

**Fixed questions (always ask, in this order):**

**Q1:** "Em uma frase: qual problema este produto resolve, para quem?"
→ Maps to §1 Problem & Context in prd.md

**Q2:** "Quem é o usuário principal? (cargo, contexto de uso, nível técnico)"
→ Maps to §2 Stakeholders & Personas

**Q3:** "O que foi conscientemente NÃO construído neste produto, e por quê?"
→ Maps to §3 Scope — Out of scope (intentional)

**Q4:** "Onde este produto deveria estar em 6 a 12 meses?"
→ Maps to §10 To-Be — Product Vision

**Conditional questions — check each trigger against Phase 1 data:**

| Priority | Trigger (from Phase 1) | Question to ask |
|----------|------------------------|-----------------|
| 1 | ERP detected: grep found SAP, TOTVS, Protheus, Oracle, Datasul | "Esta integração com ERP é bidirecional? Quem é o sistema de registro (master) para cada entidade de dados?" |
| 2 | >3 external APIs detected in Phase 1.6 | "Quais integrações são core para o produto funcionar vs nice-to-have? Se uma cair, o que quebra para o usuário final?" |
| 3 | Public API endpoints detected AND external consumers possible | "Esta API é consumida por terceiros, parceiros ou clientes? Existe contrato de versionamento ou SLA de API?" |
| 4 | Service layer OR microservices pattern detected (services/, modules/ with independent configs) | "Esses serviços são produtos independentes ou componentes auxiliares deste sistema?" |
| 5 | Both admin and end-user routes detected in same codebase | "Quem paga pelo produto? Quem usa no dia a dia? São a mesma pessoa ou papéis distintos?" |
| 6 | tenant_id, schema separation, or row-level security detected | "O produto é SaaS multi-tenant, multi-instância, ou implantado on-premise por cliente?" |
| 7 | test file count = 0 AND critical modules exist (auth, payment, data mutation) | "Qual a tolerância a downtime em produção? Existe SLA formal com clientes?" |
| 8 | TODO/FIXME count > 20 in critical paths (auth/, api/, payments/) | "Existe tech debt deixado intencionalmente? Qual o contexto e o plano para ele?" |
| 9 | git shortlog shows 1 contributor with > 80% of commits | "Existe um 'guardião' deste projeto? Quem deve herdar o conhecimento técnico?" |
| 10 | Undocumented modules with high churn (>10 changes in 90d, 0 doc files) | "Quais módulos têm regras de negócio críticas que não estão documentadas em lugar nenhum?" |
| 11 | Legacy stack: PHP 5/7, VB6, Delphi, .NET Framework < 4.8 | "Existe plano de modernização da stack? Qual o horizonte previsto?" |
| 12 | Heavy vendor dependency: all compute on one cloud, cPanel-only deploy | "O lock-in com este vendor é intencional (custo, suporte, contrato) ou acidental?" |
| 13 | Multiple auth roles with no RBAC documentation found | "Quais perfis de acesso existem? O modelo de permissão atual está correto ou é legado/acumulado?" |

Select the top 6 most relevant conditional questions given the specific codebase. Skip those whose triggers were not detected.

```

- [ ] **Step 2: Verify**

```bash
grep -n "9\.3\|Adaptive Interview\|Fixed questions\|Conditional questions\|Q1\|Q2\|Q3\|Q4" skills/generate-datasheet/SKILL.md | head -20
```

Expected: Phase 9.3 present with all 4 fixed questions and the conditional table.

- [ ] **Step 3: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): add Phase 9.3 (adaptive interview, 4 fixed + 13 conditional questions)"
```

---

### Task 6: Add Phases 9.4 and 9.5 — Build To-Be + Gate 2

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — inside Phase 9 block, after 9.3

- [ ] **Step 1: Insert Phases 9.4–9.5 after the 9.3 block**

```markdown
#### 9.4 — Build To-Be

Combine interview answers with existing backlog and roadmap evidence.

**Inputs:**
- Q4 answer (product vision — `[USER-PROVIDED]`)
- Q3 answer (intentional out of scope — `[USER-PROVIDED]`)
- `docs/backlog.md` if generated (Layer 1), or raw TODO/issue scan from Phase 1
- `docs/roadmap.md` if generated (Layer 1)
- Any features mentioned in interview answers

**Feature roadmap construction:**
1. Start with all items from backlog.md / TODO scan — these are `origin: backlog`
2. Add features mentioned in Q4 answer — these are `origin: [USER-PROVIDED]`
3. For each feature, generate 1-3 acceptance criteria:
   - Must be measurable ("User can X" or "System returns Y within Z")
   - Must NOT be vague ("Works correctly", "Is fast", "Is secure")
4. Assign initial priority: Critical / High / Medium / Low based on:
   - Critical = mentioned in Q4 + blocks core user journey
   - High = in backlog with FIXME/TODO markers in critical paths
   - Medium = in backlog, no critical path dependency
   - Low = nice-to-have, no evidence in code

**Acceptance criteria format:**
```
WRONG: "The feature works correctly"
RIGHT: "User can upload a file up to 10MB and receive a confirmation with file ID within 3 seconds"

WRONG: "Improve performance"
RIGHT: "API response time for /api/deals returns in < 500ms for payloads up to 100 records"
```

Mark all acceptance criteria derived from inference as `[VERIFY — confirm with stakeholders]`.

#### 9.5 — Gate 2: Present To-Be Draft + Approval

```
## To-Be Draft — {Project Name}
<!-- Layer 7 · Gate 2 · generate-datasheet v5 -->

### Product Vision [USER-PROVIDED]
"{Q4 answer verbatim}"

### Out of Scope (intentional) [USER-PROVIDED]
"{Q3 answer verbatim}"

### Feature Roadmap

| Feature | Origin | Priority | Acceptance Criteria |
|---------|--------|----------|---------------------|
| {feature} | backlog / [USER-PROVIDED] | Critical/High/Medium/Low | {measurable criteria} |

### To-Be: Integration Direction
| Integration | Direction | Master System | Status |
|-------------|-----------|---------------|--------|
| {ERP / API / Service} | {bidirectional / outbound / inbound} | {system} | Current / Planned [USER-PROVIDED] |

---
Isso captura a direção correta do produto?
O que deve mudar? (Digite correções ou "está correto")
```

Use `AskUserQuestion` with open-ended text input. Incorporate corrections.

Only advance to Phase 9.6 after user confirms.

```

- [ ] **Step 2: Verify**

```bash
grep -n "9\.4\|9\.5\|Build To-Be\|Gate 2\|Feature roadmap construction\|Acceptance criteria" skills/generate-datasheet/SKILL.md | head -15
```

Expected: 9.4 and 9.5 present with acceptance criteria format and Gate 2 template.

- [ ] **Step 3: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): add Phases 9.4 (Build To-Be) and 9.5 (Gate 2) for Layer 7"
```

---

### Task 7: Add Phases 9.6–9.8 — ADR Generation, PRD Generation, Report

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — inside Phase 9 block, after 9.5

- [ ] **Step 1: Insert Phases 9.6–9.8 after the 9.5 block**

```markdown
#### 9.6 — Generate ADR Files

Create one ADR file per significant architectural decision. Maximum 5-7 ADRs.

**Selection rules:**
1. Only generate an ADR if clear evidence exists: git message, code comment, or unambiguous code pattern
2. Rank candidates by architectural impact (database choice > framework > library > pattern)
3. Select top 5-7 — skip decisions with only weak [INFERRED] evidence
4. Create directory `docs/decisions/` if it does not exist

**Common ADR candidates to check (generate only if evidence found):**

| Decision Type | Evidence Signal |
|--------------|-----------------|
| Language / runtime choice | Main file extension dominance + package manager |
| Web framework | Framework import in entry point |
| Database engine | Driver import + connection string pattern |
| Auth strategy | JWT/session/OAuth library import |
| API style | REST routes vs GraphQL schema vs gRPC proto |
| Deployment model | Dockerfile vs cPanel vs serverless config |
| Sync vs async | Queue library absent/present |
| Multi-tenant vs single-tenant | Absence/presence of tenant_id |
| Monolith vs microservices | Single entry point vs multiple services |

**ADR file template** (save as `docs/decisions/ADR-{NNN}-{slug}.md`):

```markdown
# ADR-{NNN} — {Decision Title}
<!-- source: {file:line or git commit hash} -->
<!-- confidence: DOCUMENTED | [INFERRED] -->

**Status:** Accepted
**Date:** {date from git blame or git log -- {file} | head -1, or [NOT DETECTED]}

## Context

{What situation or need triggered this decision. Keep to 2-3 sentences.}
<!-- source: {evidence} -->

## Decision

{What was chosen. State it as a fact, not a recommendation.}
<!-- source: {file:line} -->

## Alternatives Considered

{If found in git messages or code comments. If not found: [NOT DOCUMENTED]}

## Consequences

{What this decision implies for the codebase — observable from code.}
<!-- source: {files affected, count} -->
```

**Anti-hallucination for ADRs:**
```
WRONG: "JWT was chosen for performance reasons"
RIGHT: "JWT detected (api/auth.php:12, jsonwebtoken in package.json:8).
        Sessions: [NOT DETECTED]. Reason for choice: [NOT DOCUMENTED].
        Confidence: [INFERRED]"
```

ADRs are immutable. Once written, never edit the content — only update `Status:` (e.g., "Superseded by ADR-005"). New decisions require new ADR files.

#### 9.7 — Generate docs/prd.md

Assemble the complete PRD from all approved data.

**File:** `docs/prd.md`

Generate using this exact structure:

```markdown
# PRD — {Project Name}
<!-- Generated by generate-datasheet v5 · Layer 7 · Reverse PRD -->
<!-- {date} · {N} commits analyzed · Confidence: {High/Medium/Low} -->
<!-- High = code evidence · [INFERRED] = pattern reconstruction · [USER-PROVIDED] = interview answers -->

## 0. Meta

| Field | Value |
|-------|-------|
| Generated | {date} |
| Codebase | {path} |
| Commits analyzed | {N} |
| Contributors | {N} |
| Overall confidence | {High / Medium / Low} |
| Confidence basis | {N} facts from code evidence, {N} [INFERRED], {N} [USER-PROVIDED], {N} [MANUAL] |

---

## 1. Problem & Context
<!-- [USER-PROVIDED] from interview Q1 + Q2 -->

**Problem solved:** {Q1 answer verbatim}
**Primary user:** {Q2 answer verbatim}
**Consciously NOT built:** {Q3 answer verbatim}

---

## 2. Stakeholders & Personas
<!-- source: auth roles, enums, UI labels — Phase 9.1 -->

| Persona | Role in system | Code evidence | Confirmed by user? |
|---------|---------------|---------------|-------------------|

---

## 3. Scope

### In scope — As-Is (what exists in the codebase)
<!-- source: endpoints.md, architecture.md — Phase 1 -->

### Out of scope — intentional
<!-- [USER-PROVIDED] from Q3 -->

### Out of scope — gap (planned but not built)
<!-- source: backlog.md, TODO scan — Phase 1 -->

---

## 4. As-Is — Current Capabilities
<!-- source: endpoints.md, component scan — Phase 1 -->

| Module | Capabilities | Evidence | Confidence |
|--------|-------------|----------|------------|

---

## 5. As-Is — Data Model
<!-- source: data-dictionary.md, migrations — Phase 1 -->

Key entities: {list with relationships}
Full detail: see `docs/data-dictionary.md`

---

## 6. As-Is — User Journeys
<!-- source: route scan, component tree — Phase 9.1 -->

**{Persona 1} journey:**
1. Entry: {route / screen}
2. Core action: {what they do}
3. Output: {what they get}

---

## 7. As-Is — Constraints & Assumptions
<!-- [INFERRED] from code patterns — Phase 9.1 -->

| Constraint | Current value | Evidence | Confidence |
|------------|--------------|----------|------------|

---

## 8. Decision History (ADR Summary)
<!-- source: docs/decisions/ADR-*.md — Phase 9.6 -->

| ADR | Decision | Status | Confidence |
|-----|---------|--------|------------|
| [ADR-001]({link}) | {title} | Accepted | DOCUMENTED / [INFERRED] |

---

## 9. Known Issues & Tech Debt
<!-- source: bugs-known.md, evolution-report.md — Layer 1 / Layer 4 -->

Top issues with product-level impact (not just code):

| # | Issue | Impact | Source | Priority |
|---|-------|--------|--------|----------|

---

## 10. To-Be — Product Vision
<!-- [USER-PROVIDED] from Q4 -->

"{Q4 answer verbatim}"

---

## 11. To-Be — Feature Roadmap
<!-- source: backlog.md + [USER-PROVIDED] — Phase 9.4 -->

| Feature | Origin | Priority | Acceptance Criteria |
|---------|--------|----------|---------------------|

---

## 12. Uncertainty Registry

All items requiring human review before this PRD can be considered complete:

| # | Item | Marker | Section | Action needed |
|---|------|--------|---------|---------------|
| 1 | {description} | [MANUAL] / [VERIFY] / [INFERRED] | §{N} | {what to do} |

**Total:** {N} [MANUAL] · {N} [VERIFY] · {N} [INFERRED] · {N} [USER-PROVIDED]
```

#### 9.8 — Final Report

After generating all files, present the completion summary:

```
## Reverse PRD Complete — {Project Name}

### Files generated
- docs/prd.md ({N} sections, {N} evidence citations)
- docs/decisions/ADR-001-*.md through ADR-{N}-*.md ({N} files)

### Confidence breakdown
| Type | Count | Meaning |
|------|-------|---------|
| Code evidence (no marker) | {N} facts | Verified from file:line |
| [INFERRED] | {N} items | Reconstructed from code patterns |
| [USER-PROVIDED] | {N} items | From interview answers |
| [MANUAL] | {N} items | Still need human input |
| [VERIFY] | {N} items | Need confirmation |

### Human input still needed
{list of [MANUAL] items with section references}

### What to do next
1. Fill in [MANUAL] items — these cannot be inferred from code
2. Review [INFERRED] items — confirm they match intent
3. Share prd.md with stakeholders for validation
4. Run Layer 6 (/scan & fix) to address issues found in §9 (Known Issues)
5. Commit docs/prd.md and docs/decisions/ to version control
```

**What Phase 9 NEVER does:**
- Never invents user personas without code evidence or user confirmation
- Never generates To-Be features not mentioned in backlog, TODOs, or interview answers
- Never writes ADRs without evidence (git message, code comment, or unambiguous pattern)
- Never advances past Gate 1 or Gate 2 without explicit user approval
- Never asks more than 10 questions total
- Never blocks the flow because user answered "pular" — records [MANUAL] and continues

```

- [ ] **Step 2: Verify**

```bash
grep -n "9\.6\|9\.7\|9\.8\|Generate ADR\|docs/prd.md\|Uncertainty Registry\|Final Report" skills/generate-datasheet/SKILL.md | head -20
```

Expected: all three subsections present, `docs/prd.md` template visible, Final Report template visible.

- [ ] **Step 3: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): add Phases 9.6 (ADR generation), 9.7 (PRD generation), 9.8 (report)"
```

---

### Task 8: Add new markers and update Anti-Hallucination + Key Principles sections

**Files:**
- Modify: `skills/generate-datasheet/SKILL.md` — Anti-Hallucination and Key Principles sections

- [ ] **Step 1: Add new markers to Anti-Hallucination section**

Find the markers table in the Anti-Hallucination Protocol section:

```markdown
| Marker | Meaning | Example |
|--------|---------|---------|
| `[VERIFY]` | Found something but can't confirm purpose | `[VERIFY] table 'logs' — purpose unclear` |
| `[NOT DETECTED]` | Looked for it, didn't find it | `2FA: [NOT DETECTED]` |
| `[MANUAL]` | Requires human input, can't extract from code | `Product description: [MANUAL — describe in 1-2 sentences]` |
| `[PARTIAL]` | Found evidence but incomplete | `Auth: JWT detected [PARTIAL — refresh token not found]` |
```

Replace with:

```markdown
| Marker | Meaning | Example |
|--------|---------|---------|
| `[VERIFY]` | Found something but can't confirm purpose | `[VERIFY] table 'logs' — purpose unclear` |
| `[NOT DETECTED]` | Looked for it, didn't find it | `2FA: [NOT DETECTED]` |
| `[MANUAL]` | Requires human input, can't extract from code | `Product description: [MANUAL — describe in 1-2 sentences]` |
| `[PARTIAL]` | Found evidence but incomplete | `Auth: JWT detected [PARTIAL — refresh token not found]` |
| `[INFERRED]` | Reconstructed from code patterns — not explicitly documented | `Auth strategy: JWT [INFERRED] — no explicit ADR found` |
| `[USER-PROVIDED]` | Came from interview answers — not from code evidence | `Vision: [USER-PROVIDED] — "expand to enterprise by Q4"` |
```

- [ ] **Step 2: Add Layer 7 to Key Principles**

Find the Key Principles section and add two new principles after principle 14:

```markdown
15. **PRD from code, not from imagination** — Layer 7 documents what exists and what users explicitly said; it never invents personas, features, or intent
16. **Two gates, no shortcuts** — As-Is gate before the interview, To-Be gate before generation; skipping either defeats the purpose
```

- [ ] **Step 3: Verify**

```bash
grep -n "\[INFERRED\]\|\[USER-PROVIDED\]\|PRD from code\|Two gates" skills/generate-datasheet/SKILL.md | head -10
```

Expected: new markers in the table, principles 15 and 16 present.

- [ ] **Step 4: Commit**

```bash
git add skills/generate-datasheet/SKILL.md
git commit -m "feat(skill): add [INFERRED] and [USER-PROVIDED] markers, principles 15-16"
```

---

### Task 9: Update CLAUDE.md — skills catalog + version history

**Files:**
- Modify: `CLAUDE.md`

**What changes:**
- Skills catalog: version 4.1.0 → 5.0.0, update purpose description
- Version history: add v5.0 entry

- [ ] **Step 1: Update skills catalog table**

Find:
```
| `generate-datasheet` | v4.1.0 | Scan → Document → Diagnose → Fix (6 layers + AI cost audit) |
```

Replace with:
```
| `generate-datasheet` | v5.0.0 | Scan → Document → Diagnose → Fix → PRD (7 layers + AI cost audit + Reverse PRD) |
```

- [ ] **Step 2: Add v5.0 to version history**

Find the version history section for generate-datasheet and add:

```
- v5.0 — + Layer 7 Reverse PRD (As-Is auto-generation → Gate 1 → adaptive interview → To-Be → Gate 2 → docs/prd.md + ADR files)
```

- [ ] **Step 3: Verify**

```bash
grep -n "v5\.0\|Layer 7\|Reverse PRD\|generate-datasheet" CLAUDE.md | head -10
```

Expected: v5.0.0 in the catalog, v5.0 entry in version history.

- [ ] **Step 4: Final full-file verification**

```bash
# Confirm version consistency between SKILL.md and CLAUDE.md
grep "version:" skills/generate-datasheet/SKILL.md | head -1
grep "generate-datasheet.*v5" CLAUDE.md | head -3

# Confirm Phase 9 is complete (all 8 subsections)
grep -n "#### 9\." skills/generate-datasheet/SKILL.md

# Confirm menu option 10 exists
grep -n "option 10\|10\. Reverse PRD" skills/generate-datasheet/SKILL.md

# Confirm both new markers in the table
grep -n "INFERRED\|USER-PROVIDED" skills/generate-datasheet/SKILL.md | wc -l
```

Expected: version 5.0.0 in both files, 8 Phase 9 subsections (9.1–9.8), option 10 in menu, [INFERRED] and [USER-PROVIDED] present in multiple places.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): sync skills catalog and version history for generate-datasheet v5.0.0"
```

---

## Summary

| Task | File | Change |
|------|------|--------|
| 1 | SKILL.md frontmatter | v5.0.0, 7 layers, PRD trigger phrases |
| 2 | SKILL.md "What this produces" | Layer 7 subsection |
| 3 | SKILL.md Phase 0 | Option 10 + "all 7 layers" |
| 4 | SKILL.md Phase 9.1–9.2 | Build As-Is + Gate 1 |
| 5 | SKILL.md Phase 9.3 | Adaptive interview (4 fixed + 13 conditional) |
| 6 | SKILL.md Phase 9.4–9.5 | Build To-Be + Gate 2 |
| 7 | SKILL.md Phase 9.6–9.8 | ADRs + PRD template + Report |
| 8 | SKILL.md markers + principles | [INFERRED], [USER-PROVIDED], principles 15-16 |
| 9 | CLAUDE.md | Skills catalog v5.0.0 + version history |

**Total commits:** 9 atomic commits, one per task.
**Files touched:** 2 (`skills/generate-datasheet/SKILL.md`, `CLAUDE.md`)
