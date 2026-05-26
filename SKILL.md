---
name: generate-datasheet
version: 1.0.0
description: |
  Generates two production-quality HTML documents from your codebase:
  1. Sales Datasheet — dark industrial theme, persona filters, 3-layer progressive 
     disclosure (title → features → technical accordion), CTA sections, honest 
     limitations. For executives, buyers, and marketing teams.
  2. Technical Specification — architecture diagrams, data flow, API reference, 
     security controls, LGPD/GDPR, multi-tenancy isolation, SLA, infrastructure 
     requirements, and known gaps. For CTOs, IT managers, and infosec teams.
  
  Both are standalone HTML files with zero dependencies (only Google Fonts CDN).
  Responsive, print-friendly (PDF export via window.print), dark theme.
  
  Use when: "generate datasheet", "create technical docs", "build sales page",
  "product documentation", "ficha técnica", "escopo técnico".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Agent
  - AskUserQuestion
---

# Generate Datasheet — Sales + Technical HTML Documentation

## What this skill produces

Two standalone HTML files from your codebase:

| Document | Audience | Content |
|----------|----------|---------|
| `{project}-datasheet.html` | Executives, Buyers, Marketing | Product overview, features by module, persona filters, CTAs, limitations |
| `{project}-technical-spec.html` | CTOs, IT Managers, Infosec | Architecture, data flow, API, security, SLA, multi-tenancy, gaps |

## Process

### Phase 1 — Discovery (read-only, no output yet)

Scan the codebase to build a complete picture. Do NOT generate any files yet.

**1.1 — Project Identity**
- Read README.md, CLAUDE.md, package.json, composer.json for project name, description, stack
- Identify: product name, company name, target audience, deployment model

**1.2 — Architecture**
- Identify frontend framework (React, Vue, Angular, etc.) and version
- Identify backend language/framework and version
- Identify database type and approximate table count
- Identify web server and hosting model
- Map: `find . -name "*.env*" -o -name "config.*" -o -name "docker-compose.*" | head -20`

**1.3 — Endpoints & API**
- Count API endpoints: `find ./api -name "*.php" -o -name "*.py" -o -name "*.ts" | wc -l` (adapt to stack)
- Check for OpenAPI/Swagger spec files
- Identify authentication method (JWT, OAuth, API Keys, sessions)
- Check for rate limiting implementation
- Check for webhook endpoints (inbound and outbound)

**1.4 — Database & Data**
- Count tables: look for migrations, schema files, or ORM models
- Identify multi-tenancy model (if any)
- Check for audit logging
- Identify data residency (hosting location)

**1.5 — Security**
- Check for: MFA/2FA, RBAC, encryption, CORS config, security headers
- Look for: auth middleware, password hashing, token management
- Identify certifications or compliance mentions in docs

**1.6 — Integrations**
- Find external API calls: `grep -r "https://" --include="*.php" --include="*.ts" --include="*.py" | grep -i "api\|oauth\|webhook" | head -30`
- Identify: email service, AI providers, payment, analytics, CRM, ads platforms
- Map OAuth flows and API key usage

**1.7 — Documentation**
- Read existing: CHANGELOG.md, architecture.md, docs/*.md
- Identify modules/features from route files, sidebar navigation, menu configs
- Count: PRs merged (git log), migrations, releases

**1.8 — Gaps**
- Identify what's missing: SSO, SOC2, pentest, mobile app, HA, staging env
- Check for TODO/FIXME comments: `grep -r "TODO\|FIXME\|HACK" --include="*.php" --include="*.ts" | wc -l`
- Look for incomplete features or partial implementations

### Phase 2 — Branding Decision

Ask the user:

```
Before generating, I need a few decisions:

1. **AI Branding**: Do you use AI/LLM features? If yes, should I:
   a) Brand all AI under a proprietary name (e.g., "[Product] AI") — recommended for sales docs
   b) Name specific providers (OpenAI, Anthropic, etc.) — more transparent but commoditizes

2. **What's your product name and company name?**

3. **Who is your target audience?** (e.g., "B2B industrial companies, 20-500 employees")

4. **Any integrations or providers you want to HIDE from the sales doc?**
   (They'll still appear in the technical spec's subprocessors section)

5. **Do you have a logo URL or should I use text-only headers?**
```

### Phase 3 — Generate Sales Datasheet

Create `{project}-datasheet.html` following this exact structure:

```
01. HERO — headline + subheadline + 3 CTAs + credibility metrics bar
02. BADGES — 6-8 horizontal chips (scan in <3 seconds)
03. EXECUTIVE SUMMARY — max 300 words, 5 paragraphs
04. STICKY NAV — anchor links + persona filter chips
05. MODULE BLOCKS — one card per module, each with:
    - Layer 1: Title + value proposition (1 sentence)
    - Layer 2: 4-6 feature bullets (visible by default)
    - Layer 3: Accordion "Technical specs" (collapsed by default)
06. ROADMAP — timeline with priority dots + status badges
07. HONEST LIMITATIONS — what the product is NOT
08. COMMERCIAL MODEL — what's included vs. additional cost
09. SLA & SUPPORT — table format
10. CTA FINAL — headline + 3 action buttons
11. FOOTER — company info, version, contact
```

**Design rules:**
- Dark theme: `--bg: #0a0a0f`, accent color amber (#f59e0b) or blue (#3b82f6)
- Fonts: Space Grotesk (display) + Inter (body) via Google Fonts
- Persona filter: chips that dim irrelevant sections (opacity 0.35), not hide
- Accordion: `max-height` transition, chevron rotation
- Responsive: 2-col → 1-col at 768px
- Print styles: white background, all accordions expanded
- Zero JS dependencies. Vanilla only.
- Export PDF: `window.print()` button

**Content rules:**
- NO empty adjectives ("powerful", "robust", "intelligent")
- USE measurable specs ("failover <2s", "50k emails/day", "116 releases")
- Honest limitations section is MANDATORY — builds more trust than hiding gaps
- AI features branded under proprietary name (from Phase 2)
- External providers abstracted in sales doc, detailed in tech spec
- Language: match project's primary language (detect from README/docs)

### Phase 4 — Generate Technical Specification

Create `{project}-technical-spec.html` following this structure:

```
00. QUICK ANSWERS — 6 answers in 60 seconds (grid at top)
01. ARCHITECTURE — context diagram (ASCII), stack table, module inventory
02. DATA FLOW & RESIDENCY — where data originates/processes/stores, subprocessors table
03. API & INTEGRATIONS — OpenAPI ref, auth methods, rate limits, webhooks in/out, integration map
04. SECURITY — identity/access matrix, encryption table, audit log details, HTTP headers, certifications
05. PRIVACY (LGPD/GDPR) — controls checklist, international transfer table, legal basis
06. MULTI-TENANCY — isolation model per layer, feature gating, plan enforcement
07. SLA & OPERATIONS — uptime target, severity matrix, backup/DR with RPO/RTO, cron jobs
08. INFRASTRUCTURE REQUIREMENTS — what client IT needs to provision (browser, network, DNS, SSO)
09. RELEASES — cadence, backward compat policy, migration strategy, rollback
10. KNOWN GAPS — security gaps, infra gaps, feature gaps — with status tags and ETAs
```

**Design rules:**
- Same dark theme but accent color blue (#3b82f6) to distinguish from sales doc
- Add monospace font (JetBrains Mono) for code blocks and diagrams
- ASCII diagrams for architecture (context + container views)
- Status tags: green (Implemented), amber (Partial), gray (Not available)
- Callout boxes for important warnings (warn = amber border, info = cyan border)
- Tables are the primary content format — scannable, not narrative
- "Confidencial — Uso em avaliação" classification in header and footer
- Print styles: same as sales doc

**Content rules:**
- This document must answer 6 questions in under 10 minutes:
  1. Where does the system run?
  2. What data enters, moves through, and leaves it?
  3. How does it integrate with our stack?
  4. What security and compliance controls exist?
  5. What are the service guarantees and operational limits?
  6. What must our IT team provision before go-live?
- Gaps section is MANDATORY and must be brutally honest
- Include RPO/RTO even if they're not great — honesty > omission
- Status tags on EVERY control: Implemented / Partial / Not available
- Subprocessors table with exact data types and regions
- Rate limits with exact numbers, not "configurable"

### Phase 5 — Validation

After generating both files:

1. **Scan for inconsistencies** — same feature must have same description in both docs
2. **Check all accordions work** — toggle each one in browser
3. **Test persona filter** — click each chip, verify dimming
4. **Test print** — window.print() should produce clean output
5. **Verify no provider names leak** into sales doc (if branding was chosen)
6. **Report to user:**
   - Files created with paths
   - Summary of what was included
   - List of decisions that need human input (pricing, CTA links, logo, etc.)

## Key Principles

1. **The sales doc is a 24/7 salesperson** — it must qualify leads by persona in <10 seconds
2. **The tech spec is a procurement accelerator** — IT must validate fit without scheduling a call
3. **Honesty > Completeness** — a gap documented is better than a feature exaggerated
4. **Scan-to-signal ratio** — tables and bullets, not paragraphs
5. **The champion test** — a non-technical person must be able to forward the sales doc to IT with confidence
6. **No AI washing** — don't use "AI-powered" as an adjective. Show what the AI actually does.

## References

Best practices derived from:
- Salesforce Trust & Compliance Documentation structure
- Rippling Security Program datasheet format
- Databricks Security Whitepaper approach
- Stripe Security documentation model
- 1Password Enterprise datasheet transparency
- Freshworks developer documentation guidelines
- Research: CAIQ, SIG questionnaire requirements for mid-market SaaS
