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

# Generate Datasheet v5 — Understand, Document, Fix, and Reconstruct

## What this skill produces

Seven layers from a single codebase scan — from documentation to correction:

### Layer 1 — Internal Documentation (Markdown)

For the development team, new contributors, and code maintainers.

| File | Content | Source |
|------|---------|--------|
| `docs/architecture.md` | System design, stack, modules, diagrams | package.json, configs, directory structure |
| `docs/backend-architecture.md` | API patterns, middleware, auth flow | Endpoint files, auth middleware, helpers |
| `docs/data-dictionary.md` | Tables, columns, types, relationships | Migrations, schema files, ORM models |
| `docs/endpoints.md` | All API routes, methods, auth level | Route files, controllers, endpoint scan |
| `docs/glossary.md` | Domain terms mapped to code entities | README, code comments, variable names |
| `docs/CHANGELOG.md` | Changes grouped by version/date | git log, PR history, migration files |
| `docs/security.md` | Auth, encryption, headers, audit, gaps | Auth middleware, configs, headers |
| `docs/roadmap.md` | Planned vs in-progress vs completed | TODOs, issues, PRD files, pendencies |
| `docs/contributing.md` | Setup, test, PR process, conventions | package.json scripts, CI configs, linters |
| `docs/bugs-known.md` | Known issues with workarounds | TODOs, FIXMEs, HACKs in code |
| `docs/backlog.md` | Features planned but not started | PRD files, issues, roadmap mentions |
| `docs/pendencies.md` | Blocked items and dependencies | Partial implementations, missing configs |

### Layer 2 — Sales Datasheet (HTML)

For executives, buyers, and marketing teams.

| Feature | Purpose |
|---------|---------|
| Persona filter chips | Dims irrelevant sections per audience |
| 3-layer depth per module | Title → Features → Technical accordion |
| Credibility metrics bar | Real numbers from codebase scan |
| Honest limitations section | What the product is NOT |
| Dark theme, responsive, print-friendly | Standalone, zero dependencies |

### Layer 3 — Technical Specification (HTML)

For CTOs, IT managers, and infosec teams.

| Feature | Purpose |
|---------|---------|
| "6 answers in 60 seconds" header | Quick qualification for IT |
| Architecture diagrams (ASCII) | Context + container views |
| Data residency table | Where data lives and moves |
| Security controls matrix | Status tags per control |
| API reference summary | Auth, rate limits, webhooks |
| SLA with RPO/RTO | Measurable commitments |
| Known gaps section | Brutally honest limitations |

### Layer 4 — Evolution Report (Markdown)

For tech leads, CTOs, and engineering managers. The document SonarQube/CodeClimate can't generate.

| Section | Content | Evidence Source |
|---------|---------|----------------|
| **Tech Radar** | Adopt / Trial / Assess / Hold for current stack | package.json versions vs latest, EOL dates |
| **Dependency Audit** | Outdated packages with upgrade impact | `npm outdated` / `composer outdated` / `pip list --outdated` |
| **Migration Recommendations** | "Migrate from X to Y because Z" with files affected | grep usage + external EOL/changelog knowledge |
| **Security Gaps** | Missing controls ranked by risk | Phase 1 security scan |
| **Test Coverage Gaps** | Source files with zero test files | Compare src/ vs test/ file mapping |
| **Performance Suggestions** | Bundle size, N+1 patterns, heavy imports | Build output, code pattern grep |
| **Tech Debt Prioritized** | TODOs/FIXMEs ranked by location criticality | grep + file path analysis (auth > UI) |
| **Architecture Evolution** | Structural improvements with effort estimate | Module coupling, file count per dir |
| **AI API Cost Audit** | LLM callsite inventory, model mapping, downgrade recommendations | grep SDK/HTTP patterns, model resolution, cost estimation |

**Anti-hallucination for recommendations:**
```
WRONG: "You should migrate to microservices"
RIGHT: "express@4.18.2 in package.json:12. Express 4.x EOL 2026.
        15 files use express.Router (grep evidence).
        Suggestion: evaluate Express 5.x or Fastify.
        Estimated effort: 15 files, ~2 days.
        [VERIFY] — confirm if v4 is kept intentionally."
```

Each recommendation MUST include:
1. What was found (with file:line)
2. Why it should change (EOL, security, performance — with source)
3. What files are affected (grep count)
4. Estimated effort (file count × complexity)
5. `[VERIFY]` marker if the recommendation might be wrong

### Layer 5 — Operational Intelligence (Markdown)

The "can't go back" layer. Answers: who knows this, what breaks if I change it, how do I onboard, what do I do when it fails?

#### 5a. Role-Based Onboarding Packs

| File | Audience | Content |
|------|----------|---------|
| `docs/onboarding-backend.md` | Backend developer | Critical API files, auth flow, DB patterns, first 5 safe PRs |
| `docs/onboarding-frontend.md` | Frontend developer | Component tree, routing, state management, design system |
| `docs/onboarding-sre.md` | SRE / DevOps | Deploy process, cron jobs, health checks, monitoring, backups |
| `docs/onboarding-product.md` | Product / Support | Module map, user flows, feature flags, config options |

Each onboarding pack includes:
- "Read these N files first" ranked by centrality and churn (git log evidence)
- Local setup: exact commands from package.json scripts, .env.example, migrations
- "Don't touch" zones: high-risk modules with low test coverage
- First 5 safe tasks: small, well-tested areas for first contribution
- Domain glossary: terms extracted from code specific to this role
- Key contacts: top contributors per module (from git blame)

**Evidence sources:**
```bash
# Most changed files (high churn = important to understand)
git log --since="90 days ago" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20

# Files by contributor concentration (bus factor per file)
git log --pretty=format:"%an" -- {file} | sort -u | wc -l

# Critical paths: auth, payment, data mutation
find . -path "*/auth/*" -o -path "*/payment/*" -o -path "*/middleware/*" | head -20

# Setup commands
cat package.json | grep -A20 '"scripts"'
cat Makefile 2>/dev/null | head -30
cat docker-compose.yml 2>/dev/null | head -20
```

#### 5b. Bus-Factor & Knowledge Silo Report

`docs/bus-factor-report.md` — identifies where knowledge is concentrated in one person.

| Column | Source | Meaning |
|--------|--------|---------|
| Module/Directory | Directory scan | Functional area |
| Dominant contributor | `git log --format="%an"` per dir | Who owns this |
| Contributor count | `git shortlog -sn -- {path}` | How many people know it |
| Change frequency | `git log --since="90d" -- {path}` | How often it changes |
| Test coverage | Test file count vs source file count | Safety net |
| Documentation | Doc file existence check | Is it documented? |
| Risk level | Composite of above | Critical / High / Medium / Low |

**Output format:**
```markdown
## Bus-Factor Report

### Critical Risk (single owner + high churn + low tests)
| Module | Owner | Contributors | Changes (90d) | Tests | Risk |
|--------|-------|-------------|---------------|-------|------|
| api/auth/ | dev-a | 1 | 23 | 0 | CRITICAL |
| api/payments/ | dev-b | 1 | 15 | 2 | CRITICAL |

### Action Items
1. "api/auth/ has 23 changes in 90 days by 1 contributor with 0 tests.
    Pair another developer on this module next sprint."
2. "api/payments/ handles financial transactions with no test coverage.
    Write integration tests before next release."
```

**Evidence commands:**
```bash
# Top contributors per directory
for dir in $(find . -maxdepth 2 -type d -not -path "*node_modules*" -not -path "*.git*"); do
  count=$(git log --format="%an" -- "$dir" 2>/dev/null | sort -u | wc -l | tr -d ' ')
  echo "$count $dir"
done | sort -n | head -20

# Files with single contributor
git log --format="%an" -- {file} | sort -u

# Churn per directory (last 90 days)
git log --since="90 days ago" --pretty=format: --name-only | grep "^{dir}" | wc -l
```

#### 5c. Incident Runbooks (from Code Paths)

Scan error handling, retry logic, health endpoints, and cron jobs to generate actionable runbooks.

**Detection sources:**
```bash
# Error handling patterns
grep -rn "catch\|except\|rescue\|on_error\|fallback\|retry\|circuit.breaker" --include="*.ts" --include="*.php" --include="*.py" | head -30

# Health endpoints
grep -rn "health\|ping\|status\|readiness\|liveness" --include="*.ts" --include="*.php" --include="*.py" | head -15

# Cron jobs and background workers
grep -rn "cron\|schedule\|worker\|queue\|consumer\|job" --include="*.ts" --include="*.php" --include="*.py" --include="*.yml" | head -20

# External service calls that can fail
grep -rn "curl_exec\|fetch\|axios\|requests\.\|http\.Get" --include="*.ts" --include="*.php" --include="*.py" | head -20

# Timeouts configured
grep -rn "timeout\|TIMEOUT\|time_limit\|deadline" --include="*.ts" --include="*.php" --include="*.py" | head -15
```

**Generated runbooks** (one per failure domain detected):

```markdown
# Runbook: Database Connection Failure
<!-- source: config.php:12, api/helpers/db.php:5-15 -->

## Symptoms
- HTTP 500 on all API endpoints
- Error log: "SQLSTATE[HY000] [2002] Connection refused" (from db.php:8)

## Likely Causes
1. MySQL service down on hosting
2. Max connections exceeded (shared hosting limit)
3. Credentials changed

## Diagnosis
1. Check error log: `tail -100 /path/to/error.log | grep -i "mysql\|pdo\|sql"`
2. Test connection: access health endpoint if available
3. Check hosting: cPanel → MySQL → process list

## Mitigation
- Restart MySQL via cPanel if possible
- Contact hosting support for connection limit issues
- Verify credentials in config.php:12

## Blast Radius
- All API endpoints depend on database (47 PHP files use PDO)
- Frontend shows loading/error states
- Cron jobs will fail silently

## Owner
- Primary: {top contributor to config.php and db.php from git blame}
```

Generate runbooks for each detected failure domain:
- Database failures (PDO/connection errors)
- External API failures (timeout, auth, rate limit)
- Queue/cron failures (stuck jobs, missed schedules)
- Auth failures (JWT expiry, token issues)
- File/storage failures (upload, disk space)
- Email delivery failures (bounce, throttle)

#### 5d. Project Health Score

`docs/health-score.md` — explainable composite score, not a vanity number.

**Dimensions (each scored 0-100 with evidence):**

| Dimension | How it's measured | Weight |
|-----------|------------------|--------|
| **Test Coverage** | Test files / source files ratio | 20% |
| **Dependency Health** | Outdated packages / total packages | 15% |
| **Documentation Coverage** | Documented modules / total modules | 15% |
| **Bus Factor** | Avg contributors per critical module | 15% |
| **Tech Debt** | TODOs+FIXMEs per 1000 lines of code | 10% |
| **Security Posture** | Controls implemented / controls expected | 10% |
| **Runbook Readiness** | Failure domains with runbooks / total domains | 10% |
| **Dependency Freshness** | Packages on latest major / total packages | 5% |

**Output:**
```markdown
# Project Health Score: 62/100

## Breakdown
| Dimension | Score | Evidence | Action |
|-----------|-------|----------|--------|
| Test Coverage | 25/100 | 12 test files / 203 source files (6%) | Add tests for auth/ and payments/ first |
| Dependency Health | 70/100 | 8 outdated / 45 total | Update 3 critical (see evolution-report) |
| Documentation | 80/100 | 10/12 modules documented | Document api/webhooks/ and api/cron/ |
| Bus Factor | 40/100 | 3 critical modules with single owner | Pair on auth/, payments/, email/ |
| Tech Debt | 55/100 | 47 TODOs in 15k LOC (3.1/KLOC) | Resolve 12 critical TODOs (see bugs-known) |
| Security | 75/100 | 9/12 controls implemented | Add rate limiting, SSO evaluation |
| Runbook Readiness | 50/100 | 3/6 failure domains covered | Generate runbooks for queue, email, auth |
| Dep Freshness | 85/100 | 38/45 on latest major | 7 packages need major upgrade |

## Top 3 Actions to Improve Score
1. Add tests for api/auth/ (+15 points) — 0 tests, 23 changes/90d, single owner
2. Pair developer on payments module (+10 points) — bus factor = 1
3. Update 3 critical dependencies (+5 points) — see evolution-report.md
```

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

### Security Pack (Markdown)

For compliance, infosec reviews, and procurement.

| File | Content | Source |
|------|---------|--------|
| `docs/security-whitepaper.md` | Complete security posture | Auth, encryption, headers, audit code |
| `docs/data-residency.md` | Where data is stored/processed/transferred | Configs, API calls, hosting info |
| `docs/subprocessors.md` | External services with data access | grep for external API URLs |
| `docs/incident-response.md` | Response plan template + current capabilities | Monitoring, logging, alerting code |
| `docs/backup-dr-policy.md` | Backup frequency, RPO, RTO, restore process | Cron jobs, backup configs, hosting |

### Layer 6 — Assisted Correction Engine

The skill doesn't just document problems — it fixes them with your explicit approval.

**How it works:**

```
SCAN ──→ DIAGNOSE ──→ PROPOSE ──→ APPROVE ──→ FIX ──→ VERIFY
  │          │            │           │          │         │
  │          │            │           │          │         └─ lint + typecheck + tests
  │          │            │           │          └─ 1 fix = 1 commit on branch
  │          │            │           └─ user picks which fixes to apply
  │          │            └─ diff preview + rationale + blast radius
  │          └─ categorize by severity + confidence
  └─ reuse Phase 1 discovery data
```

**Safety guarantees:**

| Guarantee | Implementation |
|-----------|---------------|
| Never touches main | Creates branch `fix/datasheet-corrections` |
| Per-item approval | User approves each fix individually or by category |
| Diff before apply | Shows exact changes with rationale before writing |
| Confidence labels | HIGH (lint/format) / MEDIUM (security fix) / LOW (multi-file refactor) |
| 1 fix = 1 commit | Every correction is a separate commit → individual revert possible |
| Post-fix verification | Runs available checks after each fix (lint, typecheck, test) |
| Blast radius shown | "This fix touches 3 files. 0 tests exist for them. Risk: MEDIUM" |
| Rollback plan | Every fix commit message includes revert instructions |

**Issue categories detected:**

| Category | Examples | Confidence | Auto-fixable? |
|----------|----------|------------|---------------|
| **Formatting & lint** | Missing semicolons, import order, trailing spaces | HIGH | Yes — deterministic |
| **Dependency updates** | Patch/minor bumps with no breaking changes | HIGH | Yes — update + verify |
| **Security (single-file)** | `==` instead of `===`, missing input validation, SQL injection risk | MEDIUM | Yes — with review |
| **Security (multi-file)** | Missing rate limiter, CORS misconfigured, headers absent | MEDIUM | Yes — creates files + wires them |
| **Missing tests** | Critical paths with 0 test files | MEDIUM | Yes — generates test skeletons |
| **Tech debt** | TODO/FIXME in critical paths, dead code, unused imports | MEDIUM | Partial — simple ones yes |
| **Dependency major** | Major version bumps with breaking changes | LOW | Proposes plan, doesn't auto-apply |
| **Architecture** | Module restructuring, pattern changes | LOW | Proposes plan only — never auto-applies |

**Presentation format (what the user sees):**

```
## Correction Plan — 14 issues found

### HIGH confidence (safe to auto-fix)
  
  #1 [LINT] 23 files with trailing whitespace
     Fix: remove trailing spaces
     Blast radius: cosmetic only, 0 logic changes
     [ ] Approve

  #2 [DEPENDENCY] lodash 4.17.20 → 4.17.21 (security patch)
     Fix: update package.json + lockfile
     Blast radius: 0 breaking changes, patch version
     [ ] Approve

### MEDIUM confidence (review recommended)

  #3 [SECURITY] api/auth.php:45 — password compared with == 
     Fix: change to password_verify($input, $hash)
     Blast radius: 1 file, 1 line, auth flow affected
     Rationale: == allows type juggling bypass
     [ ] Approve

  #4 [SECURITY] 3 API endpoints without rate limiting
     Fix: create middleware/rate-limiter.php + wire to 3 routes
     Blast radius: 1 new file + 3 modified files
     Files: api/auth.php, api/register.php, api/reset.php
     [ ] Approve

  #5 [MISSING-TEST] api/auth/ has 0 test files (23 changes in 90d)
     Fix: generate test skeleton with key assertions
     Blast radius: 1 new file, 0 existing files modified
     [ ] Approve

### LOW confidence (plan only, no auto-fix)

  #6 [ARCHITECTURE] api/ has 47 files in flat directory
     Suggestion: group by domain (api/crm/, api/marketing/, api/auth/)
     Estimated effort: 47 files, ~2 days
     ⚠ This is a suggestion, not an auto-fix. Requires human planning.

  #7 [DEPENDENCY-MAJOR] express 4.18.2 → 5.x (breaking changes)
     Suggestion: 15 files use express.Router, 3 breaking changes identified
     Estimated effort: 15 files, ~3 days + testing
     ⚠ Migration plan generated in evolution-report.md

─────────────────────────────────────
Approve which? (numbers, "all-high", "all-medium", "all", or "none")
```

**Execution flow after approval:**

```bash
# 1. Create safety branch
git checkout -b fix/datasheet-corrections

# 2. For each approved fix:
#    a. Apply the change (Edit tool)
#    b. Run verification:
npm run lint 2>/dev/null || true          # lint check
npx tsc --noEmit 2>/dev/null || true      # typecheck  
npm test 2>/dev/null || true              # tests
#    c. Commit with descriptive message:
git commit -m "fix(security): password_verify instead of == in auth.php

Applied by generate-datasheet skill (Layer 6).
Issue: #3 [SECURITY] password compared with == allows type juggling.
Confidence: MEDIUM
Revert: git revert {hash}"

# 3. After all fixes applied:
#    Report results
```

**Post-fix report:**

```
## Correction Results

### Applied (7/14)
| # | Category | File | Status | Verification |
|---|----------|------|--------|-------------|
| 1 | LINT | 23 files | ✓ Applied | lint: pass |
| 2 | DEPENDENCY | package.json | ✓ Applied | install: pass, tests: pass |
| 3 | SECURITY | api/auth.php | ✓ Applied | lint: pass |
| 4 | SECURITY | 3 files + 1 new | ✓ Applied | lint: pass |
| 5 | MISSING-TEST | tests/auth.test.php | ✓ Created | skeleton only |

### Skipped (5/14)
| # | Reason |
|---|--------|
| 6 | Architecture — plan only, user did not approve |
| 7 | Major dependency — plan only |

### Not approved (2/14)
| # | Category |
|---|----------|
| 8 | User declined |
| 9 | User declined |

### Branch
All changes on: `fix/datasheet-corrections`
Merge when ready: `git checkout main && git merge fix/datasheet-corrections`
Or revert all: `git branch -D fix/datasheet-corrections`

### Docs updated
- evolution-report.md — 7 items marked as resolved
- health-score.md — recalculated: 62 → 71 (+9 points)
- bugs-known.md — 3 items removed (fixed)
```

**What Layer 6 NEVER does:**

- Never commits to main — always uses a dedicated branch
- Never applies LOW confidence fixes automatically — only generates plans
- Never modifies database schemas or migrations
- Never changes environment variables or secrets
- Never deletes files without explicit approval
- Never installs new dependencies without showing what and why
- Never applies a fix if verification fails (lint/typecheck/test)
- Never applies a fix without showing the diff first
- Never combines multiple fixes in one commit — 1 fix = 1 commit

---

## Anti-Hallucination Protocol

**This is the core differentiator.** Every claim in generated docs must trace to a verifiable source.

### Rule 1: Only document what you can prove

```
WRONG: "The system uses microservices architecture"
RIGHT: "Monolith — single entry point at api/index.php (no service discovery or container orchestration detected)"

WRONG: "Approximately 50 endpoints"  
RIGHT: "47 endpoints (find api/ -name '*.php' | wc -l)"

WRONG: "The system has high availability"
RIGHT: "Single server — no HA configuration detected (no docker-compose, no k8s, no load balancer)"
```

### Rule 2: Uncertainty markers

When the skill cannot determine something with confidence, it MUST use markers:

| Marker | Meaning | Example |
|--------|---------|---------|
| `[VERIFY]` | Found something but can't confirm purpose | `[VERIFY] table 'logs' — purpose unclear` |
| `[NOT DETECTED]` | Looked for it, didn't find it | `2FA: [NOT DETECTED]` |
| `[MANUAL]` | Requires human input, can't extract from code | `Product description: [MANUAL — describe in 1-2 sentences]` |
| `[PARTIAL]` | Found evidence but incomplete | `Auth: JWT detected [PARTIAL — refresh token not found]` |
| `[INFERRED]` | Reconstructed from code patterns — not explicitly documented | `Auth strategy: JWT [INFERRED] — no explicit ADR found` |
| `[USER-PROVIDED]` | Came from interview answers — not from code evidence | `Vision: [USER-PROVIDED] — "expand to enterprise by Q4"` |

### Rule 3: Source attribution

Every section includes a comment with where the data came from:

```markdown
## Tech Stack
<!-- source: package.json:3-15, composer.json:5-12 -->

| Layer | Technology | Version | Evidence |
|-------|-----------|---------|----------|
| Frontend | React | 18.2.0 | package.json:8 |
| Backend | PHP | — | *.php files in api/ (47 files) |
| Database | MySQL | — | PDO usage in config.php:23 |
```

### Rule 4: Never generate content for these without human input

- Product description / value proposition
- Target audience / persona definitions  
- Pricing information
- SLA commitments (only document what's implemented)
- Roadmap priorities (only list TODOs found in code)
- Customer names or case studies
- Marketing claims of any kind

---

## Process

### Phase 0 — Pre-flight

Ask the user what they need:

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

### Phase 1 — Discovery (read-only, no output)

Run these exact commands to build a factual inventory. Adapt commands to the detected stack.

**1.1 — Project Identity**
```bash
cat README.md 2>/dev/null | head -20
cat package.json 2>/dev/null | head -30
cat composer.json 2>/dev/null | head -30
cat Cargo.toml 2>/dev/null | head -20
cat go.mod 2>/dev/null | head -10
cat requirements.txt 2>/dev/null | head -20
cat Gemfile 2>/dev/null | head -20
ls docker-compose* Dockerfile* 2>/dev/null
cat .env.example 2>/dev/null | head -30
```

**1.2 — Structure**
```bash
find . -type f -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.php" -o -name "*.py" -o -name "*.go" -o -name "*.rs" | wc -l
find . -type d -maxdepth 2 | head -40
ls src/ app/ api/ lib/ pages/ components/ routes/ controllers/ models/ 2>/dev/null
```

**1.3 — Database**
```bash
find . -name "migrate*" -o -name "*migration*" -o -name "schema*" -o -name "*.prisma" | head -20
grep -r "CREATE TABLE" --include="*.sql" --include="*.php" --include="*.py" --include="*.ts" 2>/dev/null | head -30
grep -r "Schema\.\|createTable\|model\s" --include="*.prisma" --include="*.ts" --include="*.py" 2>/dev/null | head -30
```

**1.4 — Endpoints / Routes**
```bash
grep -rn "router\.\|app\.\(get\|post\|put\|delete\|patch\)\|Route::\|@app\.\|@Get\|@Post" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -50
find . -path "*/api/*" -name "*.php" -o -name "*.py" -o -name "*.ts" | head -30
```

**1.5 — Authentication & Security**
```bash
grep -rl "jwt\|JWT\|jsonwebtoken\|passport\|bcrypt\|argon\|oauth\|OAuth\|SAML\|totp\|2fa\|mfa" --include="*.ts" --include="*.js" --include="*.php" --include="*.py" 2>/dev/null | head -15
grep -r "helmet\|cors\|csrf\|rate.limit\|X-Frame\|Content-Security-Policy\|HSTS" --include="*.ts" --include="*.js" --include="*.php" --include="*.py" 2>/dev/null | head -15
```

**1.6 — External Integrations**
```bash
grep -rn "https://.*api\|https://.*oauth\|amazonaws\|googleapis\|graph.facebook\|api.openai\|api.anthropic\|stripe\|twilio\|sendgrid\|mailgun" --include="*.ts" --include="*.js" --include="*.php" --include="*.py" --include="*.env*" 2>/dev/null | head -30
```

**1.7 — Tests**
```bash
find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*" -o -name "*_test.*" | wc -l
cat package.json 2>/dev/null | grep -A5 '"scripts"' | grep -i "test"
```

**1.8 — CI/CD & Deploy**
```bash
ls .github/workflows/ 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | head -30
ls Dockerfile* docker-compose* vercel.json netlify.toml fly.toml railway.json 2>/dev/null
```

**1.9 — Code Health**
```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND" --include="*.ts" --include="*.js" --include="*.php" --include="*.py" 2>/dev/null | wc -l
grep -rn "TODO\|FIXME\|HACK" --include="*.ts" --include="*.js" --include="*.php" --include="*.py" 2>/dev/null | head -20
```

**1.10 — Git History**
```bash
git log --oneline | wc -l
git log --oneline -10
git log --format="%an" | sort -u
git log --since="30 days ago" --oneline | wc -l
```

**1.11 — Existing Documentation**
```bash
find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | head -30
find ./docs -type f 2>/dev/null | head -20
```

**1.12 — Ownership & Bus Factor (for Layer 5)**
```bash
# Top contributors
git shortlog -sn --no-merges | head -10

# Contributor count per top-level directory
for dir in $(find . -maxdepth 1 -type d -not -name ".*" -not -name "node_modules"); do
  contributors=$(git log --format="%an" -- "$dir" 2>/dev/null | sort -u | wc -l | tr -d ' ')
  changes=$(git log --since="90 days ago" --oneline -- "$dir" 2>/dev/null | wc -l | tr -d ' ')
  echo "$contributors contributors, $changes changes (90d): $dir"
done

# Most changed files (churn = importance)
git log --since="90 days ago" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20
```

**1.13 — Error Handling & Failure Domains (for Runbooks)**
```bash
# Try/catch patterns
grep -rn "try\s*{\\|catch\s*(\|except\s\|rescue\s" --include="*.ts" --include="*.php" --include="*.py" 2>/dev/null | wc -l

# Retry/fallback patterns
grep -rn "retry\|fallback\|circuit.breaker\|backoff" --include="*.ts" --include="*.php" --include="*.py" 2>/dev/null | head -10

# Health endpoints
grep -rn "health\|ping\|status\|readiness" --include="*.ts" --include="*.php" --include="*.py" 2>/dev/null | head -10

# External service calls that can fail
grep -rn "curl_exec\|fetch(\|axios\.\|requests\.\|http\.Get" --include="*.ts" --include="*.php" --include="*.py" 2>/dev/null | wc -l
```

**1.14 — AI API Detection (for Cost Audit)**
```bash
# LLM SDK imports
grep -rn "openai\|anthropic\|google.generativeai\|google.cloud.aiplatform\|cohere\|mistralai\|groq\|together\|replicate" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.go" --include="*.rs" 2>/dev/null | head -30

# Model names hardcoded or configured
grep -rn "gpt-4o\|gpt-4\|gpt-3.5\|gpt-4o-mini\|o1-mini\|o1-preview\|o3-mini\|claude-3\|claude-opus\|claude-sonnet\|claude-haiku\|gemini-pro\|gemini-flash\|gemini-2\|command-r\|mistral-large\|mistral-small\|llama\|mixtral\|deepseek" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.env*" --include="*.yml" --include="*.yaml" --include="*.json" 2>/dev/null | grep -v "node_modules\|vendor\|\.lock" | head -40

# API endpoint calls to LLM providers
grep -rn "api.openai.com\|api.anthropic.com\|generativelanguage.googleapis.com\|api.cohere.ai\|api.mistral.ai\|api.groq.com\|api.together.xyz" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -20

# SDK method calls (chat completions, messages, generate)
grep -rn "chat\.completions\.create\|messages\.create\|generate_content\|responses\.create\|chat\.create\|completions\.create" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -20

# Wrapper/abstraction patterns
grep -rn "llm\.\|LLM\.\|runPrompt\|askModel\|callAI\|aiClient\|model_call\|invoke_model\|generate_response" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -20

# Model selection config (env vars, config files)
grep -rn "MODEL\|_MODEL\|model_name\|modelName\|model_id\|modelId" --include="*.env*" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.toml" 2>/dev/null | grep -v "node_modules\|vendor\|\.lock" | head -20

# Gateway/router patterns (LiteLLM, Portkey, OpenRouter)
grep -rn "litellm\|portkey\|openrouter\|ai-gateway\|model.*router\|model.*cascade\|model.*fallback" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.yml" 2>/dev/null | head -15

# Cost/token tracking already in place
grep -rn "token.*count\|token.*usage\|usage\.\|cost.*track\|billing\|metering\|rate.*limit.*ai\|budget" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15
```

### Phase 2 — Inventory Presentation

Present ALL findings to the user in a structured table. Ask for confirmation BEFORE generating anything.

```
## Discovery Results

### Project
- Name: [from package.json or README]
- Stack: [detected]
- Source files: [count]
- Commits: [count] total, [count] last 30 days
- Contributors: [count]

### Database
- Tables: [count] detected
- Migrations: [count] files

### API
- Endpoints: [count] detected
- Auth method: [detected]
- Rate limiting: [detected / NOT DETECTED]

### Security
- Password hashing: [method / NOT DETECTED]
- 2FA/MFA: [detected / NOT DETECTED]
- CORS: [detected / NOT DETECTED]
- Security headers: [list / NOT DETECTED]
- Audit logging: [detected / NOT DETECTED]

### External Integrations
- [list of services found with evidence]

### Tests
- Test files: [count]
- CI pipeline: [detected / NOT DETECTED]

### Code Health
- TODOs/FIXMEs: [count]

### Existing Documentation
- [list of .md files found]

### AI API Usage
- LLM providers detected: [list with file evidence]
- Models used: [list with file:line]
- Callsites: [count] detected
- Cost tracking: [detected / NOT DETECTED]
- Gateway/router: [detected / NOT DETECTED]

Is this accurate? Anything to add or correct?
```

### Phase 3 — Branding Decision

Ask:

```
1. Product name and company name?
2. Target audience?
3. AI branding: proprietary name or list providers?
4. Integrations to hide from sales materials?
5. Language? (pt-BR / en / es)
6. Which layers? (internal MD / sales HTML / technical HTML / evolution / operational / security)
```

### Phase 4 — Generate Internal Documentation (Markdown)

Generate each file. EVERY fact must come from Phase 1 discovery.

**Template for each doc:**
```markdown
# {Title} — {Project Name}
<!-- Generated by generate-datasheet v2. Evidence-based — sources cited per section. -->
<!-- [MANUAL] markers require human input. [VERIFY] markers need confirmation. -->

## Section
<!-- source: {file}:{line} -->
| Column | Data | Evidence |
|--------|------|----------|
```

For each file:
- architecture.md — system diagram, stack table, module inventory
- backend-architecture.md — API patterns, middleware chain, auth flow
- data-dictionary.md — every table with columns from actual migrations
- endpoints.md — every route with method, auth level, source file
- glossary.md — terms extracted from code, tables, enums
- CHANGELOG.md — entries from git log (quote directly, don't summarize)
- security.md — controls matrix with status tags
- roadmap.md — from TODOs, issues, PRDs found
- contributing.md — from package.json scripts, CI config, linter config
- bugs-known.md — from FIXME/HACK/TODO grep results
- backlog.md — from PRD files and issue references
- pendencies.md — blocked items, missing configs, partial implementations

### Phase 5 — Generate Security Pack

#### security-whitepaper.md
- Authentication model (evidence from auth files)
- Authorization / RBAC (evidence from middleware)
- Encryption (transit + rest — what's configured)
- Audit logging (events captured, retention, immutability)
- Vulnerability management (dependencies, update policy)
- Status table: Implemented / Partial / Not Available per control

#### data-residency.md
- Database location (from config/hosting)
- Backup location
- Data that leaves the country and why
- Subprocessor regions
- Legal basis for transfers (if LGPD/GDPR)

#### subprocessors.md
EXCLUSIVELY from grep results — only services with confirmed API calls:
| Subprocessor | Purpose | Data Accessed | Region | Evidence File |

#### incident-response.md
- Monitoring capabilities (from code)
- Alerting (email, webhook, or [NOT DETECTED])
- Backup/restore capability
- Communication channels
- Mark everything missing

#### backup-dr-policy.md
- Mechanism (from cron/configs)
- Frequency (evidence)
- RPO/RTO (calculated)
- Restore testing ([NOT DETECTED] if no evidence)
- Failover ([NOT DETECTED] if none)

### Phase 5.5 — Generate Evolution Report (Markdown)

Create `docs/evolution-report.md`. This is what makes the skill unique — no other tool generates this.

#### 5.5.1 — Dependency Audit
```bash
# Detect outdated packages (adapt to stack)
npm outdated --json 2>/dev/null || true
composer outdated --direct 2>/dev/null || true
pip list --outdated --format=json 2>/dev/null || true
cargo outdated 2>/dev/null || true
```

For each outdated dependency:
- Current version vs latest version (from command output)
- Files that import/use it: `grep -rl "{package}" --include="*.ts" --include="*.js" | wc -l`
- Breaking changes: note major version bumps (1.x → 2.x)
- Mark as `[VERIFY]` if pinned intentionally (lockfile or exact version in config)

#### 5.5.2 — Tech Radar (Adopt / Trial / Assess / Hold)

Categorize every technology detected in Phase 1:

```markdown
## Tech Radar — {Project Name}

### Adopt (current stack, healthy)
<!-- Technologies with recent versions, active maintenance -->
| Technology | Version | Status | Evidence |
|-----------|---------|--------|----------|
| React | 18.2.0 | Active LTS | package.json:8 |

### Trial (in use, evaluate alternatives)
<!-- Technologies working but with better alternatives available -->

### Assess (detected but not core)
<!-- Dev dependencies, optional tools -->

### Hold (outdated, plan migration)
<!-- EOL, deprecated, known vulnerabilities -->
| Technology | Version | Issue | Migration Path | Files Affected |
|-----------|---------|-------|---------------|----------------|
```

Classification rules:
- **Adopt**: Latest major version, active maintenance, no known CVEs
- **Trial**: Working but 1+ major versions behind, or better alternative exists
- **Assess**: Used in dev/build only, evaluate if still needed
- **Hold**: EOL announced, deprecated, or 2+ major versions behind

#### 5.5.3 — Migration Recommendations

For each item in "Hold" or "Trial", generate a migration card:

```markdown
### Migration: {Package} {current} → {target}

**Why:** {EOL date / security advisory / performance improvement}
**Evidence:** {file}:{line} — used in {N} files
**Breaking changes:** {list from changelog or [VERIFY]}
**Files affected:** {count} ({list top 5})
**Estimated effort:** {Small (1-4h) / Medium (1-3d) / Large (1-2w)}
**Priority:** {Critical / High / Medium / Low}
**Risk:** {description or "Low — non-breaking upgrade"}
```

IMPORTANT: Only recommend migrations where evidence exists. If you can't find EOL dates or changelogs, mark as `[VERIFY — check official docs for EOL status]`.

#### 5.5.4 — Security Gaps (from Phase 1 scan)

Rank by criticality:

```markdown
## Security Gaps

| # | Gap | Current State | Recommendation | Priority | Evidence |
|---|-----|--------------|----------------|----------|----------|
| 1 | No rate limiting on API | [NOT DETECTED] | Add rate limiter middleware | Critical | grep found 0 rate-limit files |
| 2 | No 2FA/MFA | [NOT DETECTED] | Add TOTP support | High | grep found 0 totp/mfa files |
```

#### 5.5.5 — Test Coverage Gaps

```bash
# Map source files to test files
find src/ -name "*.ts" -not -name "*.test.*" -not -name "*.spec.*" | wc -l  # source files
find src/ -name "*.test.*" -o -name "*.spec.*" | wc -l  # test files
```

Report:
- Total source files vs test files (ratio)
- Directories with zero test coverage
- Critical paths without tests (auth, payment, data mutation)

#### 5.5.6 — Tech Debt Summary

From Phase 1 grep results, prioritize TODOs/FIXMEs by location:

| Priority | Location Pattern | Reasoning |
|----------|-----------------|-----------|
| Critical | auth/, security/, middleware/ | Security-related debt |
| High | api/, controllers/, routes/ | API-facing debt |
| Medium | services/, helpers/, utils/ | Internal logic debt |
| Low | components/, pages/, UI/ | Cosmetic debt |

```markdown
## Tech Debt — Prioritized

| # | File | Line | Type | Content | Priority |
|---|------|------|------|---------|----------|
| 1 | api/auth.php | 45 | FIXME | "rate limit bypass" | Critical |
| 2 | api/deals.php | 123 | TODO | "add pagination" | High |
```

#### 5.5.7 — Architecture Suggestions

Only suggest if there's clear evidence:

```
WRONG: "Consider microservices for better scalability"
RIGHT: "api/ has 47 PHP files in a single directory. 
        Consider grouping by domain: api/crm/, api/marketing/, api/auth/.
        Evidence: ls api/ | wc -l = 47. No subdirectory structure detected."
```

Suggestions must include:
- What was observed (with command/file evidence)
- What could improve (specific, actionable)
- Estimated effort
- `[VERIFY]` if the current structure might be intentional

#### 5.5.8 — AI API Cost Audit

Scan all LLM API callsites, map models used, identify cost optimization opportunities.

**No tool does this from static code analysis.** Runtime tools (Langfuse, Helicone, Portkey) monitor what ran. This section analyzes code to find what COULD be optimized before execution.

**Step 1 — Build callsite inventory**

For each LLM API call detected in Phase 1.14, resolve:

```markdown
## AI API Callsite Inventory

| # | File:Line | Provider | Model | Resolution | Task Pattern | Confidence |
|---|-----------|----------|-------|------------|-------------|------------|
| 1 | src/agents/title.ts:42 | OpenAI | gpt-4o | hardcoded | Short prompt, JSON schema | RESOLVED |
| 2 | api/ai/analyze.php:18 | Anthropic | claude-sonnet-4-20250514 | env var (AI_MODEL) | Long context, reasoning | RESOLVED |
| 3 | lib/classify.py:55 | OpenAI | gpt-4 | config.yml:12 | Classification, low temp | RESOLVED |
| 4 | utils/helpers.ts:90 | unknown | unknown | dynamic (wrapper) | Cannot determine | UNRESOLVED |
```

Resolution types:
- **RESOLVED**: model name found in code, config, or env example
- **PARTIAL**: provider detected but model is dynamic or parameterized
- **UNRESOLVED**: wrapper/abstraction hides provider and model — mark `[VERIFY]`

**Step 2 — Classify task complexity per callsite**

For each RESOLVED callsite, analyze the surrounding code to infer task type:

| Signal | Points to simple task | Points to complex task |
|--------|----------------------|----------------------|
| Prompt length | < 200 tokens estimated | > 1000 tokens, multi-turn |
| Temperature | 0 or low (< 0.3) | High (> 0.7) or absent |
| Output format | JSON schema, structured, enum | Free text, creative |
| Tool use | None | Function calling, tool chains |
| Context window | Small, single document | RAG, multi-document, long context |
| Error handling | Simple retry | Cascade, fallback chain |
| Business criticality | Formatting, tagging, extraction | Auth decisions, financial, safety |

Classification:
- **SIMPLE**: Short prompt + low temperature + structured output + no tool use → cheaper model candidate
- **MODERATE**: Medium prompt + some structure + moderate complexity → evaluate case by case
- **COMPLEX**: Long context + tool use + high stakes + creative output → keep current model
- **UNKNOWN**: Cannot determine from code alone → mark `[VERIFY]`

**Step 3 — Generate cost optimization recommendations**

```markdown
## AI API Cost Audit — {Project Name}
<!-- source: Phase 1.14 scan results -->

### Provider & Model Summary
| Provider | Models Used | Callsites | Files |
|----------|-----------|-----------|-------|
| OpenAI | gpt-4o (3), gpt-4o-mini (1) | 4 | 4 |
| Anthropic | claude-sonnet-4-20250514 (2) | 2 | 2 |
| **Total** | **5 distinct models** | **6 callsites** | **6 files** |

### Cost Optimization Opportunities

#### #1 [HIGH confidence] gpt-4o → gpt-4o-mini
<!-- source: src/agents/title.ts:42 -->
- **Current**: gpt-4o ($2.50/1M input, $10.00/1M output)
- **Proposed**: gpt-4o-mini ($0.15/1M input, $0.60/1M output)
- **Why safe**: Prompt is < 100 tokens, temperature 0, JSON schema output, classification task
- **Estimated savings**: 90%+ per call at this callsite
- **Blast radius**: 1 file, title generation only
- **Risk**: LOW — task is deterministic, schema-constrained
- **Action**: Change model parameter at src/agents/title.ts:42
- **Validate**: Test with 50+ historical inputs before rollout

#### #2 [MEDIUM confidence] claude-sonnet-4-20250514 → claude-haiku for extraction
<!-- source: api/ai/extract.php:31 -->
- **Current**: claude-sonnet-4-20250514 ($3.00/1M input, $15.00/1M output)
- **Proposed**: claude-haiku-4-5-20251001 ($0.80/1M input, $4.00/1M output)
- **Why possible**: Prompt extracts structured data from fixed templates
- **Estimated savings**: ~70% per call
- **Blast radius**: 1 file, data extraction pipeline
- **Risk**: MEDIUM — extraction accuracy may degrade for edge cases
- **Action**: Change model + validate extraction accuracy
- **Validate**: Run against 100+ sample documents, compare field accuracy
- `[VERIFY]` — confirm extraction quality meets business requirements

#### #3 [LOW confidence] Consider model routing for mixed workloads
<!-- source: lib/ai-client.ts:15 (single model for all tasks) -->
- **Observation**: All 4 AI calls in this service use the same model (gpt-4o)
- **Suggestion**: Implement model routing — simple tasks (classify, extract, format) 
  to cheaper model, complex tasks (analyze, reason, generate) to frontier model
- **Pattern**: callAIWithFallback() at lib/ai-client.ts:15 already has fallback logic
- **Estimated savings**: 40-70% if 60% of calls are simple tasks
- **Risk**: Requires task classification logic + quality validation
- ⚠ Plan only — requires human architecture decisions

### What This Project Does NOT Have
<!-- Absence is evidence too -->
| Control | Status | Recommendation |
|---------|--------|---------------|
| Model routing / tiering | [NOT DETECTED] | Route simple tasks to cheaper models |
| Semantic caching | [NOT DETECTED] | Cache similar prompts to reduce API calls |
| Token/cost tracking | [NOT DETECTED] | Add per-call cost logging for visibility |
| Budget alerts | [NOT DETECTED] | Set spend limits per feature/environment |
| Prompt optimization | [NOT DETECTED] | Review prompt lengths for unnecessary context |
| Environment isolation | [VERIFY] | Confirm staging doesn't use production API keys |

### Cost Awareness Score: X/100
| Dimension | Score | Evidence |
|-----------|-------|----------|
| Model right-sizing | X/100 | Y callsites use frontier model for simple tasks |
| Cost visibility | X/100 | Token tracking: detected / not detected |
| Caching | X/100 | Semantic cache: detected / not detected |
| Routing | X/100 | Model router: detected / not detected |
| Environment isolation | X/100 | Staging API keys separate from prod: detected / not detected |
```

**Anti-hallucination for AI cost audit:**

```
WRONG: "You're spending too much on AI APIs"
RIGHT: "6 callsites detected using gpt-4o. 3 callsites have short prompts (<100 tokens),
        temperature 0, and JSON schema output — candidate for gpt-4o-mini at 90% lower cost.
        Evidence: src/agents/title.ts:42, src/classify.ts:18, api/format.php:55"

WRONG: "Switch to a cheaper model"
RIGHT: "src/agents/title.ts:42 uses gpt-4o for a classification task.
        Prompt is 47 tokens, temperature 0, output is JSON enum.
        gpt-4o-mini handles this class of task reliably.
        Validate on historical samples before switching.
        [VERIFY] — confirm output quality meets requirements"
```

Each recommendation MUST include:
1. Current model with file:line evidence
2. Proposed model with reasoning (task type, prompt characteristics)
3. Estimated savings range (based on published pricing)
4. Blast radius (files affected, downstream dependencies)
5. Risk level with explanation
6. Validation steps before rollout
7. `[VERIFY]` if task complexity cannot be determined from code alone

**Model pricing reference (for estimation, not hard claims):**

Use current published pricing from provider documentation. Mark estimates as approximate:
```
"Estimated savings: ~70% per call (based on published pricing as of scan date).
 Actual savings depend on token volume, caching, and retry patterns.
 [VERIFY] — confirm current pricing at provider's pricing page."
```

NEVER claim exact monthly savings without runtime data. Use ranges and assumptions:
```
WRONG: "You'll save $500/month"
RIGHT: "If this callsite handles ~1000 requests/day at avg 200 tokens,
        switching from gpt-4o to gpt-4o-mini could save approximately
        $X-$Y/month. [VERIFY] — actual volume unknown from code alone."
```

### Phase 6 — Generate Sales Datasheet (HTML)

Structure:
```
01. HERO — headline + 3 CTAs + metrics bar (real numbers)
02. BADGES — 6-8 chips
03. EXECUTIVE SUMMARY — [MANUAL] + detected facts
04. STICKY NAV — anchors + persona chips
05. MODULE BLOCKS — 3 layers each from endpoint/component scan
06. ROADMAP — from TODOs and issues
07. HONEST LIMITATIONS — from Phase 1 gaps
08. COMMERCIAL MODEL — [MANUAL]
09. SLA & SUPPORT — what exists + what doesn't
10. CTA FINAL
11. FOOTER
```

Design: dark theme (#0a0a0f), accent amber (#f59e0b), Space Grotesk + Inter, persona filter, accordions, responsive, print-friendly, zero dependencies.

### Phase 7 — Generate Technical Specification (HTML)

Structure:
```
00. QUICK ANSWERS — 6 answers grid
01. ARCHITECTURE — ASCII diagram, stack, modules
02. DATA FLOW & RESIDENCY — subprocessors
03. API — auth, rate limits, webhooks
04. SECURITY — controls matrix with status tags
05. PRIVACY — LGPD/GDPR controls
06. MULTI-TENANCY — isolation model (or "not multi-tenant")
07. SLA — uptime, severity, backup/DR
08. INFRA REQUIREMENTS — what client IT provisions
09. RELEASES — cadence, compat policy
10. KNOWN GAPS — with status tags and ETAs
```

Design: dark theme, accent blue (#3b82f6), JetBrains Mono for code, status tags, callout boxes, "Confidential" classification.

### Phase 8 — Validation & Report

1. Cross-check consistency between all docs (same feature = same description everywhere)
2. Count uncertainty markers: `[VERIFY]`, `[MANUAL]`, `[NOT DETECTED]`, `[PARTIAL]`
3. Test HTML (accordions, persona filter, print output)
4. Verify evolution report recommendations have evidence (no file:line = remove it)
5. Report to user:

```
## Documentation Pack Generated

### Layer 1 — Internal (MD)
- docs/architecture.md (X lines, Y sources)
- docs/data-dictionary.md (X tables)
- docs/endpoints.md (X routes)
- docs/glossary.md (X terms)
- docs/CHANGELOG.md (X entries)
- docs/security.md (X controls)
- docs/roadmap.md
- docs/contributing.md
- docs/bugs-known.md (X items)
- docs/backlog.md
- docs/pendencies.md

### Layer 2 — Sales Datasheet (HTML)
- {project}-datasheet.html

### Layer 3 — Technical Spec (HTML)
- {project}-technical-spec.html

### Layer 4 — Evolution Report
- docs/evolution-report.md
  - Dependencies audited: X (Y outdated)
  - Migration recommendations: X
  - Security gaps: X
  - Test coverage: X% estimated
  - Tech debt items: X (Y critical)
  - Tech Radar: X Adopt / Y Trial / Z Assess / W Hold

### Layer 5 — Operational Intelligence
- docs/onboarding-backend.md (X critical files, Y setup commands)
- docs/onboarding-frontend.md
- docs/onboarding-sre.md
- docs/onboarding-product.md
- docs/bus-factor-report.md (X critical-risk modules, Y single-owner)
- docs/runbooks/ (X runbooks for Y failure domains)
- docs/health-score.md (score: X/100, top 3 actions)

### Security Pack
- docs/security-whitepaper.md
- docs/data-residency.md
- docs/subprocessors.md (X services)
- docs/incident-response.md
- docs/backup-dr-policy.md

### Human Input Needed
- [count] items marked [MANUAL]
- [count] items marked [VERIFY]
- Executive summary for sales datasheet
- Pricing/commercial model details
- CTA links (demo, contact)

### Quality Metrics
- Facts with file:line evidence: X
- Uncertainty markers remaining: X
- Module coverage: X/Y documented
```

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
- Never edits an existing ADR's content — only updates Status field

---

### Phase 10 — Correction Engine (Layer 6)

Only runs if user selected Layer 6 (option 1 or 7 in Phase 0).

**10.1 — Compile issue list from previous phases**

Gather all issues found during Phases 1, 4 (Evolution), and 5 (Operational):
- Security gaps from security.md
- Outdated dependencies from evolution-report.md
- TODOs/FIXMEs from bugs-known.md
- Missing tests from health-score.md
- Lint/format issues from code scan
- AI model downgrades from AI API Cost Audit (HIGH confidence only — single-line model parameter changes)

**10.2 — Classify each issue**

For each issue, determine:
```
- Category: LINT | DEPENDENCY | SECURITY | MISSING-TEST | TECH-DEBT | ARCHITECTURE | AI-COST
- Confidence: HIGH | MEDIUM | LOW
- Blast radius: files affected, tests exist?, contracts changed?
- Auto-fixable: yes | plan-only
- Evidence: file:line where issue was detected
```

Classification rules:
- **HIGH confidence**: deterministic fixes — formatting, import order, patch dependencies, unused imports
- **MEDIUM confidence**: single-file security fixes, missing test skeletons, simple TODO resolutions
- **LOW confidence**: multi-file refactors, major dependency upgrades, architecture changes

**10.3 — Present correction plan**

Use AskUserQuestion tool to present the plan grouped by confidence level.
User must explicitly approve which fixes to apply.

IMPORTANT:
- LOW confidence items are NEVER auto-fixable — only plans/suggestions
- Show blast radius for every item
- Show diff preview for MEDIUM items
- Group by category for easy batch approval ("all-high", "all-medium")

**10.4 — Create safety branch**

```bash
git checkout -b fix/datasheet-corrections
```

If branch already exists from a previous run, ask user whether to continue or start fresh.

**10.5 — Apply approved fixes**

For each approved fix, in order of confidence (HIGH first, then MEDIUM):

1. Apply the change using Edit tool
2. Run available verification:
   ```bash
   # Adapt to detected stack
   npm run lint 2>/dev/null || npx eslint . 2>/dev/null || true
   npx tsc --noEmit 2>/dev/null || true
   npm test 2>/dev/null || true
   php -l {file} 2>/dev/null || true
   python -m py_compile {file} 2>/dev/null || true
   ```
3. If verification FAILS:
   - Revert the change: `git checkout -- {files}`
   - Report: "Fix #N failed verification: {error}. Reverted."
   - Continue to next fix
4. If verification PASSES:
   - Commit with descriptive message:
   ```
   fix({category}): {short description}
   
   Applied by generate-datasheet skill (Layer 6).
   Issue: #{number} [{CATEGORY}] {description}
   Confidence: {HIGH|MEDIUM}
   Evidence: {file}:{line}
   Revert: git revert {hash}
   ```

**10.6 — Post-fix actions**

After all approved fixes are applied:

1. Regenerate affected docs:
   - Update health-score.md (recalculate)
   - Update bugs-known.md (remove fixed items)
   - Update evolution-report.md (mark resolved items)
2. Report results to user (applied, failed, skipped, not approved)
3. Provide merge and revert instructions

**10.7 — Rules the correction engine MUST follow**

1. NEVER commit to main — always dedicated branch
2. NEVER apply LOW confidence fixes — only generate plans
3. NEVER modify database schemas, migrations, or seed files
4. NEVER change .env files, secrets, or credentials
5. NEVER delete files without explicit per-file approval
6. NEVER install new dependencies without showing what and why
7. NEVER apply a fix if ANY verification step fails — revert immediately
8. NEVER combine fixes in one commit — 1 fix = 1 commit
9. NEVER apply fixes the user didn't explicitly approve
10. NEVER skip the diff preview for MEDIUM confidence fixes
11. ALWAYS show blast radius before applying
12. ALWAYS include revert instructions in commit message

---

## Key Principles

1. **Evidence over inference** — can't point to file:line? don't write it
2. **Uncertainty is honest** — `[NOT DETECTED]` beats a guess
3. **Humans approve, AI executes** — skill proposes, human decides, skill applies
4. **Security by transparency** — document gaps, don't hide them
5. **Scan-to-signal ratio** — tables not paragraphs
6. **The champion test** — non-technical person forwards to IT with confidence
7. **The audit test** — infosec reviews risk from security pack alone
8. **The evolution test** — tech lead prioritizes next quarter from the report
9. **The correction test** — every fix is revertible, verifiable, and explainable
10. **No AI washing** — show what AI does, don't say "AI-powered"
11. **Docs-as-code** — markdown, versionable, diffable
12. **Cure for vibe-coding** — code nobody can explain is a liability
13. **Fixes need evidence** — no fix without file:line, blast radius, and confidence label
14. **1 fix = 1 commit** — atomic, revertible, traceable
15. **PRD from code, not from imagination** — Layer 7 documents what exists and what users explicitly said; it never invents personas, features, or intent
16. **Two gates, no shortcuts** — As-Is gate before the interview, To-Be gate before generation; skipping either defeats the purpose

## What This Skill Is NOT

- Not a marketing copy generator — it documents reality
- Not SonarQube — it explains WHY, not just WHAT is wrong
- Not a replacement for human judgment — it structures, humans decide
- Not a one-time tool — re-run when codebase changes
- Not opinionated about your stack — works with any language/framework
- Not noisy — every finding has evidence or gets `[VERIFY]` marker
- Not an autonomous agent — never applies changes without approval
- Not destructive — never deletes, never touches main, never skips verification

## References

- Salesforce Trust Documentation (architecture separation)
- Rippling Security Datasheet (layered depth)
- Databricks Security Whitepaper (quick security review)
- Stripe Security Documentation (anticipate questions)
- 1Password Enterprise Datasheet (walk the model)
- Thoughtworks Technology Radar (Adopt/Trial/Assess/Hold format)
- FastAPI, Supabase, Cal.com (well-documented OSS)
- GitHub Copilot Autofix (responsible-use guidance, failure modes)
- Snyk Agent Fix (candidate fix generation, single-file limitation)
- CodeRabbit Autofix (PR-driven correction workflow)
- Dependabot (noise management, auto-merge patterns)
- ESLint safe-fix vs unsafe-fix (scope of automated changes)
- CAIQ, SIG questionnaire standards
- Technical Debt Master (`tdm`) — evidence-based debt discovery
- Vibe-coding crisis research (Osmani/Google, Veracode 2025)
- SonarQube/CodeClimate complaints (Reddit r/devops, r/cybersecurity, HN)
