# Feedback: Perplexity Review dos HTMLs do CodeDocs (SyneriumX)

Review realizada em 31/05/2026 — Perplexity analisou os 4 HTMLs + CONTEXT.md.

---

## Problemas críticos (matam credibilidade)

### 1. Health score otimista demais
- 67/100 com 0 testes em 1071 arquivos parece "bonito no resumo"
- Zero testes deveria derrubar a nota de forma brutal e visível
- Scores individuais (100/100 docs, 100/100 security) mascaram o problema

### 2. "No significant gaps detected" contradiz o technical spec
- Sales datasheet diz "sem gaps"
- Technical spec lista gaps reais (SLA, hosting, infra requirements vazios)
- Divergência destrói confiança

### 3. Migration plan: 0 critical blockers mas lista PHP_DEPRECATED e PHP_RAW_SQL
- Blockers estão listados mas não contam como "critical"
- Parece cálculo superficial ou regra mal calibrada

### 4. Placeholders [MANUAL] parecem relatório bruto
- Hosting, SLA, RPO/RTO todos vazios com [MANUAL]
- Deveria transformar em "Requires Input" com contexto claro
- Parece dump de scanner, não documento final

### 5. Sales datasheet é espelho do scan, não peça de vendas
- Sem proposta de valor, diferenciação, narrativa persuasiva
- Métricas técnicas sem contexto de negócio
- Limitações negam problemas em vez de explicá-los

### 6. "6 answers in 60 seconds" com respostas vazias
- Hosting, SLA, IT requirements ficam em branco
- Promessa de maturidade maior do que a evidência suporta

### 7. Migration plan genérico demais
- Mostra 6 plataformas sem recomendar uma baseada no perfil do codebase
- Não fica claro qual critério decide qual caminho seguir

## O que está bom

- Base de evidências forte (endpoints, tabelas, integrações, commits)
- Números concretos (341 endpoints, 54 tabelas, 18 integrações, 771 commits)
- Estrutura de módulos por risco/esforço é boa
- Rastreabilidade file:line funciona

## Veredito

> "O material transmite competência técnica, mas também transmite 'gerado por ferramenta'.
> O problema não é falta de informação — é falta de curadoria, hierarquia e honestidade
> editorial entre o que foi encontrado, o que foi inferido e o que precisa ser validado."

## Correções necessárias (priorizadas)

1. Health score: penalizar MUITO mais por 0 testes, adicionar banner de warning
2. Sales datasheet: SEMPRE mostrar gaps reais (testes, bus factor), nunca "no significant gaps"
3. Technical spec: preencher "6 answers" do scan data, trocar [MANUAL] por linguagem profissional
4. Migration plan: PHP_DEPRECATED/PHP_RAW_SQL devem contar como blockers, recomendar best-fit target
5. Consistência cross-document: mesma linguagem de status em todos os 4 HTMLs
6. Separar scan técnico de material comercial: sales datasheet precisa de narrativa, não dump
7. Trocar placeholders por linguagem executiva clara
