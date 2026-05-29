---
name: generate-compliance
version: 1.0.0
description: |
  Pre-fills security compliance questionnaires from codebase evidence.
  CAIQ, SIG Lite, LGPD/GDPR data mapping — each answer traced to code.
  Generates evidence manifest JSON + unsupported claims section.
  Zero hallucination. What can't be proven gets [MANUAL].
  
  Use when: "compliance", "CAIQ", "SIG", "questionnaire", "security questionnaire",
  "procurement", "vendor assessment", "LGPD", "GDPR", "SOC 2", "audit",
  "questionário de segurança", "compliance questionnaire".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Generate Compliance v1 — Security Questionnaires from Code Evidence

## What this skill produces

### 1. Pre-filled Questionnaire (Markdown)
CAIQ or SIG Lite questionnaire with answers extracted from code:
- Each answer includes evidence source (file:line)
- Confidence level per answer (PROVEN / PARTIAL / UNVERIFIABLE)
- `[MANUAL]` for questions that require human/organizational input
- Status tags: Implemented / Partial / Not Implemented / Not Applicable

### 2. Evidence Manifest (JSON)
Machine-readable mapping of every control to its code evidence:
```json
{
  "controls": [
    {
      "id": "AIS-01",
      "question": "Application security: secure coding practices?",
      "status": "PARTIAL",
      "confidence": "PROVEN",
      "evidence": [
        {"type": "file", "path": "middleware/auth.php", "line": 15, "finding": "JWT validation"},
        {"type": "file", "path": "middleware/cors.php", "line": 8, "finding": "CORS configuration"}
      ],
      "gaps": ["No input validation middleware detected", "No SAST/DAST pipeline detected"],
      "manual_input_needed": false
    }
  ]
}
```

### 3. Unsupported Claims Report (Markdown)
What the code CANNOT prove:
- Organizational policies (HR, training, incident response team)
- Physical security controls
- Business continuity procedures not in code
- Contractual obligations (SLAs, DPAs)
- Third-party audit results (SOC 2 reports, pentest results)
- Insurance and legal protections

### 4. LGPD/GDPR Data Mapping (Markdown)
If personal data processing detected:
- Data categories collected (from DB schema + forms)
- Processing purposes (inferred from code context)
- Legal basis per processing activity (`[MANUAL]`)
- Data retention policies (from code or `[NOT DETECTED]`)
- Data subject rights implementation status
- International transfers (from API calls to external services)

---

## Anti-Hallucination Protocol

Compliance questionnaires are HIGH STAKES — a wrong answer can have legal/contractual consequences.

```
WRONG: "Yes, we implement secure coding practices"
RIGHT: "PARTIAL — JWT auth detected (middleware/auth.php:15), CORS configured
       (middleware/cors.php:8), password hashing with bcrypt (auth/register.php:42).
       NOT DETECTED: input validation middleware, SAST/DAST in CI pipeline,
       dependency vulnerability scanning.
       [MANUAL] — describe organizational secure coding training and review process."

WRONG: "Data is encrypted at rest"
RIGHT: "UNVERIFIABLE from code. Database encryption depends on hosting configuration.
       [MANUAL] — confirm with hosting provider whether MySQL encryption at rest is enabled.
       In-code encryption: [NOT DETECTED] — no application-level field encryption found."
```

### Confidence levels

| Level | Meaning | When to use |
|-------|---------|-------------|
| **PROVEN** | Direct code evidence exists | Found auth middleware, encryption function, CORS config |
| **PARTIAL** | Some evidence but incomplete | Found JWT but no refresh token, CORS but permissive |
| **UNVERIFIABLE** | Cannot determine from code alone | Infrastructure config, hosting setup, org policies |
| **NOT APPLICABLE** | Control doesn't apply to this system | Mobile controls for web-only, physical for cloud |

### Status tags

| Tag | Meaning |
|-----|---------|
| `Implemented` | Code evidence confirms the control is in place |
| `Partial` | Some aspects implemented, gaps identified |
| `Not Implemented` | Looked for evidence, found none |
| `Not Applicable` | Control doesn't apply (with justification) |
| `[MANUAL]` | Requires organizational/human input |

---

## Process

### Phase 0 — Pre-flight

Ask the user:

```
What do you need?

1. CAIQ (Consensus Assessments Initiative Questionnaire) — cloud security, 260+ questions
2. SIG Lite (Standardized Information Gathering) — vendor risk, 100+ questions
3. LGPD/GDPR Data Mapping — personal data processing inventory
4. All of the above
5. Specific sections only (I'll tell you which)

Additional context:
- Company name and product name?
- Hosting model? (cloud / on-prem / shared hosting / hybrid)
- Any existing certifications? (SOC 2, ISO 27001, etc.)
- Data processing regions? (if known)
```

### Phase 1 — Security Discovery

Reuse Phase 1 from generate-datasheet if available. Otherwise run:

**1.1 — Authentication & Access Control**
```bash
# Auth mechanisms
grep -rn "jwt\|JWT\|bcrypt\|argon\|password_hash\|password_verify\|passport\|oauth\|session" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -20

# RBAC / permissions
grep -rn "role\|permission\|isAdmin\|authorize\|can(\|hasRole\|guard" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15

# MFA / 2FA
grep -rn "totp\|2fa\|mfa\|two.factor\|authenticator\|otp" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10

# Session management
grep -rn "session\|cookie\|expires\|maxAge\|ttl\|timeout.*session" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10
```

**1.2 — Data Protection**
```bash
# Encryption
grep -rn "encrypt\|decrypt\|AES\|RSA\|crypto\|cipher\|hash\|hmac" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15

# HTTPS / TLS
grep -rn "https\|ssl\|tls\|certificate\|HSTS\|Strict-Transport" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.yml" --include="*.conf" 2>/dev/null | head -10

# Personal data fields
grep -rn "email\|phone\|cpf\|cnpj\|address\|birth\|gender\|salary\|password\|ssn\|social.security" --include="*.sql" --include="*.prisma" --include="*.ts" --include="*.php" 2>/dev/null | grep -i "create\|column\|field\|model\|schema" | head -20

# Data retention / deletion
grep -rn "delete.*user\|purge\|retention\|soft.delete\|anonymize\|gdpr\|lgpd\|right.*forget\|erasure" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10
```

**1.3 — Security Headers & Network**
```bash
# Security headers
grep -rn "helmet\|X-Frame\|X-Content-Type\|Content-Security-Policy\|X-XSS\|Referrer-Policy\|Permissions-Policy" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.conf" 2>/dev/null | head -15

# CORS
grep -rn "cors\|Access-Control-Allow\|origin" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10

# Rate limiting
grep -rn "rate.limit\|throttle\|too.many.requests\|429" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10

# Input validation / sanitization
grep -rn "sanitize\|escape\|htmlspecialchars\|xss\|injection\|prepared.*statement\|parameterized\|bindParam\|placeholder" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15
```

**1.4 — Logging & Monitoring**
```bash
# Audit logging
grep -rn "audit\|log.*event\|log.*action\|activity.*log\|track\|record.*action" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -15

# Error logging
grep -rn "logger\|winston\|pino\|log4\|monolog\|logging\|sentry\|bugsnag\|rollbar" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10

# Monitoring / health checks
grep -rn "health\|ping\|status\|monitor\|uptime\|datadog\|newrelic\|prometheus" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -10
```

**1.5 — CI/CD & Development Practices**
```bash
# CI/CD pipeline
ls .github/workflows/ 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | head -40

# Linters / formatters
ls .eslintrc* .prettierrc* .flake8 .pylintrc tslint* biome.json 2>/dev/null
cat package.json 2>/dev/null | grep -A5 '"lint\|format\|eslint\|prettier"'

# Tests
find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*" | wc -l

# Dependency scanning
grep -rn "npm audit\|snyk\|dependabot\|renovate\|safety check" .github/ 2>/dev/null | head -5
cat .github/dependabot.yml 2>/dev/null | head -20
```

**1.6 — External Services & Data Flow**
```bash
# External API calls (data leaves the system)
grep -rn "https://.*api\|amazonaws\|googleapis\|graph.facebook\|api.openai\|api.anthropic\|stripe\|twilio\|sendgrid" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" 2>/dev/null | head -25

# Data storage locations
grep -rn "s3\|blob\|storage\|upload\|bucket\|cdn\|cloudflare\|cloudfront" --include="*.ts" --include="*.js" --include="*.py" --include="*.php" --include="*.yml" 2>/dev/null | head -10

# Backup patterns
grep -rn "backup\|dump\|export\|snapshot\|replicate" --include="*.sh" --include="*.yml" --include="*.php" --include="*.py" 2>/dev/null | head -10
```

### Phase 2 — Map Findings to Controls

For each questionnaire section, map Phase 1 findings to specific control questions.

**Mapping rules:**
- One finding can answer multiple questions
- One question can have evidence from multiple findings
- If no finding maps to a question → `Not Implemented` + `[MANUAL]` if it could exist outside code
- If partial findings → `Partial` with specific gaps listed
- NEVER mark as `Implemented` without file:line evidence

### Phase 3 — Generate CAIQ

Generate `docs/compliance/caiq-{project}.md`:

```markdown
# CAIQ — {Project Name}
<!-- Generated by generate-compliance v1. Evidence-based — every answer traced to code. -->
<!-- PROVEN = code evidence exists. [MANUAL] = requires organizational input. -->
<!-- Generated on: {date}. Re-run to update after code changes. -->

## Summary
- Total controls: [count]
- Implemented: [count] ([percentage]%)
- Partial: [count]
- Not Implemented: [count]
- Not Applicable: [count]
- Requires [MANUAL] input: [count]

## AIS — Application & Interface Security

### AIS-01: Application Security — Secure Development
**Status**: Partial
**Confidence**: PROVEN

**Evidence**:
- JWT authentication: middleware/auth.php:15
- Password hashing (bcrypt): auth/register.php:42
- CORS configuration: middleware/cors.php:8
- Input validation: [NOT DETECTED] — no validation middleware found
- SAST in CI: [NOT DETECTED] — no security scanning in workflows

**Gaps**:
- No input validation middleware detected
- No SAST/DAST tools in CI pipeline
- No code review enforcement detected

**[MANUAL]**: Describe secure coding training program and code review process.

---

### AIS-02: Application Security — Customer Access Requirements
**Status**: Implemented
**Confidence**: PROVEN

**Evidence**:
- Auth required on all API endpoints: middleware/auth.php applied to router (routes/api.php:3)
- Role-based access: middleware/checkRole.php:12
- Session timeout: config.php:45 (session.gc_maxlifetime = 3600)

---
```

Continue for all CAIQ domains:
- AIS (Application & Interface Security)
- BCR (Business Continuity & Operational Resilience)
- CCC (Change Control & Configuration Management)
- CEK (Cryptography, Encryption & Key Management)
- DSP (Data Security & Privacy Lifecycle)
- GRC (Governance, Risk & Compliance)
- HRS (Human Resources)
- IAM (Identity & Access Management)
- IPY (Interoperability & Portability)
- IVS (Infrastructure & Virtualization Security)
- LOG (Logging & Monitoring)
- SEF (Security Incident Management)
- TVM (Threat & Vulnerability Management)

For HRS, BCR, GRC — most answers will be `[MANUAL]` since these are organizational, not code-based.

### Phase 4 — Generate SIG Lite

Generate `docs/compliance/sig-lite-{project}.md`:

Same format as CAIQ but mapped to SIG Lite domains:
- Information Security Management
- Access Control
- Application Security
- Change Management
- Data Security
- Network Security
- Physical Security (mostly `[MANUAL]` or `Not Applicable`)
- Risk Management
- Security Incident Management
- Business Continuity

### Phase 5 — Generate LGPD/GDPR Data Mapping

Generate `docs/compliance/data-mapping-{project}.md`:

```markdown
# LGPD/GDPR Data Processing Inventory — {Project Name}
<!-- Generated by generate-compliance v1. -->

## Personal Data Detected

| # | Data Category | Fields | Source | Purpose | Legal Basis |
|---|--------------|--------|--------|---------|-------------|
| 1 | Contact info | email, phone | users table (migration:15) | Account creation | [MANUAL] |
| 2 | Identity | name, cpf | users table (migration:15) | User identification | [MANUAL] |
| 3 | Financial | payment_method | payments table (migration:42) | Billing | [MANUAL] |

## Data Flow — Where Data Goes

| Destination | Data Sent | Purpose | Evidence |
|-------------|-----------|---------|----------|
| Stripe (api.stripe.com) | payment info | Payment processing | payments/charge.php:22 |
| SendGrid (api.sendgrid.com) | email, name | Transactional email | email/send.php:15 |
| OpenAI (api.openai.com) | user text inputs | AI processing | ai/analyze.php:30 |

## Data Subject Rights Implementation

| Right | Status | Evidence |
|-------|--------|----------|
| Access (portability) | [NOT DETECTED] | No data export endpoint found |
| Rectification | Partial | User profile edit at api/profile.php:20 |
| Erasure (right to delete) | [NOT DETECTED] | No account deletion flow found |
| Objection | [NOT DETECTED] | No opt-out mechanism found |
| Data minimization | [VERIFY] | Review fields collected vs. necessary |

## Retention & Deletion

| Data | Retention Period | Deletion Method | Evidence |
|------|-----------------|-----------------|----------|
| User accounts | [NOT DETECTED] | [NOT DETECTED] | No retention policy in code |
| Logs | [NOT DETECTED] | [NOT DETECTED] | No log rotation detected |
| Backups | [MANUAL] | [MANUAL] | Depends on hosting provider |

## International Transfers
<!-- source: Phase 1.6 external API calls -->
| Service | Region | Data Transferred | Safeguard |
|---------|--------|-----------------|-----------|
```

### Phase 6 — Generate Evidence Manifest

Generate `docs/compliance/evidence-manifest.json`:

Valid JSON file mapping every control to its evidence chain. This file enables:
- Automated verification (re-scan and check evidence still exists)
- Audit trail (when was evidence last verified)
- Gap tracking (what needs human input)

### Phase 7 — Generate Unsupported Claims Report

Generate `docs/compliance/unsupported-claims.md`:

```markdown
# Unsupported Claims — What Code Cannot Prove

This report lists compliance aspects that CANNOT be verified from source code alone.
These require organizational documentation, policies, or third-party evidence.

## Organizational Controls (always [MANUAL])
- [ ] Employee security training program
- [ ] Background check process
- [ ] Security awareness campaigns
- [ ] Incident response team composition
- [ ] Management security commitment

## Physical Security (always [MANUAL] for cloud/hosted)
- [ ] Data center security
- [ ] Office access controls
- [ ] Device management policy
- [ ] Media disposal procedures

## Contractual & Legal (always [MANUAL])
- [ ] Data Processing Agreement (DPA)
- [ ] Service Level Agreement (SLA) commitments
- [ ] Cyber insurance coverage
- [ ] Legal basis for data processing (LGPD/GDPR)
- [ ] Subprocessor agreements

## Infrastructure (depends on hosting)
- [ ] Encryption at rest (database level)
- [ ] Network segmentation
- [ ] DDoS protection
- [ ] Backup verification/testing
- [ ] Disaster recovery testing

## Third-Party Evidence (requires external docs)
- [ ] SOC 2 Type II report
- [ ] Penetration test results
- [ ] Vulnerability scan results
- [ ] Third-party security audit
```

### Phase 8 — Validation & Report

```
## Compliance Pack Generated

### CAIQ
- docs/compliance/caiq-{project}.md
- Controls: [total] | Implemented: [count] | Partial: [count] | [MANUAL]: [count]

### SIG Lite
- docs/compliance/sig-lite-{project}.md
- Controls: [total] | Implemented: [count] | Partial: [count] | [MANUAL]: [count]

### LGPD/GDPR Data Mapping
- docs/compliance/data-mapping-{project}.md
- Personal data categories: [count]
- External data transfers: [count]
- Data subject rights gaps: [count]

### Evidence Manifest
- docs/compliance/evidence-manifest.json
- Total evidence items: [count]
- PROVEN: [count] | PARTIAL: [count] | UNVERIFIABLE: [count]

### Unsupported Claims
- docs/compliance/unsupported-claims.md
- Items requiring organizational input: [count]

### Action Items
1. Fill [MANUAL] items in CAIQ and SIG Lite ([count] items)
2. Confirm data processing legal basis for LGPD/GDPR ([count] data categories)
3. Provide organizational policies for [list of domains]
4. Attach third-party evidence if available (SOC 2, pentest, etc.)
```

---

## Key Principles

1. **Evidence over claims** — "Implemented" requires file:line proof
2. **Honesty is compliance** — `Not Implemented` beats a false "yes"
3. **Code is partial truth** — organizational controls need `[MANUAL]` input
4. **Confidence matters** — PROVEN / PARTIAL / UNVERIFIABLE per answer
5. **Unsupported claims listed** — what code CAN'T prove is as important as what it can
6. **Machine-readable output** — evidence manifest enables automated re-verification
7. **Stack agnostic** — works with any language/framework
8. **Non-prescriptive** — documents what IS, doesn't judge what SHOULD be

## What This Skill Is NOT

- Not legal advice — output is evidence gathering, not legal compliance assessment
- Not a certification — generates evidence, humans/auditors make compliance decisions
- Not a replacement for auditors — structures evidence for them to review faster
- Not SOC 2 ready — generates evidence mapping, not the audit report itself
- Not a security scanner — documents controls, doesn't find vulnerabilities
