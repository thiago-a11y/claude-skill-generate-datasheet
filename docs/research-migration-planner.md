# Pesquisa Perplexity — Migration Planner (C#/.NET → Web + ERP Integration)

Pesquisa realizada em 30/05/2026 para fundamentar feature de plano de migração no CodeDocs.

---

## O que existe

### Microsoft (oficial)
- **.NET Upgrade Assistant** — DEPRECATED (late 2025), substituído por GitHub Copilot App Modernization
- **Copilot App Modernization** — gera assessment.md + plan.md + commits sequenciais (requer AI/cloud)
- **.NET Portability Analyzer** — analisa compatibilidade de API
- **System.Web Adapters** — side-by-side Web Forms + moderno (Strangler Fig)

### Ferramentas de análise
- **CAST Highlight** — scan rápido, cloud readiness score, tech debt (caro, UI confusa)
- **NDepend** — qualidade de código, grafos de dependência
- **Roslyn Analyzers** — diagnósticos do compilador, regras customizáveis
- **Azure/AWS Migration Hub** — assessment de infra, não de código

### Gap confirmado
> Nenhuma ferramenta offline gera plano de migração file-by-file com esforço estimado, ordem de prioridade por risco de negócio, e plano de integração ERP.

---

## Queixas reais

### Timelines subestimados
- 70% dos rewrites falham ou excedem timelines significativamente
- Média de rewrite: 18-24 meses
- "Big rewrites of legacy applications will likely not get approval" (r/dotnet)

### Dependency hell (.NET Framework → .NET 8+)
- Dependências transitivas: "where migrations quietly go to die"
- System.Drawing é Windows-only — TypeLoadException no Linux/containers
- .NET Core não tem binding redirects — falhas silenciosas em produção

### Database (EF6 → EF Core)
- EF6 → EF Core é "conceptual break, not syntax change"
- Lazy loading explode sob carga (N+1 queries)
- Stored procedures com 400 linhas de business logic — sem extração automatizada

### UI rewrite
- WinForms: "tight coupling between UI & logic in btnSubmit_Click"
- Web Forms: ViewState, server controls não tem equivalente direto
- 40 horas/tela manualmente vs 4 horas/tela com reverse engineering visual
- Third-party controls (DevExpress, Telerik) sem equivalente Blazor

### Business logic perdida
- 67% dos sistemas legados não tem documentação
- "Code archaeology" — semanas rastreando event handlers
- Stored procedures com lógica de negócio trapped no banco

### ERP Integration
- TOTVS Protheus: customizações isoladas, alto custo, integrações falham
- SAP: auth complexa (OAuth/JWT), user ID entre hops é "very tricky"
- Oracle: REST/SOAP APIs exigem clients customizados

---

## O que seria ruptura de paradigma

1. **Visual reverse engineering** — gravar SME usando o sistema → extrair componentes, API contracts, data models (90% redução de custo: $1.6M → $160k para 200 telas)
2. **Business logic extraction de black boxes** — capturar input → output sem ler código
3. **Plano faseado com ordering + risk mitigations** — files affected + effort + ordem
4. **E2E test generation automática** — Playwright/Cypress do workflow legado
5. **Ghost feature detection** — 30% das features nunca são usadas, não migrar

---

## Melhores práticas de migração

### Strangler Fig Pattern (mais recomendado)
1. YARP reverse proxy entre legado e moderno
2. Migrar rota-por-rota, redirecionar tráfego
3. System.Web Adapters pra compartilhar session/auth
4. Rollback = mudança de config do proxy (< 1 min)

### Ordem de migração por risco
1. Read-only lookups (menor risco)
2. Admin pages internas
3. Transações revenue-critical (maior risco, por último)

### Priority Matrix (Value × Effort)
- **Quick Wins**: alto valor, baixo esforço → Phase 2
- **Major Projects**: alto valor, alto esforço → Phase 3-4
- **Fill-ins**: baixo valor, baixo esforço → Phase 2-3
- **Avoid**: baixo valor, alto esforço → não migrar

---

## Detecção de complexidade (static analysis)

### Sinais de bloqueio pra migração
| Pattern | Detecção | Impacto |
|---------|----------|---------|
| COM Interop | `DllImport("ole32.dll")`, TypeLib | Windows-only, precisa wrapper |
| P/Invoke | `[DllImport]`, kernel32.dll | Linux/containers blocked |
| System.Web | `HttpContext.Current` | Não existe no .NET Core |
| System.Drawing | `System.Drawing.Common` | Windows-only |
| EF6 EDMX | `.edmx`, ObjectContext | Substituir por EF Core Code-First |
| Stored Procedures | `CommandType.StoredProcedure` | Extrair lógica pra services |
| async void | event handlers com async void | Bug risk |

### Score de complexidade
```
Score = (CC × 2) + (Coupling × 1.5) + (Inheritance × 1) + (ExtDeps × 3) + (Interop × 5)

0-20: Low — conversão automática funciona
21-50: Medium — refactoring manual necessário
51+: High — redesign arquitetural antes de migrar
```

---

## Integração ERP — patterns recomendados

| ERP | Pattern | Motivo |
|-----|---------|--------|
| SAP ECC | OData (preferido) ou RFC/BAPI | OData: JSON, OAuth 2.0 moderno |
| TOTVS Protheus | TOTVS API Services REST + iPaaS | Padrão brasileiro, conectores prontos |
| Oracle ERP Cloud | REST API + Azure Logic Apps | REST layer completo, OAuth 2.0 |

### Arquitetura de integração
- **API Gateway**: centraliza auth e rate limiting (Kong, NGINX)
- **Middleware/iPaaS**: orquestração complexa multi-step
- **Event-Driven (Kafka)**: alto volume, desacoplamento
- **Anti-pattern**: point-to-point (n×(n-1)/2 conexões — insustentável)

---

## Output que CTOs confiam

| Componente | Formato | Por quê |
|-----------|---------|---------|
| Executive Summary | PDF (1-2 pgs) | Board-friendly |
| Roadmap detalhado | Markdown (GFM) | Versionável, buscável |
| Inventário de módulos | Excel/CSV | Filtrável, importável no Jira |
| Grafo de dependências | Mermaid + PNG | Visual pra apresentações |
| Estimativas de esforço | Excel (com fórmulas) | Editável pelo stakeholder |

---

## Impacto no CodeDocs

Essa pesquisa fundamenta a feature de "Migration Planner" no CodeDocs:

### Novos scans C# específicos
- Controllers MVC (`[HttpGet]`, `[Route]`, `Controller`)
- Entity Framework (DbContext, DbSet, .edmx, migrations)
- Views Razor/ASPX (.cshtml, .aspx)
- Configs (.csproj, web.config, appsettings.json, Startup.cs)
- Blockers (COM Interop, P/Invoke, System.Web, System.Drawing)
- NuGet dependencies (.csproj PackageReference, packages.config)

### Output do Migration Planner
1. **Complexity Score** por módulo (fórmula da pesquisa)
2. **Priority Matrix** (Value × Effort, 4 quadrantes)
3. **Phased Roadmap** (5 fases com timelines)
4. **Blocker Report** (COM, P/Invoke, System.Web, etc.)
5. **ERP Integration Plan** (SAP/TOTVS/Oracle patterns)
6. **Effort Estimates** (story points → horas)
7. **Dependency Graph** (Mermaid diagram)

### Referências
- Replay.build: visual reverse engineering methodology
- TYMIQ: 10 common mistakes .NET migration
- Platform.uno: Web Forms to modern .NET
- CAST Highlight: G2 reviews
- TOTVS API Services: tnusistemas.com.br
- SAP/Oracle integration: bobits.at, matthewswong.com
