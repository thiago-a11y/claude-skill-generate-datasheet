---
name: generate-datasheet
version: 2.0.0
description: |
  Complete documentation pack generator for any codebase. Scans your project 
  and generates evidence-based documentation — only documents what it can prove 
  from actual files, configs, and code. Zero hallucination by design.
  
  Generates 3 layers:
  Layer 1 (Internal/MD): architecture.md, data-dictionary.md, glossary.md, 
    changelog.md, endpoints.md, security.md, roadmap.md, contributing.md, 
    bugs-known.md, backlog.md, pendencies.md
  Layer 2 (External/HTML): Sales datasheet with persona filters, 3-layer 
    progressive disclosure, dark theme
  Layer 3 (External/HTML): Technical specification for CTOs/IT with 
    architecture diagrams, security controls, API reference, SLA, known gaps
  
  Plus: Security Pack (security-whitepaper.md, data-residency.md, 
    subprocessors.md, incident-response.md, backup-dr-policy.md)
  
  Built to cure the vibe-coding documentation crisis: functional projects 
  that nobody can explain, maintain, or audit.
  
  Use when: "generate docs", "document this project", "create datasheet", 
  "generate documentation", "security docs", "ficha técnica", "escopo técnico",
  "documentar projeto".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Agent
  - AskUserQuestion
---

# Generate Datasheet v2 — Complete Documentation Pack

## What this skill produces

Three layers of documentation from a single codebase scan:

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

1. Full pack (internal MD + sales HTML + technical HTML + security)
2. Internal only (MD files for the dev team)
3. External only (sales + technical HTML)
4. Security pack only
5. Specific files (I'll tell you which)
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
6. Which layers? (internal MD / sales HTML / technical HTML / security pack)
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

1. Cross-check consistency between docs
2. Count uncertainty markers
3. Test HTML (accordions, filter, print)
4. Report: files created, human input needed, quality metrics

---

## Key Principles

1. **Evidence over inference** — can't point to file:line? don't write it
2. **Uncertainty is honest** — `[NOT DETECTED]` beats a guess
3. **Humans provide context** — skill provides structure
4. **Security by transparency** — document gaps, don't hide them
5. **Scan-to-signal ratio** — tables not paragraphs
6. **The champion test** — non-technical person forwards to IT with confidence
7. **The audit test** — infosec reviews risk from security pack alone
8. **No AI washing** — show what AI does, don't say "AI-powered"
9. **Docs-as-code** — markdown, versionable, diffable
10. **Cure for vibe-coding** — code nobody can explain is a liability

## References

- Salesforce Trust Documentation (architecture separation)
- Rippling Security Datasheet (layered depth)
- Databricks Security Whitepaper (quick security review)
- Stripe Security Documentation (anticipate questions)
- 1Password Enterprise Datasheet (walk the model)
- FastAPI, Supabase, Cal.com (well-documented OSS)
- CAIQ, SIG questionnaire standards
- Vibe-coding crisis research (Osmani, Veracode 2025)
