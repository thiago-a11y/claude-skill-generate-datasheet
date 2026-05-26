# generate-datasheet

A Claude Code skill that generates two production-quality HTML documents from your codebase:

1. **Sales Datasheet** — dark industrial theme, persona filters, 3-layer progressive disclosure, CTAs, honest limitations
2. **Technical Specification** — architecture, security, API, SLA, multi-tenancy, known gaps

Both are standalone HTML files with zero dependencies. Responsive, print-friendly, dark theme.

## Why

- Most SaaS companies have bad technical documentation ([source](https://www.productmarketingalliance.com/developer-marketing/discover-the-key-types-of-saas-documentation-real-life-examples/))
- Creating these documents manually takes days and the result is usually a marketing brochure, not a procurement-ready asset
- This skill scans your actual codebase and generates documentation that reflects reality, including honest limitations

## What it produces

| Document | Audience | Key Features |
|----------|----------|-------------|
| Sales Datasheet | Executives, Buyers, Marketing | Persona filter chips, 3-layer depth per module, credibility metrics, CTA sections, limitations section |
| Technical Spec | CTOs, IT Managers, Infosec | "6 answers in 60s" header, architecture diagrams, data residency, API reference, security matrix, SLA with RPO/RTO, known gaps |

## Install

### Option A — Project-level (recommended)

Copy to your project's `.claude/skills/` directory:

```bash
mkdir -p .claude/skills/generate-datasheet
cp SKILL.md .claude/skills/generate-datasheet/
```

### Option B — Global (all projects)

```bash
mkdir -p ~/.claude/skills/generate-datasheet
cp SKILL.md ~/.claude/skills/generate-datasheet/
```

## Usage

In Claude Code, type:

```
/generate-datasheet
```

Or describe what you want:

```
Generate a sales datasheet and technical specification for this project
```

The skill will:
1. Scan your codebase (endpoints, tables, integrations, configs, docs)
2. Ask branding decisions (AI naming, audience, hidden providers)
3. Generate the sales datasheet HTML
4. Generate the technical spec HTML
5. Report what was included and what needs human input

## Design Philosophy

### Sales Datasheet
- **3 layers per module**: Title + value line (5s scan) → Feature bullets (30s read) → Technical accordion (deep dive)
- **Persona filters**: Chips dim irrelevant sections — doesn't hide, just guides the eye
- **Honest limitations**: Mandatory section. Builds more trust than hiding gaps.
- **AI branding**: External providers abstracted under proprietary brand (like HubSpot's "Breeze AI")

### Technical Spec
- **6 questions in 10 minutes**: Where does it run? How does data flow? How to integrate? What security exists? What are the SLAs? What must IT provision?
- **Status tags on everything**: Implemented (green) / Partial (amber) / Not available (gray)
- **Gaps section**: Brutally honest. Documents what's missing with ETAs.
- **Subprocessors table**: Exact data types and regions per external service

## Best Practices Applied

Based on research into how best-in-class B2B SaaS companies document their products:

| Company | What we learned |
|---------|----------------|
| Salesforce | Trust documentation structure: separate architecture/security/infrastructure |
| Rippling | Security datasheets: frameworks first, then plain language, then crypto details |
| Databricks | Security whitepapers: "designed for security teams to quickly review" |
| Stripe | Security pages: anticipate developer questions about fraud/encryption |
| 1Password | Walk through the security model step-by-step, not just "we're encrypted" |

## Output Examples

### Sales Datasheet
- Dark theme (almost black background, amber/blue accent)
- Space Grotesk headlines, Inter body text
- Sticky navigation with persona chips
- Accordion sections with chevron animation
- Print-friendly (white background, all sections expanded)

### Technical Spec
- Same dark theme, blue accent (distinguishes from sales doc)
- JetBrains Mono for code blocks and ASCII diagrams
- Status tags (Implemented / Partial / Not available)
- Callout boxes for warnings and important notes
- "Confidential — Evaluation use" classification

## License

MIT — Use freely, modify as needed, no attribution required.

## Credits

Created by [Objetiva Solucao Empresarial](https://objetivasolucao.com.br) for the SyneriumX project.
Methodology derived from Perplexity research on B2B SaaS documentation best practices (Salesforce, Rippling, Databricks, Stripe, 1Password, Freshworks).
