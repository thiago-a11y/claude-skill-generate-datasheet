# CodeDocs Desktop — Design Spec

## Resumo

App desktop offline para Windows e Mac que empacota o CodeDocs (Python CLI) numa interface gráfica para gestores não-técnicos. O usuário arrasta uma pasta de projeto, o app escaneia e mostra os 5 documentos em abas navegáveis, com export PDF.

Modelo freemium: Scan Report + Decision Brief grátis. Migration Plan, Technical Spec e Sales Datasheet requerem licença Pro.

## Público-alvo

Gestor não-técnico (diretor, gerente, CTO não-hands-on) que precisa entender o estado de um sistema sem saber programar. Não usa terminal. Espera experiência de "arrastar e usar".

## Lacuna de mercado (validada por pesquisa)

Nenhuma ferramenta existente combina:
- Scan 100% offline (sem cloud, sem IA, sem egresso de dados)
- Outputs executivos (risk score, migration plan, decision brief)
- Formato de consultoria (não dashboard de dev)

SonarQube e CodeScene são os mais próximos mas param na camada de achados técnicos. A "camada de síntese" — transformar scan em recomendação executiva — é domínio de consultores humanos. CodeDocs já faz isso. O app desktop é o empacotamento para distribuição.

## Stack

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Shell | Electron | Ecossistema maduro, PDF export nativo via Chromium, .exe/.dmg com electron-builder |
| UI | React + TypeScript | Stack que o time já domina, maior ecossistema de componentes |
| Engine | Python (PyInstaller) | CodeDocs já é Python, empacota como executável standalone sem dependência de Python instalado |
| Comunicação | IPC (Electron) + stdio (Python) | Renderer → IPC → Main → stdin/stdout → Python sidecar |
| Licença | Ed25519 signed JWT | Verificação local com chave pública embutida, sem internet |
| Update | electron-updater | Auto-update diferencial, canais stable/beta |

## Arquitetura

```
┌─────────────────────────────────────────────┐
│           Electron (Main Process)           │
│  - Gerencia janela e ciclo de vida          │
│  - Lança Python sidecar como child process  │
│  - IPC bridge (renderer ↔ Python)           │
│  - Auto-update (electron-updater)           │
│  - Licença local (Ed25519 verify)           │
└──────────┬───────────────┬──────────────────┘
           │               │
     IPC Bridge      Spawn + stdio
           │               │
┌──────────▼──┐    ┌───────▼──────────────────┐
│  Renderer   │    │  Python Sidecar          │
│  (React)    │    │  - codedocs.scanner       │
│  - Drop zone│    │  - codedocs.renderer      │
│  - Progress │    │  - codedocs.migration     │
│  - Tab view │    │  - codedocs.i18n          │
│  - PDF btn  │    │  - JSON via stdout/stdin  │
└─────────────┘    └──────────────────────────┘
```

### Regras de segurança do sidecar
- Renderer nunca spawna Python diretamente — só via IPC para Main.
- Python só escuta em stdin, nunca abre porta HTTP.
- stderr vai para arquivo de log, não é contrato de API.
- Main impõe timeout de 5 minutos no scan. Fallback: tela de erro com "Tentar novamente".
- Python sidecar é versionado junto com o app (atômico).

### Protocolo de comunicação (Main ↔ Python)

Main envia via stdin:
```json
{
  "command": "scan",
  "path": "/Users/thiago/propostasap",
  "options": {
    "lang": "pt-BR",
    "target": "react-node",
    "name": "PropostaSAP"
  }
}
```

Python responde via stdout (uma linha JSON por evento):
```json
{"type": "progress", "step": 5, "total": 19, "label": "Analisando endpoints"}
{"type": "progress", "step": 19, "total": 19, "label": "Concluído"}
{"type": "result", "files": {"scan-report": "<html>...", "decision-brief": "<html>...", ...}}
```

Main repassa para o Renderer via IPC.

## Fluxo de telas (3 telas)

### Tela 1 — Drop Zone (estado inicial)

- Área de drop ocupa a janela inteira.
- Aceita drag-and-drop de pasta ou clique para selecionar via dialog nativo.
- Mostra badges das linguagens suportadas (PHP, TypeScript, Python, Java, C#).
- Footer: versão do app + indicador Free/Pro.
- Frase de confiança: "100% offline · Zero IA · Seus dados nunca saem do computador".

### Tela 2 — Progresso (scanning)

- Nome do projeto + caminho detectados.
- Barra de progresso determinada (step/total do scanner).
- Lista de etapas com checkmarks:
  - ✅ Detectando linguagens — N arquivos
  - ✅ Escaneando endpoints — N detectados
  - ⏳ Etapa atual...
  - ○ Etapas pendentes
- Sem botão de cancelar no MVP (simplificação).

### Tela 3 — Resultados (documentos)

- Barra de abas no topo:
  - 📊 Decision Brief (free)
  - 📋 Scan Report (free)
  - 🔧 Tech Spec (🔒 Pro)
  - 📈 Migration Plan (🔒 Pro)
  - 📄 Sales Datasheet (🔒 Pro)
- Aba ativa renderiza o HTML do documento dentro de um webview/iframe.
- Abas Pro no modo free: conteúdo borrado com overlay "Desbloquear (Pro)".
- Botão "Exportar PDF" no canto superior direito (exporta a aba ativa).
- Botão "Novo Scan" para voltar à Drop Zone.

### PDF Export

- Usa `webContents.printToPDF()` nativo do Electron/Chromium.
- Nome do arquivo automático: `{NomeProjeto}_{NomeDoc}_{Data}.pdf`.
- Diálogo "Salvar como" nativo do SO.
- Após salvar: notificação com "Abrir PDF" e "Abrir pasta".

## Modelo freemium

| Feature | Free | Pro |
|---------|------|-----|
| Scan Report | ✅ | ✅ |
| Decision Brief | ✅ | ✅ |
| Technical Spec | ❌ borrado | ✅ |
| Migration Plan | ❌ borrado | ✅ |
| Sales Datasheet | ❌ borrado | ✅ |
| Targets (react-node, net-blazor, sap-fiori) | ❌ | ✅ |
| Export PDF (docs free) | ✅ | ✅ |
| Export PDF (todos os docs) | ❌ | ✅ |
| Idiomas (PT-BR, EN-US) | ✅ | ✅ |

### Licença

- Token JWT assinado com Ed25519.
- Payload: `{app_id, edition, modules[], customer_id, expires_at}`.
- Verificação local com chave pública embutida no app.
- Sem internet para validar.
- Tela de ativação: campo de texto para colar a chave + botão "Ativar".
- Chave inválida/expirada: volta para modo Free com mensagem clara.
- Grace period: 7 dias após expiração antes de desabilitar Pro features.

## Distribuição

### Windows
- Formato: .exe (NSIS installer via electron-builder).
- Sem code signing no MVP (aceitar SmartScreen warning).
- Futuro: EV certificate para eliminar warnings.

### macOS
- Formato: .dmg (electron-builder).
- Sem notarização no MVP (usuário precisa permitir em Preferências de Segurança).
- Futuro: Apple Developer Account + notarização.

### Auto-update
- electron-updater com GitHub Releases como backend.
- Canal único (stable) no MVP.
- Update check silencioso ao abrir o app.
- Notificação: "Nova versão disponível. Atualizar agora?"
- Download em background, instala ao reiniciar.

## Estrutura do projeto

```
codedocs-desktop/
├── electron/
│   ├── main.ts              — processo principal, janela, lifecycle
│   ├── preload.ts           — IPC bridge seguro (contextBridge)
│   ├── sidecar.ts           — spawn/manage Python process
│   ├── license.ts           — verificação Ed25519
│   └── updater.ts           — auto-update logic
├── src/                     — React app (renderer)
│   ├── App.tsx              — router entre as 3 telas
│   ├── pages/
│   │   ├── DropZone.tsx     — drag-and-drop + file picker
│   │   ├── Progress.tsx     — barra de progresso + etapas
│   │   └── Results.tsx      — abas + document viewer + export
│   ├── components/
│   │   ├── TabBar.tsx       — barra de abas dos documentos
│   │   ├── DocumentView.tsx — renderiza HTML do doc
│   │   ├── ProOverlay.tsx   — overlay borrado para docs Pro
│   │   ├── ExportPDF.tsx    — botão + lógica de export
│   │   └── ActivateKey.tsx  — modal de ativação de licença
│   └── hooks/
│       ├── useScan.ts       — IPC com main para scan
│       └── useLicense.ts    — estado da licença
├── python/                  — CodeDocs engine
│   ├── wrapper.py           — stdin/stdout JSON protocol
│   └── dist/                — PyInstaller output (executável)
├── assets/
│   ├── icon.icns            — ícone macOS
│   ├── icon.ico             — ícone Windows
│   └── icon.png             — ícone genérico
├── package.json
├── electron-builder.yml     — config de empacotamento
├── tsconfig.json
├── vite.config.ts           — bundler do renderer
└── README.md
```

## Python wrapper (protocolo JSON)

O CodeDocs CLI atual gera arquivos HTML. O wrapper (`python/wrapper.py`) adapta isso para o protocolo stdin/stdout:

```python
"""Wrapper: adapta codedocs para comunicação JSON via stdio."""
import json
import sys
from codedocs.scanner import scan
from codedocs.renderer import (render_scan_report, render_sales_datasheet,
    render_technical_spec, render_migration_plan, render_decision_brief)
from codedocs.migration import analyze_migration

def progress(step, total, label):
    print(json.dumps({"type": "progress", "step": step, "total": total, "label": label}), flush=True)

def main():
    request = json.loads(sys.stdin.readline())
    path = request["path"]
    opts = request.get("options", {})
    lang = opts.get("lang", "pt-BR")
    target = opts.get("target")
    name = opts.get("name")

    data = scan(path, progress_callback=progress)
    if name:
        data["project"]["name"] = name

    files = {}
    files["scan-report"] = render_scan_report(data, lang=lang)
    files["decision-brief"] = render_decision_brief(data, lang=lang)

    # Pro docs — sempre gera, o gate é no frontend
    files["technical-spec"] = render_technical_spec(data, lang=lang, target=target)
    files["sales-datasheet"] = render_sales_datasheet(data, lang=lang, target=target)

    plan = analyze_migration(data, target_platform=target or "all")
    files["migration-plan"] = render_migration_plan(data, plan, lang=lang)
    files["decision-brief"] = render_decision_brief(data, plan, lang=lang)

    print(json.dumps({"type": "result", "files": files}), flush=True)

if __name__ == "__main__":
    main()
```

## Erros e edge cases

| Cenário | Comportamento |
|---------|--------------|
| Pasta vazia / sem código | Tela de erro: "Nenhum arquivo de código encontrado nesta pasta." + botão "Tentar outra pasta" |
| Scan falha / Python crash | Tela de erro: "Erro ao analisar o projeto." + log path + botão "Tentar novamente" |
| Python sidecar não inicia | Tela de erro: "Componente de análise não encontrado." + sugerir reinstalação |
| Timeout (>5 min) | Tela de erro: "A análise demorou mais que o esperado." + botão "Tentar novamente" |
| Licença expirada | Banner no topo: "Sua licença Pro expirou em DD/MM. Docs Pro em modo somente-leitura por 7 dias." |
| Licença inválida | Modal: "Chave inválida. Verifique se copiou corretamente." |
| Drop de arquivo (não pasta) | Ignorar silenciosamente, manter drop zone ativa |
| Projeto muito grande (>10k files) | Warning antes de iniciar: "Este projeto tem N arquivos. A análise pode levar alguns minutos." |

## Fora de escopo (MVP)

- Wizard de onboarding (primeira tela já é o drop zone).
- Histórico de scans / projetos recentes.
- Branding customizável no PDF.
- Code signing (Windows EV + macOS notarização).
- Múltiplos idiomas no app UI (app sempre em PT-BR, docs escolhem idioma).
- Tela de configurações.
- Beta channel no auto-update.

## Métricas de sucesso

- Download → primeiro scan completo em menos de 2 minutos (incluindo install).
- Gestor não-técnico consegue gerar o Decision Brief sem ajuda.
- Tamanho do instalador < 250MB (Electron ~150MB + Python frozen ~50-80MB).
- Zero dados enviados para internet (verificável por firewall).
