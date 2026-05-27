# Pesquisa Perplexity — AI API Cost Audit (Static Code Analysis)

Pesquisa realizada em 27/05/2026 para fundamentar nova feature de auditoria de custos de IA.

---

## Pergunta Central

Existe ferramenta que faz análise estática de código para identificar chamadas de LLM, mapear modelos usados, e recomendar modelos mais baratos para tarefas simples?

## Resultado: Lacuna Confirmada

**Não existe ferramenta madura open-source** que faz análise estática de código especificamente para inferir "este code path usa GPT-4/Claude Opus/Gemini Pro e deveria ser rebaixado para tarefas simples."

Ferramentas existentes focam em **runtime observability**, não em análise do código-fonte.

---

## O que existe hoje

### Observabilidade LLM (Runtime)
| Ferramenta | O que faz | O que NÃO faz |
|-----------|-----------|---------------|
| **Langfuse** | Tracing, analytics, custo por token, latência | Não escaneia código-fonte |
| **Helicone** | Logging de requests, custo, experimentação de prompts | Não analisa callsites no repo |
| **LangSmith** | Debugging e tracing para LangChain | Visibilidade runtime apenas |
| **Portkey** | AI gateway + observability + routing + caching | Forte em runtime, não em static scan |
| **PostHog AI** | Tracking de modelo, custo, spans, traces | Telemetria runtime |

### AI Gateways / Routing (Runtime)
| Ferramenta | Routing | Static Analysis |
|-----------|---------|-----------------|
| **LiteLLM** | Cost-based, auto routing, complexity router | Não escaneia repo |
| **Portkey Gateway** | Conditional routing, load balancing | Não gera migration plans do código |
| **Martian** | Dynamic model router por prompt | Não faz audit de callsites |
| **Not Diamond** | Routing por query com otimização cost/quality/latency | Não escaneia codebase |
| **Unify.ai** | Otimização de model choice | Sem code analysis |

### Gap
> "The practical gap is that today's platforms mostly detect and optimize **what actually ran**, not what the source code *could* be routed to more cheaply before execution."

---

## Queixas reais de usuários

| Fonte | Queixa | Detalhe |
|-------|--------|---------|
| r/mlops | "$3.2K LLM bill — 68% was preventable waste" | 68% queries repetidas sem cache, 22% staging usando prod keys |
| r/CLine | "AI Billing Horror Show" — $2K overnight | Token costs escalam, alertas inexistentes |
| r/LLMDevs | "Bill spikes and I don't know which project caused it" | Zero visibilidade por modelo/projeto |
| Hacker News | "Monthly Claude bill nearly 3x our SaaS cloud spend" | Cortando gasto com modelos reasoning |
| Hacker News | "Agents retry more than they should, bill goes up" | Aggregate usage, sem breakdown |
| Dev blog | "60% of requests handled by smaller model = wasting money" | GPT-4 $0.03/1K vs smaller $0.001/1K |

### Problemas centrais
1. **Sem visibilidade** — billing agregado não quebra por agent/task/feature
2. **Modelos caros para tarefas simples** — 60-80% das tasks poderiam usar modelos 10-100x mais baratos
3. **Agent loops/retries** — queimam dinheiro sem controle
4. **Staging usando prod keys** — dev environments batendo na API real
5. **Waste semântico** — mesmas perguntas diferentes batendo API toda vez

---

## Savings típicos

| Estratégia | Economia | Condição |
|-----------|----------|----------|
| Model routing sozinho | 40-70% | 60% requests roteadas para modelo 5x mais barato |
| Routing + caching | 70-85% | Context-heavy workflows com compactação |
| RouteLLM research | 45-85% | 85% queries para modelo barato, 95% qualidade mantida |
| Simple → smaller model | 5-10x por token | Classification, extraction, sentiment |
| Three-tier routing | 30-50% | 60% cheap, 30% medium, 10% large |
| Fine-tuned 7B vs GPT-4 | ~10x menos por token | High-volume use cases |

> **Key insight**: Frontier models (Opus, GPT-4) custam ~5x mais por token que variantes eficientes (Haiku, GPT-4o-mini). Roteie 60-80% das queries para modelos baratos e corte 40-70% dos custos mantendo 95% de qualidade.

---

## O que a análise estática PODE fazer (80%)

- Encontrar onde APIs OpenAI/Anthropic/Google são chamadas
- Mapear quais modelos são hardcoded ou defaulted
- Identificar callsites candidatos a routing mais barato
- Flaggar padrões óbvios: "classification", "summarization", "formatting" que não precisam de frontier

## O que NÃO pode (20%)

- Julgar complexidade da task só pelo código
- Saber impacto business de outputs de menor qualidade
- Entender prompt length dinâmico, tool calls, model selection dinâmico
- Recomendar swaps seguros sem evals runtime ou human review

---

## Formato ideal de output

### Detecções necessárias
- SDK calls: `client.chat.completions.create()`, `anthropic.messages.create()`, `google.generativeai`
- HTTP patterns: `fetch`, `axios`, `requests` para endpoints de LLM
- Wrappers: `llm.generate()`, `runPrompt()`, `askModel()`, abstrações LangChain/LiteLLM/Vercel AI

### Evidência por callsite
- File:line
- Expressão exata que seleciona o modelo
- Fonte upstream (`.env`, config, feature flag, hardcoded)
- Modelo efetivo resolvido
- Confidence label (resolved / partially resolved / unknown)

### Recomendação ideal
```
Switch src/agents/title.ts:42 from gpt-4o to gpt-4o-mini
- Prompt is short, temperature-low, schema-constrained
- Estimated savings: 55-70% at current traffic
- Validate on 500 historical samples before rollout
- Confidence: HIGH
- Quality risk: LOW
```

### Opportunity Score
```
Score = Savings Potential × Confidence × Traffic Share × (1 - Quality Risk)
```

---

## Trust signals (o que faz devs confiarem)

**Constrói confiança:**
- Evidência exata (file:line, snippet, modelo resolvido)
- Heurísticas explicáveis ("downgrade porque prompt é curto, schema-bound, low temperature")
- Replay/shadow evals em prompts históricos
- Quality guardrails (pass/fail, regressão, rollback)
- Linguagem conservadora ("estimated", "confidence", "validate")
- Integração com logs reais (Portkey, LiteLLM, OpenTelemetry)

**Destrói confiança:**
- Regex-only scans que perdem wrappers
- Estimativas de custo sem premissas explícitas
- Recomendações que ignoram latência/retries/quality risk
- "One-click downgrade" sem evals ou rollback

---

## Product wedge

> "The first trustworthy AI cost/code auditor that explains where every model decision lives and turns optimization into an engineering change-management flow."

> Tagline: "Find every LLM call, prove what model it uses, simulate cheaper alternatives, and ship safe migrations."

Whitespace: "Portkey/LiteLLM observability, but shifted left into the repo with code evidence and prescriptive migration planning."

---

## Impacto na skill

Essa pesquisa fundamenta uma nova capacidade para o generate-datasheet ou skill separada:
- **Scan estático** de callsites LLM com file:line evidence
- **Inventário de modelos** usados com custo estimado
- **Recomendações de downgrade** com confidence labels e blast radius
- **Migration plan** com diff preview e rollback instructions
- Integra com Layer 6 (Correction Engine) para aplicar mudanças com aprovação

### Referências
- Langfuse: langfuse.com/docs/observability/features/token-and-cost-tracking
- Helicone: helicone.ai/blog/monitor-and-optimize-llm-costs
- Portkey: portkey.ai/features/ai-gateway
- LiteLLM: docs.litellm.ai/docs/routing
- Not Diamond: docs.notdiamond.ai/docs/what-is-model-routing
- Martian: diginomica.com/martian-model-router-jumpstarts-ai-cost-optimization
- r/mlops: "$3.2K bill" thread
- Hacker News: "Claude bill 3x cloud spend" thread
