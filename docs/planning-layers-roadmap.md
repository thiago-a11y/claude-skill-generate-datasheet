# Planejamento de Layers e Roadmap

## Estado Atual — v4.0

| Layer | Status | O que gera |
|-------|--------|-----------|
| 1 — Internal MD | Implementado | 12 arquivos: architecture, data-dictionary, glossary, changelog, endpoints, security, roadmap, contributing, bugs-known, backlog, pendencies |
| 2 — Sales HTML | Implementado | Ficha técnica com persona filters, 3 camadas, dark theme, CTAs |
| 3 — Technical HTML | Implementado | Escopo técnico: arquitetura, API, segurança, SLA, gaps |
| 4 — Evolution | Implementado | Tech radar, dependency audit, migrations, security gaps, test gaps, tech debt |
| 5 — Operational | Implementado | Onboarding packs (4 roles), bus-factor, runbooks, health score |
| 6 — Correction | Implementado | Scan → diagnose → propose → approve → fix → verify |
| Security Pack | Implementado | Whitepaper, data-residency, subprocessors, incident-response, backup-dr |

---

## v5.0 — Planejado

### Layer 7: SDK & Integration Pack
- Postman collection gerada dos endpoints detectados
- Integration guide por stack (React, Python, PHP, Node)
- Webhook recipes com exemplos de payload
- Auth setup guide (passo a passo de como autenticar)
- Fonte: endpoint scan + auth middleware analysis

### Compliance Questionnaire Pack
- Respostas CAIQ pré-preenchidas com evidência do código
- Respostas SIG/SIG-Lite pré-preenchidas
- Evidence manifest (JSON com links para file:line de cada controle)
- "Unsupported claims" — o que NÃO pode ser provado pelo código
- Fonte: security scan + audit log + encryption + headers

### Live Health Badges
- Badges dinâmicas para README baseadas no health score real
- Dimensões: test coverage, dependency freshness, doc coverage, bus factor
- Formato: shields.io compatible ou SVG inline
- Atualiza em cada run da skill

---

## v6.0 — Futuro

### Layer 8: Observability Pack
- Dashboard configs (Grafana JSON / Datadog YAML) gerados de health endpoints
- Alert rules baseadas em error patterns no código
- SLI/SLO suggestions de uptime/latency/error rate
- Runbook linkado a cada alerta
- Fonte: health endpoints + error handling + cron jobs + external calls

### Demo & Walkthrough Pack
- Roteiro de demo descoberto das rotas e user flows
- CLI walkthrough script (comandos para demonstrar features)
- Feature tour com screenshots placeholders
- Seeded data suggestions para demo environment
- Fonte: routes + UI components + fixtures/seeds

### Training Pack
- Material de treinamento por role (slides outline)
- Voiceover scripts para vídeos de treinamento
- Support playbook (perguntas frequentes mapeadas do código)
- Partner enablement guide
- Fonte: onboarding packs + docs + glossary + API reference

---

## SaaS — Modelo de Negócio Futuro

### Free Tier (CLI/Skill)
- Tudo que a skill faz hoje (Layers 1-6 + Security Pack)
- Roda local, sem dependências
- MIT licensed

### Pro Tier (Hosted)
- Upload repo ou connect GitHub
- Dashboard web com histórico de scans
- Comparação de architectural drift entre versões
- Export PDF profissional dos HTMLs
- Badges dinâmicas hospedadas

### Team Tier
- Múltiplos repos
- Approval workflows para Layer 6 (corrections)
- Templates customizados por empresa
- Compliance questionnaire library (CAIQ, SIG, VSA, HECVAT)

### Enterprise Tier
- Private templates e branding
- Evidence retention para auditorias
- Integração CI/CD (GitHub Actions, GitLab CI)
- SSO/SAML para dashboard
- SLA garantido
- Custom export formats

---

## Priorização de Novas Skills (repo multi-skill)

| Skill | Descrição | Prioridade |
|-------|-----------|-----------|
| `generate-datasheet` | A skill principal — docs + ops + fix | Ativa (v4.0) |
| `generate-api-client` | SDK + Postman + integration guides | Alta — v5.0 |
| `generate-compliance` | CAIQ/SIG/GDPR questionnaire answers | Alta — v5.0 |
| `generate-observability` | Dashboards + alerts + SLOs | Média — v6.0 |
| `generate-demo` | Roteiros + walkthroughs + seed data | Média — v6.0 |
| `generate-training` | Material de treinamento por role | Baixa — v6.0 |
| `health-badges` | Badges dinâmicas para README | Alta — v5.0 |

---

## Referências

Todas as decisões acima baseadas em 9 pesquisas Perplexity documentadas em `docs/research-perplexity-results.md`:
- Branding de IA em SaaS (HubSpot, Salesforce, Freshworks)
- Melhores práticas de ficha técnica B2B
- Requisitos de TI para procurement
- Documentação exemplar (Stripe, Rippling, Databricks)
- Crise do vibe-coding
- Evolução tecnológica e tech debt
- Features ruptura de paradigma
- Scan → Fix com aprovação
- Enriquecimento + Monetização
