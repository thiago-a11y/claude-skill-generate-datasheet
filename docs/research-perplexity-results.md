# Pesquisas Perplexity — Resumo Consolidado

Pesquisas realizadas em 26/05/2026 para fundamentar a skill generate-datasheet.

---

## Pesquisa 1: Branding de IA em SaaS (Synerium AI)

**Pergunta:** Como empresas B2B SaaS brandificam features de IA?

**Resultado:**
- HubSpot → "Breeze AI", Salesforce → "Einstein", Freshworks → "Freddy AI", Zoho → "Zia", Monday → "monday AI"
- Nenhuma empresa lista providers (OpenAI, Anthropic, Google) em material de vendas
- Providers são revelados apenas em docs de segurança/privacidade ou docs de dev
- Best practice: usar nome proprietário em vendas, detalhar providers apenas em security docs

**Impacto na skill:** Seção 4 do PRD — toda IA sob marca proprietária do cliente. Tabela de substituição de providers por nomes genéricos.

---

## Pesquisa 2: Melhores práticas para ficha técnica SaaS

**Pergunta:** O que CTOs esperam ver? Quais são as queixas comuns?

**Resultado:**
- Documento deve responder 6 perguntas em <10 min: onde roda? como dados fluem? como integra? segurança? SLA? o que TI provisiona?
- 3 níveis de diagrama: contexto, container, componente
- Seção de segurança deve ser concreta (controles, não adjetivos)
- API: endpoints, auth, rate limits, webhooks, retry, versionamento
- SLA: uptime, RPO/RTO, severidades, créditos
- Queixas: docs muito promocionais, limitações escondidas, SLAs vagos, diagramas bonitos que não refletem realidade

**Impacto na skill:** Estrutura do Layer 3 (Technical Spec HTML) com 10 seções. "6 answers in 60 seconds" header.

---

## Pesquisa 3: O que TI pede antes de aprovar SaaS

**Pergunta:** Perguntas técnicas, motivos de rejeição, documentos exigidos.

**Resultado:**
- Clusters de perguntas: segurança/vendor risk, identidade/acesso, data handling, confiabilidade, APIs, arquitetura/isolamento
- Motivos de rejeição: documentação de segurança incompleta, sem SSO/SAML, integração fraca, data residency incerta, sem DR/backup
- Documentos exigidos: CAIQ/SIG preenchido, SOC2/ISO27001, DPA, SLA matrix, API reference, architecture proof
- Padrão: 1 PDF segurança + 1 diagrama arquitetura + 1 API page + 1 SLA page + 1 data residency

**Impacto na skill:** Security Pack (5 arquivos) + status tags (Implemented/Partial/Not Available) + gaps honestos.

---

## Pesquisa 4: Documentação exemplar em SaaS

**Pergunta:** Quais empresas têm a melhor documentação técnica?

**Resultado:**
- Stripe, Rippling, Databricks, Snowflake, Salesforce, 1Password, Auth0, Twilio
- Rippling: security datasheet com frameworks primeiro, depois plain language, depois crypto details
- Databricks: "designed for security teams to quickly review"
- 1Password: walk through do modelo criptográfico step-by-step
- Salesforce: separação clara de architecture/security/infrastructure
- Eficácia: scan-to-signal ratio alto, tradução tech→customer speak, proof visual, empower do champion interno

**Impacto na skill:** Modelo de 3 camadas por módulo (título → features → acordeão técnico). Persona filters.

---

## Pesquisa 5: Problema de documentação no vibe-coding

**Pergunta:** Quais docs faltam? Onde generators falham? Crise do vibe-coding?

**Resultado:**
- Docs mais ausentes: architecture.md, CONTRIBUTING.md, data-dictionary, ADRs, glossary, env setup guide, API examples
- Ferramentas falham em: diagramas automáticos, rationale de decisões, data dictionary, glossary, manutenção
- Vibe-coding: 70% do caminho rápido, 30% restante (incluindo docs) ignorado. Devs não entendem o que construíram
- Veracode 2025: chunks significativos de código AI-gerado com vulnerabilidades OWASP Top 10
- "A CULTURE OF DOCUMENTATION over box-checking behavior" (Stack Overflow)

**Impacto na skill:** Layer 1 completo (12 arquivos MD). Anti-hallucination protocol. Marcadores de incerteza.

---

## Pesquisa 6: Sugestões de evolução tecnológica

**Pergunta:** Alguma ferramenta gera "migrate from X to Y because Z" com evidência?

**Resultado:**
- Ferramentas existentes: Technical Debt Master (tdm), Claude Code /refactor-suggest, Stepsize AI, Refact.ai, OpenRewrite
- Nenhuma gera plano de migração com evidência do codebase
- SonarQube: "drowning in false positives", sem contexto de negócio, sem rationale
- CodeClimate: "users receiving data but not knowing what to do with it"
- Gap: nenhuma ferramenta combina doc + detecção + correção em um workflow

**Impacto na skill:** Layer 4 (Evolution Report) com Tech Radar format (Adopt/Trial/Assess/Hold). Migration cards com evidência.

---

## Pesquisa 7: Features ruptura de paradigma

**Pergunta:** O que faria a skill ser "can't go back"?

**Resultado:**
- Onboarding packs por role (Day 1/Week 1/Month 1) — ninguém faz bem
- Bus-factor report (git blame + churn + test coverage + criticality)
- Runbooks gerados de error handling no código (try/catch, retry, health endpoints)
- Project health score explicável (0-100 com 8 dimensões)
- Contract discovery entre módulos/serviços
- Cost-of-change estimates (coupling + tests + churn = esforço)
- Compliance narratives com evidence manifests
- Living delta briefs em cada PR/release
- Interactive architecture graph (visual frontend para todos os docs)
- "Safe change planner" — blast radius antes de mudar qualquer coisa

**Impacto na skill:** Layer 5 (Operational Intelligence) com 4 onboarding packs + bus-factor + runbooks + health score.

---

## Pesquisa 8: Scan → Fix com aprovação humana

**Pergunta:** Alguma ferramenta faz o ciclo completo scan→diagnose→propose→approve→fix?

**Resultado:**
- Closest: GitHub Copilot Autofix, Snyk Agent Fix, CodeRabbit Autofix, Dependabot
- Nenhuma faz o ciclo completo cross-codebase
- Snyk: não suporta fixes inter-file
- Dependabot: "incredibly noisy", "noise machine"
- Trust: branch dedicada, diff preview, dry-run, scope limits, rollback, verificação pós-fix
- Devs confiam em: lint/format auto-fix, patch deps. Não confiam em: architecture changes, auth, billing, migrations
- Gap: "trust orchestration" — explainable diagnosis, scoped proposals, approval UX, blast-radius, verification

**Impacto na skill:** Layer 6 (Correction Engine) com 12 safety rules, confidence labels, 1 fix = 1 commit, auto-revert se verificação falhar.

---

## Pesquisa 9: Enriquecimento + Monetização

**Pergunta:** O que mais falta no ecossistema? Como monetizar?

**Resultado:**
- Layers possíveis: SDK/Integration pack, Observability pack, Compliance questionnaire, Demo pack, Go-to-market pack, Training pack, Live health badges
- Nenhuma ferramenta faz repo → docs → health → observability → compliance → demo → sales collateral
- Monetização: freemium/open-core, hosted SaaS, usage-based, support/consulting, dual license
- Padrão que converte: OSS free para adoção → paid tiers para colaboração, hosting, compliance, governance, history
- Não existe marketplace oficial de Claude Code skills — distribuição via GitHub, blogs, social
- Revenue: GitHub Sponsors, Open Collective, Polar.sh, paid tiers
- Precedentes: GitLab, Sentry, PostHog, Elastic (OSS → empresa)

**Impacto na skill:** Roadmap v5 (SDK + Compliance + Badges), v6 (Observability + Demo + Training). Modelo SaaS futuro.
