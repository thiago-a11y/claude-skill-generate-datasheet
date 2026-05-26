---
name: generate-datasheet
version: 2.1.0
description: |
  Complete documentation pack generator for any codebase. Scans your project 
  and generates evidence-based documentation — only documents what it can prove 
  from actual files, configs, and code. Zero hallucination by design.
  
  Generates 4 layers:
  Layer 1 (Internal/MD): architecture.md, data-dictionary.md, glossary.md, 
    changelog.md, endpoints.md, security.md, roadmap.md, contributing.md, 
    bugs-known.md, backlog.md, pendencies.md
  Layer 2 (External/HTML): Sales datasheet with persona filters, 3-layer 
    progressive disclosure, dark theme
  Layer 3 (External/HTML): Technical specification for CTOs/IT with 
    architecture diagrams, security controls, API reference, SLA, known gaps
  Layer 4 (Evolution/MD): evolution-report.md — tech debt radar, migration 
    recommendations, dependency audit, security gaps, test coverage gaps, 
    performance suggestions. Thoughtworks Radar format (Adopt/Trial/Assess/Hold).
  
  Plus: Security Pack (security-whitepaper.md, data-residency.md, 
    subprocessors.md, incident-response.md, backup-dr-policy.md)
  
  Built to cure the vibe-coding documentation crisis: functional projects 
  that nobody can explain, maintain, or audit.
  
  Use when: "generate docs", "document this project", "create datasheet", 
  "generate documentation", "security docs", "tech debt", "evolution report",
  "ficha técnica", "escopo técnico", "documentar projeto", "what should I upgrade".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Agent
  - AskUserQuestion
---

# Generate Datasheet v2.1 — Complete Documentation Pack

## What this skill produces

Four layers of documentation from a single codebase scan:

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

### Security Pack (Markdown)

For compliance, infosec reviews, and procurement.

| File | Content | Source |
|------|---------|--------|
| `docs/security-whitepaper.md` | Complete security posture | Auth, encryption, headers, audit code |
| `docs/data-residency.md` | Where data is stored/processed/transferred | Configs, API calls, hosting info |
| `docs/subprocessors.md` | External services with data access | grep for external API URLs |
| `docs/incident-response.md` | Response plan template + current capabilities | Monitoring, logging, alerting code |
| `docs/backup-dr-policy.md` | Backup frequency, RPO, RTO, restore process | Cron jobs, backup configs, hosting |

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
What documentation do you need?

1. Full pack (internal MD + sales HTML + technical HTML + security + evolution report)
2. Internal only (MD files for the dev team)
3. External only (sales + technical HTML)
4. Security pack only
5. Evolution report only (tech debt, migrations, dependency audit, gaps)
6. Specific files (I'll tell you which)
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
6. Which layers? (internal MD / sales HTML / technical HTML / security pack / evolution report)
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

---

## Key Principles

1. **Evidence over inference** — can't point to file:line? don't write it
2. **Uncertainty is honest** — `[NOT DETECTED]` beats a guess
3. **Humans provide context** — skill provides structure, humans verify
4. **Security by transparency** — document gaps, don't hide them
5. **Scan-to-signal ratio** — tables not paragraphs
6. **The champion test** — non-technical person forwards to IT with confidence
7. **The audit test** — infosec reviews risk from security pack alone
8. **The evolution test** — tech lead can prioritize next quarter from the report alone
9. **No AI washing** — show what AI does, don't say "AI-powered"
10. **Docs-as-code** — markdown, versionable, diffable
11. **Cure for vibe-coding** — code nobody can explain is a liability
12. **Recommendations need evidence** — "migrate X→Y" requires file count, EOL date, breaking changes

## What This Skill Is NOT

- Not a marketing copy generator — it documents reality
- Not SonarQube — it explains WHY, not just WHAT is wrong
- Not a replacement for human judgment — it structures, humans verify
- Not a one-time tool — re-run when codebase changes
- Not opinionated about your stack — works with any language/framework
- Not noisy — every recommendation has evidence or gets `[VERIFY]` marker

## References

- Salesforce Trust Documentation (architecture separation)
- Rippling Security Datasheet (layered depth)
- Databricks Security Whitepaper (quick security review)
- Stripe Security Documentation (anticipate questions)
- 1Password Enterprise Datasheet (walk the model)
- Thoughtworks Technology Radar (Adopt/Trial/Assess/Hold format)
- FastAPI, Supabase, Cal.com (well-documented OSS)
- CAIQ, SIG questionnaire standards
- Technical Debt Master (`tdm`) — evidence-based debt discovery
- Vibe-coding crisis research (Osmani/Google, Veracode 2025)
- SonarQube/CodeClimate complaints (Reddit r/devops, r/cybersecurity, HN)
