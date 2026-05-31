# Pesquisa Perplexity — Migration Equivalences & Competitive Analysis

Pesquisa realizada em 30/05/2026 para fundamentar feature de mapeamento de equivalências e seleção de target.

---

## Concorrentes e o que fazem

| Ferramenta | O que faz | Cross-stack? | Offline? | Preço |
|-----------|-----------|-------------|---------|-------|
| GitHub Copilot App Modernization | .NET 8→10, Java upgrades, plan.md + commits | Não | Não | $39-50/user/mês |
| OpenRewrite / Moderne.io | Recipes determinísticas (5000+), Java focused | Não | Parcial | Enterprise opaco |
| Mobilize.Net / GapVelocityAI | VB6 → C#/.NET, side-by-side code | Parcial (VB6→C#) | Não | Comercial |
| IBM watsonx Code Assistant | COBOL → Java (mainframe) | Parcial (COBOL→Java) | Não | Enterprise |
| CAST Highlight | Cloud readiness score, tech debt | Não | Não | $50K-150K/ano |
| AWS Migration Hub | Assessment + orchestração multi-team | Não | Não | $100K-500K |
| Konveyor (Red Hat) | Java EE → Quarkus, rules-based | Não | Sim | Open source |

### Gap confirmado
> **NENHUMA ferramenta faz cross-stack migration offline** (Razor→React, EF→Prisma, MVC→FastAPI)

---

## Queixas reais

### Copilot App Modernization
- "Huge downgrade" do .NET Upgrade Assistant grátis — agora requer Copilot pago
- "Spend more time fighting suggestions than coding" (r/dotnet)
- 50+ cliques de "Confirm" durante upgrade

### CAST Highlight
- Caro pra SMBs, UI confusa, SBOM reporting inadequado
- "Only assessment — no code generation" — users querem código, não score

### AI COBOL→Java
- "Java code read like assembler" — código gerado ilegível
- 70-80% falham porque IA não "enxerga" estrutura em arquivos longos
- "Lost in the Middle" effect

### Geral
- 70% dos rewrites falham ou excedem timelines
- 60% dos "big bang" rewrites falham
- $75B desperdiçados anualmente em migrações cloud que passam do orçamento

---

## Tabela de equivalências (accuracy rates)

### Conversões seguras (90%+ accuracy)
- Route decorators (MVC → FastAPI/Express/Gin): 95%
- ORM models (EF → Prisma/SQLAlchemy/GORM): 95%
- Validation (FluentValidation → Pydantic/Joi/validator): 95%
- Config (web.config → .env/appsettings): 95%
- NuGet → npm/pip/go equivalents: 95%
- Razor loops/conditionals → React JSX: 95%

### Conversões médias (70-85%)
- Auth middleware: 80%
- DI patterns: 85%
- Form helpers (Html.TextBoxFor → React input): 70%
- Ajax calls → fetch/axios: 75%
- DataGridView → AG Grid/React Table: 75%
- Transactions: 80%

### Conversões que exigem humano (50-70%)
- Stored Procedures → service layer: 60-70%
- COM Interop → gRPC/REST: 50-60%
- EDMX → Code-First: 70%
- BackgroundWorker → Web Worker: 70%
- File System Access (desktop → web): 60%

---

## O que seria imbatível (holy grail)

1. **Cross-stack code mapping** — Razor→React, EF→Prisma, MVC→FastAPI com side-by-side diff
2. **Skeleton code gerado** — não "código pronto" mas templates populados do target
3. **Accuracy labels** por conversão — GREEN (95%+) / YELLOW (70-85%) / RED (50-70%)
4. **Interactive target selection** — scan → perfil do codebase → recomendação de target
5. **Architecture comparison** — diagrama current vs target lado a lado
6. **Test plan por fase** — o que validar depois de cada módulo migrado
7. **Effort calibration** — story points × velocity da equipe

### Vantagem competitiva do CodeDocs
| Dimensão | Concorrentes | CodeDocs |
|----------|-------------|----------|
| Targets | Same-language (.NET 8→10) | Cross-stack (Razor→React, EF→Prisma) |
| Code generation | Plan + auto-fixes (Copilot) | Skeleton + equivalence map + tests |
| Effort estimates | Person-days genéricos (CAST) | File-by-file com confidence ranges |
| Deploy | Cloud/AI required | 100% offline, zero data egress |
| Preço | $100K-500K/ano | $5K-20K one-time |
| Output | PDF assessment | Markdown + CSV + Mermaid + HTML |

### CTO buy-in statement
> "Analisamos 15 ferramentas de migração. CodeDocs é a única que gera mapeamento cross-stack (Razor→React, EF→Prisma) com estimativas calibradas e 90% redução de custo. É offline (LGPD-compliant) e custa 90% menos que CAST Highlight."

---

## Equivalência de pacotes (NuGet → npm/pip/go)

| Categoria | NuGet | npm | pip | go |
|----------|-------|-----|-----|-----|
| Auth | JwtBearer | jsonwebtoken | PyJWT | golang-jwt |
| Logging | Serilog | winston | loguru | logrus |
| ORM | EntityFramework | prisma | SQLAlchemy | gorm |
| HTTP Client | HttpClient | axios | httpx | net/http |
| Testing | xUnit | jest | pytest | testing |
| Caching | Memory Cache | node-cache | redis-py | go-redis |
| Messaging | Azure.ServiceBus | kafkajs | aiokafka | kafka-go |
| Validation | FluentValidation | joi | pydantic | validator |
| Mapping | AutoMapper | class-transformer | pydantic | copier |
| Background Jobs | Hangfire | bull | celery | robfig/cron |

---

## Referências
- OpenRewrite: moderne.ai/openrewrite
- Mobilize.Net: legacyleap.ai, github.com/MobilizeNet/VBMigration
- Copilot App Modernization: learn.microsoft.com
- CAST Highlight: g2.com/products/cast-highlight
- Replay.build: visual reverse engineering methodology
- IBM watsonx: ibm.com/docs/watsonx
- Prisma: prisma.io/docs/orm/prisma-migrate
