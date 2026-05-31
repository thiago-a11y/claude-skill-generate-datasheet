# Pesquisa Perplexity — Offline Documentation Tool (Air-gapped, LLM-free)

Pesquisa realizada em 30/05/2026 para fundamentar o app offline de documentação.

---

## Pergunta 1: Ferramentas offline existentes e queixas

### O que existe
- **Comment-to-API**: Doxygen, Javadoc, Sphinx/autodoc, Typedoc, Compodoc — geram refs de API, não docs operacionais
- **Arquitetura**: Structurizr, Dependency-Cruiser, Madge, Understand, NDepend — grafos de dependência, não "o que o sistema faz"
- **Extração profunda**: Sphinx autodoc, NDepend reports — mais que API docs mas ainda code-centric

### Queixas recorrentes (Reddit, HN)
- "Documentam o que o código já diz, não o que humanos precisam saber"
- Doxygen/Sphinx: noisy, literal demais, depende de comments disciplinados
- Ferramentas de arquitetura: diagramas difíceis de manter, não explicam comportamento do sistema
- NDepend: foca em qualidade de código e dependências, não em documentação completa

### O que NENHUMA ferramenta offline gera
- Data dictionary com definições de negócio, ownership, sensibilidade
- Security posture / threat model / controles
- Onboarding guides (workflows, deploy, setup, failure modes)
- Sales datasheets / implementation guides / "why this product matters"
- Specs operacionais end-to-end (código + DB + integrações + usuários + processos)

### Gap fundamental
> "Ferramentas estáticas extraem SINTAXE (classes, métodos, imports, schemas).
>  Não extraem INTENÇÃO (vocabulário de domínio, permissões, data ownership, compliance, valor pro cliente)."

---

## Pergunta 2: O que seria divisor de águas / ruptura de paradigma

### Category-defining = "SonarQube of Documentation"
- Todo scan é reproduzível (mesmo código → mesmo output, mesmo hash)
- Todo campo é rastreável (cada claim aponta pra código, migration, config, test)
- Security teams aprovam numa reunião só (zero data egress by design)

### O que faz devs dizerem "não tem volta"
1. **One-pass, multi-audience**: técnico + vendas + segurança + dev, tudo do mesmo scan
2. **Traceability sem IA**: click em qualquer campo → vai pro code
3. **Quality gates pra docs**: bloqueia merge se doc não atinge threshold (como SonarQube)
4. **Doc health score como KPI**: sobe quando docs melhoram, cai quando código muda sem docs
5. **IDE + CI integration**: feedback onde dev já trabalha

### O que faz security teams aprovarem instantaneamente
1. **Zero egress by design**: sem network calls, sem telemetria, sem cloud
2. **Audit trail completo**: manifest (arquivos, versões, checksums), report hash, logs
3. **Compliance-aligned**: outputs mapeiam pra SOC 2, HIPAA, ITAR, FedRAMP, ISO 27001, CMMC
4. **No black box**: regras de parsing documentadas, customizáveis, determinísticas
5. **Air-gapped capable**: instala via USB/artifact repo, zero internet pós-instalação

### O que indústrias compliance-heavy precisam
| Indústria | Necessidade |
|-----------|------------|
| Financeiro | Audit-ready, data flows, access controls, dependency chain |
| Saúde | HIPAA (PHI fields), encryption, audit logging, incident response |
| Defesa | ITAR (technical data classification, export control, access logs) |
| Industrial | Arquitetura + integrações MES/ERP, data dictionary, dependency audit |

### Gaps das ferramentas atuais (nenhuma resolve)
| Gap | Impacto |
|-----|---------|
| No sales-ready docs | Ferramentas param em API refs e diagramas |
| No security controls matrix | Postura de segurança é inferida manualmente |
| No data dictionary de migrations | Schema docs existem, mas sem PHI/PII tags |
| No health score | Sem métrica composta de completude |
| Weak traceability | Docs estáticas, sem link pra código |
| No quality gates | Documentação não é enforced em CI |
| Poor compliance alignment | Reports não mapeiam pra SOC 2, HIPAA, ITAR |
| No multi-audience output | Mesmo scan não produz docs pra tech, security e sales |

---

## Pergunta 3: Melhores práticas para o app

### Parsing: estratégia híbrida recomendada
1. **Regex/grep** (MVP): rápido, zero deps, padrões por linguagem
2. **Tree-sitter** (futuro): AST preciso, multi-linguagem, robusto
3. **Fallback gracioso**: se parser falha, gera docs com menor precisão

### Stack recomendada (Python)
- **CLI**: click ou typer
- **Parsing**: regex patterns por linguagem (fallback) + tree-sitter (opcional)
- **Templates**: Jinja2 (bundled)
- **UX**: rich (progress bars, cores, tabelas) + questionary (prompts interativos)
- **Output**: HTML multi-arquivo com index.html, dark/light theme, print CSS
- **Distribuição**: PyInstaller single binary (primário) > pip > Docker > homebrew

### UX patterns que fazem diferença
- Progress bars com X/Y (não spinners genéricos)
- Cores: verde=ok, amarelo=warning, vermelho=crítico
- Auto-open do HTML no browser após scan
- Error messages que guiam ("não achou package.json? tente --language=python")
- `--help` com exemplos concretos

### Distribuição
| Canal | Público | Air-gapped? |
|-------|---------|-------------|
| Single binary (PyInstaller) | Enterprise/industrial | Sim |
| pip install | Python devs | Não (ou mirror interno) |
| Docker | CI/CD | Parcial |
| Homebrew | macOS devs | Não |

### Como ferramentas maduras lidam com offline
- **Trivy**: `--offline-scan`, `--skip-db-update`, DB pré-baixado via USB
- **Semgrep**: `--metrics=off`, regras locais em `.semgrep.yaml`
- **Snyk CLI**: auth via token, configurável pra ambientes restritos
- **SonarScanner**: self-hosted server dentro da rede

### Padrões de ferramentas de sucesso pra adotar
| Ferramenta | Pattern | Aplicação |
|-----------|---------|-----------|
| SonarQube | Quality Gates | Bloqueia merge se doc score cai |
| SonarQube | New Code focus | Enforce em código novo primeiro |
| Snyk | Fix over find | Sugere como documentar, não só lista gaps |
| Terraform | Plan/apply | `doc plan` mostra diff, `doc apply` atualiza |
| Backstage | Software catalog | Portal local com componentes, owners, APIs |

---

## Impacto no produto

Essa pesquisa fundamenta o app offline como produto standalone:
- **Posicionamento**: "SonarQube of Documentation" — offline, determinístico, audit-ready
- **Diferencial**: nenhuma ferramenta gera sales + tech + security docs num único scan offline
- **Mercado**: indústrias compliance-heavy (finanças, saúde, defesa, industrial) que não podem usar LLM
- **Stack**: Python + Jinja2 + rich + regex + PyInstaller
- **MVP**: regex-based, single binary, HTML output com dark/light theme
- **Futuro**: tree-sitter pra parsing, quality gates em CI, IDE integration

### Nome candidato: CodeDocs / DocForge / CodeRadar

### Referências
- Trivy air-gap: trivy.dev/docs/latest/advanced/air-gap
- Semgrep offline: github.com/semgrep/semgrep/issues/8793
- Structurizr: structurizr.com
- SonarQube adoption: community.sonarsource.com
- ITAR compliance: preveil.com/blog/itar-compliance
- Air-gapped AI governance: getmaxim.ai
- CLI UX: evilmartians.com/chronicles/cli-ux-best-practices
