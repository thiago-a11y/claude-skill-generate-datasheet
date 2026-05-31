# Feedback: Perplexity Review #2 — "Ferrari com painel de Gol 96"

Review realizada em 31/05/2026 — segunda rodada após correções.

## Veredito

> "Motor de Fórmula 1, mas ainda jogando log bruto na cara do cliente."
> "Você claramente não é amador; o amadorismo é de copy/UX de saída, não de arquitetura."

## O que melhorou (reconhecido)
- Sales datasheet agora lista limitações reais (testes 0%, bus factor, SLA) ✓
- Health score caiu de 67 → 48 (mais honesto) ✓
- Migration planner com módulos por risco/esforço é "o que consultoria enterprise cobra" ✓
- Base de evidências é nível sênior ✓

## 3 cortes cirúrgicos pra nível enterprise

### Corte 1: Health Score → Risk Score
- Renomear "Health Score" para "Risk Score" ou "Operational Risk Score"
- Peso brutal: testes (40%), bus factor (20%), deprecated tech (15%)
- Menos peso: docs, deps frontend, número de endpoints
- Se 0 testes → score cai pra 20-30/100
- Narrativa: "sistema funcional, porém com risco operacional alto"

### Corte 2: Acabar com placeholders genéricos
- "Requires organizational input" → contextualizado por seção:
  - Hosting: "Hosting details depend on client infrastructure. Typical options: cPanel shared, VPS, Docker, cloud PaaS."
  - SLA: "SLA terms require business agreement. Industry standard for B2B SaaS: 99.5% uptime, 4h RPO, 1h RTO."
  - Commercial: "Pricing model requires business decision. Common models: per-seat, per-company, flat fee + usage."
- "No significant gaps detected" → NUNCA usar. Sempre listar gaps reais.
- NOT DETECTED → explicar se é "não existe" ou "scanner não conseguiu verificar"

### Corte 3: Opinião forte + recomendação default
- Migration plan: recomendar 1 target baseado no stack detectado
  - PHP+TS → "Recommended: keep TypeScript frontend, migrate PHP to Node/NestJS (single language)"
  - C# MVC → "Recommended: Blazor for C#-only teams, React+FastAPI for greenfield"
  - Java Spring → "Recommended: keep Java, upgrade Spring Boot"
- Tech spec: marcar "pontos sensíveis LGPD" e "o que auditor pergunta primeiro"
- Sales datasheet: abrir com output ("Em 48h entregamos: risk score, mapa de riscos, plano 5 fases, esforço em horas"), não com motor
