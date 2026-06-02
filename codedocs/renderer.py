"""HTML renderer — generates documentation from scan data. Zero dependencies."""

import html

from codedocs.i18n import t


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0f;--bg2:#12121a;--bg3:#1a1a2e;--fg:#e0e0e8;--fg2:#a0a0b0;--accent:#f59e0b;--accent2:#3b82f6;--green:#22c55e;--yellow:#eab308;--red:#ef4444;--border:#2a2a3e;--font:'Segoe UI','Helvetica Neue',Arial,sans-serif;--mono:'Courier New','Consolas',monospace}
body{background:var(--bg);color:var(--fg);font-family:var(--font);font-size:14px;line-height:1.6;padding:0;margin:0}
.container{max-width:1100px;margin:0 auto;padding:20px 30px}
h1{font-size:28px;font-weight:700;margin-bottom:8px;color:#fff}
h2{font-size:20px;font-weight:600;margin:32px 0 16px;color:#fff;padding-bottom:8px;border-bottom:1px solid var(--border)}
h3{font-size:16px;font-weight:600;margin:20px 0 10px;color:var(--fg)}
.subtitle{color:var(--fg2);font-size:15px;margin-bottom:24px}
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;margin-right:6px;margin-bottom:4px}
.badge-green{background:rgba(34,197,94,.15);color:var(--green)}
.badge-yellow{background:rgba(234,179,8,.15);color:var(--yellow)}
.badge-red{background:rgba(239,68,68,.15);color:var(--red)}
.badge-blue{background:rgba(59,130,246,.15);color:var(--accent2)}
.badge-amber{background:rgba(245,158,11,.15);color:var(--accent)}
table{width:100%;border-collapse:collapse;margin:12px 0 20px}
th{text-align:left;padding:10px 12px;background:var(--bg3);color:var(--fg2);font-size:12px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--border)}
td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px;color:var(--fg)}
tr:hover td{background:var(--bg2)}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:20px;margin:12px 0}
.metric{text-align:center;padding:16px}
.metric-value{font-size:36px;font-weight:700;color:#fff}
.metric-label{font-size:12px;color:var(--fg2);text-transform:uppercase;letter-spacing:.5px;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0}
.status-impl{color:var(--green)}
.status-partial{color:var(--yellow)}
.status-notdet{color:var(--red)}
.evidence{font-family:var(--mono);font-size:12px;color:var(--fg2)}
.section{margin-bottom:32px}
.hero{background:linear-gradient(135deg,var(--bg2),var(--bg3));border:1px solid var(--border);border-radius:12px;padding:40px;margin:20px 0 32px;text-align:center}
.hero h1{font-size:32px;margin-bottom:12px}
.note{background:rgba(59,130,246,.08);border-left:3px solid var(--accent2);padding:12px 16px;margin:12px 0;border-radius:0 6px 6px 0;font-size:13px}
.warn{background:rgba(239,68,68,.08);border-left:3px solid var(--red);padding:12px 16px;margin:12px 0;border-radius:0 6px 6px 0;font-size:13px}
.footer{text-align:center;padding:32px;color:var(--fg2);font-size:12px;border-top:1px solid var(--border);margin-top:40px}
code{font-family:var(--mono);background:var(--bg3);padding:1px 5px;border-radius:3px;font-size:12px}
@media print{body{background:#fff;color:#000}h1,h2,h3,.metric-value{color:#000}th{background:#f0f0f0}td{border-color:#ddd}.card{border-color:#ddd;background:#fafafa}.hero{background:#f5f5f5;border-color:#ddd}}
"""


def _e(text):
    return html.escape(str(text))


def _status_badge(detected, lang="pt-BR"):
    if detected:
        return f'<span class="badge badge-green">{t("common.implemented", lang)}</span>'
    return f'<span class="badge badge-red">{t("common.not_detected", lang)}</span>'


def _score_color(score):
    if score >= 70:
        return "green"
    if score >= 40:
        return "yellow"
    return "red"


def _risk_narrative(score, data, lang="pt-BR"):
    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    contributors = len(data["git"]["contributors"])
    if score <= 30:
        return t("risk.narrative_critical", lang).format(sf=sf, tf=tf, contributors=contributors)
    elif score <= 50:
        return t("risk.narrative_moderate_high", lang)
    elif score <= 70:
        return t("risk.narrative_moderate", lang)
    else:
        return t("risk.narrative_low", lang)


def _risk_score(data, lang="pt-BR"):
    scores = []
    sf = max(1, data["tests"]["source_files"])
    tf = data["tests"]["test_files"]
    test_ratio = tf / sf
    test_score = min(100, int(test_ratio * 200))
    if tf == 0 and sf > 50:
        test_label = t("score.test_critical", lang).format(sf=sf)
    elif test_ratio < 0.05:
        test_label = t("score.test_high_risk", lang).format(tf=tf, sf=sf, pct=int(test_ratio*100))
    else:
        test_label = f"{tf}/{sf} ({int(test_ratio*100)}%)"
    scores.append((t("score.test_coverage", lang), test_score, test_label))

    contributors = len(data["git"]["contributors"])
    bus_score = min(100, contributors * 25) if contributors > 0 else 0
    if contributors <= 1:
        bus_label = t("score.bus_critical", lang)
    elif contributors <= 2:
        bus_label = t("score.bus_high_risk", lang).format(contributors=contributors)
    else:
        bus_label = t("score.bus_ok", lang).format(contributors=contributors)
    scores.append((t("score.bus_factor", lang), bus_score, bus_label))

    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = max(1, len(data["security"]))
    scores.append((t("score.security_controls", lang), int(sec_count / sec_total * 100), t("score.controls_ratio", lang).format(count=sec_count, total=sec_total)))

    loc = max(1, data["health"]["loc"])
    debt = data["health"]["todos"] / (loc / 1000)
    debt_score = max(0, 100 - int(debt * 15))
    scores.append((t("score.tech_debt", lang), debt_score, t("score.debt_detail", lang).format(todos=data["health"]["todos"], loc=f"{loc:,}", density=f"{debt:.1f}")))

    doc_score = min(100, len(data["existing_docs"]) * 12)
    scores.append((t("score.documentation", lang), doc_score, t("score.doc_files", lang).format(count=len(data["existing_docs"]))))

    dep_score = 80 if data["dependencies"]["manager"] != "NOT DETECTED" else 20
    scores.append((t("score.dependency_mgmt", lang), dep_score, data["dependencies"]["manager"]))

    weights = [0.35, 0.25, 0.15, 0.10, 0.08, 0.07]
    composite = min(100, int(sum(s[1] * w for s, w in zip(scores, weights))))

    if tf == 0 and sf > 50:
        composite = min(composite, 30)
    if contributors <= 1 and sf > 50:
        composite = min(composite, 35)

    return composite, scores


def _executive_verdict(score, data, lang="pt-BR"):
    if score <= 30:
        diagnosis = t("verdict.diagnosis_0_30", lang)
    elif score <= 50:
        diagnosis = t("verdict.diagnosis_31_50", lang)
    elif score <= 70:
        diagnosis = t("verdict.diagnosis_51_70", lang)
    elif score <= 85:
        diagnosis = t("verdict.diagnosis_71_85", lang)
    else:
        diagnosis = t("verdict.diagnosis_86_100", lang)

    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    contributors = len(data["git"]["contributors"])

    dont_do = []
    if tf == 0:
        dont_do.append(t("verdict.dont_expand_scope", lang))
    if contributors <= 2:
        dont_do.append(t("verdict.dont_hire_before_busfactor", lang))
    if score <= 50:
        dont_do.append(t("verdict.dont_migrate_before_fundamentals", lang))

    actions = []
    if tf == 0 and sf > 0:
        actions.append(t("verdict.action_add_tests", lang).format(sf=sf))
    elif tf > 0 and sf > 0 and tf / sf < 0.1:
        actions.append(t("verdict.action_increase_coverage", lang).format(ratio=int(tf/sf*100)))
    if contributors <= 2:
        actions.append(t("verdict.action_document_onboarding", lang).format(contributors=contributors))
    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = len(data["security"])
    if sec_count < sec_total * 0.7:
        actions.append(t("verdict.action_security_controls", lang).format(missing=sec_total - sec_count))

    risk_items = []
    if tf == 0 and sf > 50:
        risk_items.append(t("verdict.risk_regression", lang))
    if contributors <= 1:
        risk_items.append(t("verdict.risk_key_person_full", lang))
    elif contributors <= 2:
        risk_items.append(t("verdict.risk_key_person_partial", lang))

    if score <= 30:
        risk_level = t("verdict.risk_high", lang)
    elif score <= 50:
        risk_level = t("verdict.risk_medium", lang)
    elif score <= 70:
        risk_level = t("verdict.risk_low_medium", lang)
    else:
        risk_level = t("verdict.risk_low", lang)

    risk_text = t("verdict.risk_factors", lang).format(level=risk_level, factors="; ".join(risk_items)) if risk_items else f"{risk_level}."

    return {
        "diagnosis": diagnosis,
        "dont_do": "; ".join(dont_do).capitalize() if dont_do else t("verdict.no_restrictions", lang),
        "action": actions[0] if actions else t("verdict.action_maintain", lang),
        "financial_risk": risk_text,
    }


def _audit_readiness(data, lang="pt-BR"):
    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    integrations = data["integrations"]
    questions = []

    integ_count = len(integrations)
    if integ_count > 0:
        classified = [i for i in integrations if i.get("data_residency") and i["data_residency"] != "Unknown"]
        if len(classified) == integ_count:
            q_status = f'<span class="badge badge-green">{t("badges.mapped", lang)}</span>'
            q_answer = t("audit.a_data_mapped", lang).format(count=integ_count)
        else:
            q_status = f'<span class="badge badge-yellow">{t("badges.partial", lang)}</span>'
            q_answer = t("audit.a_data_partial", lang).format(count=integ_count)
    else:
        q_status = f'<span class="badge badge-green">{t("common.na", lang)}</span>'
        q_answer = t("audit.a_data_none", lang)
    questions.append((t("audit.q_data_storage", lang), q_status, q_answer))

    sla_detected = any(v["detected"] for k, v in data["security"].items() if "audit" in k)
    if sla_detected:
        q_status = f'<span class="badge badge-yellow">{t("badges.partial", lang)}</span>'
        q_answer = t("audit.a_dr_partial", lang)
    else:
        q_status = f'<span class="badge badge-red">{t("badges.not_defined", lang)}</span>'
        q_answer = t("audit.a_dr_none", lang)
    questions.append((t("audit.q_disaster_recovery", lang), q_status, q_answer))

    if tf == 0 and sf > 0:
        q_status = f'<span class="badge badge-red">{t("badges.high_risk", lang)}</span>'
        q_answer = t("audit.a_tests_zero", lang)
    elif sf > 0 and tf / sf < 0.1:
        q_status = f'<span class="badge badge-yellow">{t("badges.low_coverage", lang)}</span>'
        q_answer = t("audit.a_tests_low", lang).format(ratio=int(tf/sf*100))
    else:
        ratio = int(tf / max(1, sf) * 100)
        q_status = f'<span class="badge badge-green">{t("badges.covered", lang)}</span>'
        q_answer = t("audit.a_tests_ok", lang).format(ratio=ratio)
    questions.append((t("audit.q_bug_production", lang), q_status, q_answer))

    if data["auth"]["rbac"] and data["auth"]["method"] != "NOT DETECTED":
        auth_evidence = ", ".join(data["auth"]["evidence"][:3]) or "—"
        q_status = f'<span class="badge badge-green">{t("common.implemented", lang)}</span>'
        q_answer = t("audit.a_auth_full", lang).format(method=data["auth"]["method"], evidence=auth_evidence)
    elif data["auth"]["method"] != "NOT DETECTED":
        q_status = f'<span class="badge badge-yellow">{t("badges.partial", lang)}</span>'
        q_answer = t("audit.a_auth_partial", lang).format(method=data["auth"]["method"])
    else:
        q_status = f'<span class="badge badge-red">{t("badges.not_detected_badge", lang)}</span>'
        q_answer = t("audit.a_auth_none", lang)
    questions.append((t("audit.q_multi_tenant", lang), q_status, q_answer))

    return questions


def _product_description(data, lang="pt-BR"):
    name = data["project"]["name"]
    sys_type = data["project"].get("system_type", "web-platform")
    langs = ", ".join(sorted(data["languages"].keys(), key=lambda x: -data["languages"][x]["files"])[:3])
    endpoints = len(data["endpoints"])
    integrations = len(data["integrations"])
    tables = len(data["database"]["tables"])
    score, _ = _risk_score(data, lang)

    type_keys = {"CRM": "type_crm", "ERP": "type_erp", "E-commerce": "type_ecommerce", "SaaS Platform": "type_saas", "web-platform": "type_web"}
    type_label = t(f"product.{type_keys.get(sys_type, 'type_default')}", lang)

    parts = []
    if score <= 30:
        parts.append(t("product.risk_critical", lang))
    elif score <= 50:
        parts.append(t("product.risk_moderate_high", lang))
    elif score <= 70:
        parts.append(t("product.risk_moderate", lang))
    else:
        parts.append(t("product.risk_low", lang))

    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = len(data["security"])
    if sec_count >= sec_total * 0.8:
        parts.append(t("product.security_solid", lang))
    elif sec_count >= sec_total * 0.5:
        parts.append(t("product.security_partial", lang))

    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    contributors = len(data["git"]["contributors"])
    gap_items = []
    if tf == 0 and sf > 0:
        gap_items.append(t("tech_spec.automated_tests", lang).lower())
    if contributors <= 2:
        gap_items.append(t("tech_spec.bus_factor", lang).lower())
    if gap_items:
        parts.append(t("product.gaps_in", lang).format(items=" & ".join(gap_items)))

    summary_text = ", ".join(parts)

    return t("product.description", lang).format(
        name=_e(name), type=type_label, langs=langs, endpoints=endpoints,
        integrations=integrations, tables=tables, score=score, summary=summary_text
    )


def _render_executive_verdict(score, data, lang="pt-BR"):
    v = _executive_verdict(score, data, lang)
    return f"""
<div class="card" style="border-left:3px solid var(--accent)">
  <h3 style="margin-top:0">{t("verdict.title", lang)}</h3>
  <p><strong>{t("verdict.diagnostic_label", lang)}</strong> {v['diagnosis']}</p>
  <p><strong>{t("verdict.dont_do_label", lang)}</strong> {v['dont_do']}</p>
  <p><strong>{t("verdict.next_action_label", lang)}</strong> {v['action']}</p>
  <p><strong>{t("verdict.financial_risk_label", lang)}</strong> {v['financial_risk']}</p>
</div>
"""


def _render_audit_readiness(data, lang="pt-BR"):
    questions = _audit_readiness(data, lang)
    rows = ""
    for question, status, answer in questions:
        rows += f"<tr><td>{question}</td><td>{status}</td><td>{answer}</td></tr>"
    return f"""
<h2>{t("audit.title", lang)}</h2>
<div class="warn">
  <strong>{t("audit.subtitle", lang)}</strong>
</div>
<table>
  <tr><th>{t("headers.question", lang)}</th><th>{t("headers.current_status", lang)}</th><th>{t("headers.recommended_answer", lang)}</th></tr>
  {rows}
</table>
"""


def _render_sla_by_size(lang="pt-BR"):
    return f"""
<h3>{t("sla.title", lang)}</h3>
<table>
  <tr><th>{t("headers.tier", lang)}</th><th>{t("headers.uptime", lang)}</th><th>{t("headers.rpo", lang)}</th><th>{t("headers.rto", lang)}</th><th>{t("headers.backup", lang)}</th></tr>
  <tr><td><strong>{t("sla.sme", lang)}</strong> {t("sla.sme_size", lang)}</td><td>99.0%</td><td>8h</td><td>4h</td><td>{t("sla.daily", lang)}</td></tr>
  <tr><td><strong>{t("sla.mid", lang)}</strong> {t("sla.mid_size", lang)}</td><td>99.5%</td><td>4h</td><td>1h</td><td>{t("sla.every_6h", lang)}</td></tr>
  <tr><td><strong>{t("sla.enterprise", lang)}</strong> {t("sla.enterprise_size", lang)}</td><td>99.9%</td><td>1h</td><td>15min</td><td>{t("sla.continuous_dr", lang)}</td></tr>
</table>
"""


def _is_dotnet_project(data):
    frameworks = [f["name"] for f in data.get("migration", {}).get("frameworks", [])]
    dotnet_indicators = ["ASP.NET MVC/API", "Web Forms", "WinForms", "WPF", "Blazor"]
    return any(fw in dotnet_indicators for fw in frameworks) or "csharp" in data.get("languages", {})


TARGET_RECOMMENDATIONS = {
    "react+express": {
        "pt-BR": {
            "paragraph": "Recomendamos migrar gradualmente o backend atual para Node.js (Express/NestJS) em TypeScript, mantendo o frontend em React TypeScript. Isso unifica a stack em uma única linguagem (TypeScript) em todo o produto, facilita contratação de devs e permite aproveitar o ecossistema npm. Para a equipe atual, a curva de aprendizado é baixa e o ganho de produtividade é alto.",
            "recs": [
                "Definir um monorepo ou estratégia clara de compartilhamento de tipos (DTOs) entre frontend React e backend NestJS para reduzir bugs de contrato de API.",
                "Adotar NestJS como backbone do backend (módulos, DI, guards) para que devs vindos de ASP.NET MVC se sintam em casa.",
                "Padronizar testes E2E (por exemplo, Playwright/Cypress) cobrindo os módulos revenue-critical antes da virada completa de rota no proxy.",
            ],
        },
        "en-US": {
            "paragraph": "We recommend gradually migrating the current backend to Node.js (Express/NestJS) in TypeScript, keeping the frontend in React TypeScript. This unifies the stack into a single language (TypeScript) across the entire product, makes hiring easier, and leverages the npm ecosystem. For the current team, the learning curve is low and the productivity gain is high.",
            "recs": [
                "Define a monorepo or clear type-sharing strategy (DTOs) between React frontend and NestJS backend to reduce API contract bugs.",
                "Adopt NestJS as the backend backbone (modules, DI, guards) so devs coming from ASP.NET MVC feel at home.",
                "Standardize E2E tests (e.g., Playwright/Cypress) covering revenue-critical modules before full route switch at the proxy.",
            ],
        },
    },
    "blazor": {
        "pt-BR": {
            "paragraph": "Recomendamos migrar a aplicação para .NET 8, usando ASP.NET Core no backend e Blazor na camada de interface. Este alvo é ideal para times que já dominam C# e têm outros sistemas corporativos em .NET. Ele reduz a necessidade de aprender outra linguagem, permite reaproveitar bibliotecas existentes e facilita a integração com o ecossistema Microsoft (AD/Entra ID, SQL Server, Azure, etc.).",
            "recs": [
                "Planejar uma biblioteca compartilhada de lógica de negócio (projeto .NET class library) que possa ser usada tanto pelas APIs quanto pelos componentes Blazor, evitando duplicação de regras.",
                "Migrar telas mais simples de manutenção e consulta primeiro (painéis, cadastros), antes de atacar fluxos críticos de faturamento, usando feature flags para rollback rápido.",
                "Definir desde o início o padrão de autenticação/SSO (OpenID Connect / Entra ID / IdentityServer) e como as roles de negócio vão mapear para roles de autorização no código.",
            ],
        },
        "en-US": {
            "paragraph": "We recommend migrating the application to .NET 8, using ASP.NET Core for the backend and Blazor for the UI layer. This target is ideal for teams that already master C# and have other corporate systems in .NET. It reduces the need to learn another language, allows reuse of existing libraries, and facilitates integration with the Microsoft ecosystem (AD/Entra ID, SQL Server, Azure, etc.).",
            "recs": [
                "Plan a shared business logic library (.NET class library project) that can be used by both APIs and Blazor components, avoiding rule duplication.",
                "Migrate simpler maintenance and lookup screens first (dashboards, CRUD), before tackling critical billing flows, using feature flags for fast rollback.",
                "Define the authentication/SSO pattern from the start (OpenID Connect / Entra ID / IdentityServer) and how business roles will map to authorization roles in code.",
            ],
        },
    },
    "sap-fiori-ui5": {
        "pt-BR": {
            "paragraph": "Recomendamos expor o núcleo do sistema por meio de APIs adequadas a SAP (OData/REST) e construir apps Fiori específicos para os processos que precisam viver dentro do Launchpad SAP. Este alvo é indicado quando a organização já tem S/4HANA ou SAP BTP e exige experiência nativa SAP Fiori para usuários internos. A stack é mais especializada e requer equipe com experiência em SAPUI5 e OData, mas traz alinhamento total com governança SAP.",
            "recs": [
                "Identificar quais fluxos realmente precisam de UI Fiori (ex.: aprovação de pedidos, consulta de crédito, visão 360 do cliente) e quais podem continuar em uma UI web independente. Isso evita reescrever telas desnecessárias em SAPUI5.",
                "Projetar o backend atual para expor serviços em um formato amigável a SAP (OData/REST) via API Gateway, garantindo autenticação, autorização e logging compatíveis com o landscape SAP (S/4HANA/BTP).",
                "Planejar a convivência entre Fiori e a UI existente durante o período híbrido: alguns perfis entrarão pelo Fiori Launchpad, outros pela aplicação web atual. Documentar claramente quais perfis usam qual entrada e como será a transição.",
            ],
        },
        "en-US": {
            "paragraph": "We recommend exposing the system's core through SAP-compatible APIs (OData/REST) and building specific Fiori apps for processes that need to live within the SAP Launchpad. This target is recommended when the organization already has S/4HANA or SAP BTP and requires native SAP Fiori experience for internal users. The stack is more specialized and requires a team with SAPUI5 and OData expertise, but provides full alignment with SAP governance.",
            "recs": [
                "Identify which flows truly need Fiori UI (e.g., purchase order approval, credit check, 360 customer view) and which can continue in an independent web UI. This avoids unnecessarily rewriting screens in SAPUI5.",
                "Design the current backend to expose services in an SAP-friendly format (OData/REST) via API Gateway, ensuring authentication, authorization, and logging compatible with the SAP landscape (S/4HANA/BTP).",
                "Plan coexistence between Fiori and the existing UI during the hybrid period: some profiles will enter via Fiori Launchpad, others via the current web app. Clearly document which profiles use which entry point and how the transition will work.",
            ],
        },
    },
}

TARGET_LABELS = {
    "react+express": {"pt-BR": "React + Node.js (Express/NestJS) — full TypeScript", "en-US": "React + Node.js (Express/NestJS) — full TypeScript"},
    "blazor": {"pt-BR": ".NET 8 — ASP.NET Core + Blazor", "en-US": ".NET 8 — ASP.NET Core + Blazor"},
    "sap-fiori-ui5": {"pt-BR": "SAP Fiori (SAPUI5/OpenUI5) + serviços OData", "en-US": "SAP Fiori (SAPUI5/OpenUI5) + OData services"},
}

NEUTRAL_NOTE = {
    "pt-BR": "Nenhuma plataforma-alvo foi selecionada. Use <code>--target react-node</code>, <code>--target net-blazor</code> ou <code>--target sap-fiori-ui5</code> para ver recomendações específicas de modernização.",
    "en-US": "No target platform selected. Use <code>--target react-node</code>, <code>--target net-blazor</code> or <code>--target sap-fiori-ui5</code> for specific modernization recommendations.",
}


def _target_recs_html(target_key, lang="pt-BR"):
    info = TARGET_RECOMMENDATIONS.get(target_key, {}).get(lang, {})
    if not info:
        return ""
    recs = info.get("recs", [])
    items = "".join(f"<li>{r}</li>" for r in recs)
    label = TARGET_LABELS.get(target_key, {}).get(lang, target_key)
    return f"""<div class="card" style="border-left:3px solid var(--accent2)">
    <h3 style="margin-top:0;color:var(--accent2)">{_e(label)}</h3>
    <ul style="margin-top:8px">{items}</ul>
</div>"""


TARGET_SELECTED_NOTE = {
    "react+express": {
        "pt-BR": "Plataforma-alvo selecionada: <strong>react-node</strong> (React + Express / NestJS, full TypeScript). As recomendações abaixo são específicas para este caminho de modernização.",
        "en-US": "Selected target platform: <strong>react-node</strong> (React + Express / NestJS, full TypeScript). The recommendations below are specific to this modernization path.",
    },
    "blazor": {
        "pt-BR": "Plataforma-alvo selecionada: <strong>net-blazor</strong> (.NET 8 — ASP.NET Core + Blazor). As recomendações abaixo são específicas para este caminho de modernização.",
        "en-US": "Selected target platform: <strong>net-blazor</strong> (.NET 8 — ASP.NET Core + Blazor). The recommendations below are specific to this modernization path.",
    },
    "sap-fiori-ui5": {
        "pt-BR": "Plataforma-alvo selecionada: <strong>sap-fiori-ui5</strong> (SAP Fiori / SAPUI5 + serviços OData). As recomendações abaixo são específicas para este caminho de modernização.",
        "en-US": "Selected target platform: <strong>sap-fiori-ui5</strong> (SAP Fiori / SAPUI5 + OData services). The recommendations below are specific to this modernization path.",
    },
}


def _target_summary_html(target_key, lang="pt-BR"):
    info = TARGET_RECOMMENDATIONS.get(target_key, {}).get(lang, {})
    if not info:
        return ""
    paragraph = info.get("paragraph", "")
    note = TARGET_SELECTED_NOTE.get(target_key, {}).get(lang, "")
    return f"""<div class="note" style="margin-bottom:16px">{note}</div>
<div class="card" style="border-left:3px solid var(--accent)">
    <p style="color:var(--fg)">{paragraph}</p>
</div>"""


def _neutral_note_html(lang="pt-BR"):
    return f'<p class="note">{NEUTRAL_NOTE.get(lang, NEUTRAL_NOTE["en-US"])}</p>'


SALES_TARGET_NOTES = {
    "react+express": {
        "pt-BR": 'O plano de modernização pode ser gerado com diferentes plataformas-alvo recomendadas (React + Node/NestJS, .NET 8 + Blazor, SAP Fiori SAPUI5), com prós e contras claros para cada cenário. Para {name}, o alvo recomendado atualmente é <strong>React + Node/NestJS (full TypeScript)</strong> pela afinidade com a stack existente e facilidade de contratação.',
        "en-US": 'The modernization plan can be generated with different recommended target platforms (React + Node/NestJS, .NET 8 + Blazor, SAP Fiori SAPUI5), with clear pros and cons for each scenario. For {name}, the currently recommended target is <strong>React + Node/NestJS (full TypeScript)</strong> due to stack affinity and ease of hiring.',
    },
    "blazor": {
        "pt-BR": 'O plano de modernização pode ser gerado com diferentes plataformas-alvo recomendadas (React + Node/NestJS, .NET 8 + Blazor, SAP Fiori SAPUI5), com prós e contras claros para cada cenário. Para {name}, o alvo recomendado atualmente é <strong>.NET 8 + Blazor</strong> pela afinidade com o ecossistema Microsoft e reaproveitamento de bibliotecas existentes.',
        "en-US": 'The modernization plan can be generated with different recommended target platforms (React + Node/NestJS, .NET 8 + Blazor, SAP Fiori SAPUI5), with clear pros and cons for each scenario. For {name}, the currently recommended target is <strong>.NET 8 + Blazor</strong> due to Microsoft ecosystem affinity and reuse of existing libraries.',
    },
    "sap-fiori-ui5": {
        "pt-BR": 'O plano de modernização pode ser gerado com diferentes plataformas-alvo recomendadas (React + Node/NestJS, .NET 8 + Blazor, SAP Fiori SAPUI5), com prós e contras claros para cada cenário. Para {name}, o alvo recomendado atualmente é <strong>SAP Fiori (SAPUI5)</strong> pela exigência de UI nativa SAP integrada ao Launchpad e S/4HANA.',
        "en-US": 'The modernization plan can be generated with different recommended target platforms (React + Node/NestJS, .NET 8 + Blazor, SAP Fiori SAPUI5), with clear pros and cons for each scenario. For {name}, the currently recommended target is <strong>SAP Fiori (SAPUI5)</strong> due to the requirement for native SAP UI integrated with Launchpad and S/4HANA.',
    },
}

TECHSPEC_TARGET_NOTES = {
    "react+express": {
        "pt-BR": "Um plano de migração faseado para React + Node/NestJS (full TypeScript) foi gerado separadamente, com esforço estimado e roadmap por módulo.",
        "en-US": "A phased migration plan to React + Node/NestJS (full TypeScript) was generated separately, with estimated effort and per-module roadmap.",
    },
    "blazor": {
        "pt-BR": "Um plano de migração faseado para .NET 8 + Blazor foi gerado separadamente, com esforço estimado e roadmap por módulo.",
        "en-US": "A phased migration plan to .NET 8 + Blazor was generated separately, with estimated effort and per-module roadmap.",
    },
    "sap-fiori-ui5": {
        "pt-BR": "Um plano de migração faseado para SAP Fiori (SAPUI5) + serviços OData foi gerado separadamente, com esforço estimado e roadmap por módulo.",
        "en-US": "A phased migration plan to SAP Fiori (SAPUI5) + OData services was generated separately, with estimated effort and per-module roadmap.",
    },
}


def _sales_target_note(target, product_name, lang="pt-BR"):
    from codedocs.migration import _resolve_target
    if not target:
        return ""
    key = _resolve_target(target)
    info = SALES_TARGET_NOTES.get(key, {}).get(lang)
    if not info:
        return ""
    return f'<div class="note">{info.format(name=product_name)}</div>'


def _techspec_target_note(target, lang="pt-BR"):
    from codedocs.migration import _resolve_target
    if not target:
        return ""
    key = _resolve_target(target)
    note = TECHSPEC_TARGET_NOTES.get(key, {}).get(lang)
    if not note:
        return ""
    return f'<p class="note" style="margin-top:12px">{note}</p>'


def _wrap_html(title, body, lang="pt-BR"):
    html_lang = "pt" if lang == "pt-BR" else "en"
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_e(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
{body}
<div class="footer">
{t("footer.generated_by", lang)}<br>
{t("footer.tagline", lang)}
</div>
</div>
</body>
</html>"""


def render_scan_report(data, lang="pt-BR"):
    name = _e(data["project"]["name"])
    date = _e(data["project"]["scan_date"])
    score, score_details = _risk_score(data, lang)
    sc = _score_color(score)

    langs_rows = ""
    for l, info in sorted(data["languages"].items(), key=lambda x: -x[1]["files"]):
        langs_rows += f"<tr><td>{_e(l)}</td><td>{info['files']}</td><td>{info['lines']:,}</td></tr>"
    total_files = sum(v["files"] for v in data["languages"].values())
    total_loc = sum(v["lines"] for v in data["languages"].values())
    langs_rows += f"<tr><td><strong>{t('common.total', lang)}</strong></td><td><strong>{total_files}</strong></td><td><strong>{total_loc:,}</strong></td></tr>"

    endpoints_rows = ""
    for ep in data["endpoints"][:50]:
        endpoints_rows += f"<tr><td><code>{_e(ep['method'])}</code></td><td>{_e(ep['path'])}</td><td class='evidence'>{_e(ep['file'])}:{ep['line']}</td></tr>"

    tables_rows = ""
    for tbl in data["database"]["tables"]:
        tables_rows += f"<tr><td>{_e(tbl['name'])}</td><td class='evidence'>{_e(tbl['file'])}:{tbl['line']}</td></tr>"

    sec_rows = ""
    for control, info in data["security"].items():
        label = control.replace("_", " ").title()
        status = _status_badge(info["detected"], lang)
        evidence = ", ".join(info["files"][:3]) if info["files"] else "—"
        sec_rows += f"<tr><td>{label}</td><td>{status}</td><td class='evidence'>{_e(evidence)}</td></tr>"

    integrations_rows = ""
    for integ in data["integrations"]:
        integrations_rows += f"<tr><td>{_e(integ['service'])}</td><td class='evidence'>{_e(integ['file'])}:{integ['line']}</td></tr>"

    score_rows = ""
    for label, val, evidence in score_details:
        color = _score_color(val)
        score_rows += f"<tr><td>{label}</td><td><span class='badge badge-{color}'>{val}/100</span></td><td class='evidence'>{_e(evidence)}</td></tr>"

    todos_rows = ""
    for item in data["health"]["todo_items"][:15]:
        todos_rows += f"<tr><td class='evidence'>{_e(item['file'])}:{item['line']}</td><td>{_e(item['content'])}</td></tr>"

    deps_rows = ""
    for dep in data["dependencies"]["items"][:30]:
        deps_rows += f"<tr><td>{_e(dep['name'])}</td><td>{_e(dep['version'])}</td></tr>"

    git_rows = ""
    for entry in data["git"]["last_10"]:
        git_rows += f"<tr><td>{_e(entry)}</td></tr>"

    body = f"""
<div class="hero">
    <h1>{name}</h1>
    <p class="subtitle">{t("scan_report.subtitle", lang).format(date=date)}</p>
    <div class="grid" style="max-width:600px;margin:20px auto 0">
        <div class="metric"><div class="metric-value" style="color:var(--{sc})">{score}</div><div class="metric-label">{t("common.risk_score_short", lang)}</div></div>
        <div class="metric"><div class="metric-value">{total_files}</div><div class="metric-label">{t("common.source_files", lang)}</div></div>
        <div class="metric"><div class="metric-value">{total_loc:,}</div><div class="metric-label">{t("common.lines_of_code", lang)}</div></div>
        <div class="metric"><div class="metric-value">{len(data['endpoints'])}</div><div class="metric-label">{t("common.endpoints_short", lang)}</div></div>
    </div>
</div>

<h2>{t("scan_report.risk_breakdown", lang)}</h2>
<div class="{'warn' if score <= 50 else 'note'}"><strong>{score}/100 — {_e(_risk_narrative(score, data, lang))}</strong></div>
<table><tr><th>{t("headers.dimension", lang)}</th><th>{t("headers.score", lang)}</th><th>{t("headers.evidence", lang)}</th></tr>{score_rows}</table>

{"".join(_render_executive_verdict(score, data, lang))}

<h2>{t("scan_report.languages", lang)}</h2>
<table><tr><th>{t("headers.language", lang)}</th><th>{t("headers.files", lang)}</th><th>{t("headers.lines", lang)}</th></tr>{langs_rows}</table>

<h2>{t("scan_report.endpoints_title", lang).format(count=len(data['endpoints']))}</h2>
{"<table><tr><th>" + t("headers.method", lang) + "</th><th>" + t("headers.path", lang) + "</th><th>" + t("headers.source", lang) + "</th></tr>" + endpoints_rows + "</table>" if endpoints_rows else '<p class="note">' + t("scan_report.no_endpoints", lang) + '</p>'}

<h2>{t("scan_report.database_title", lang).format(tables=len(data['database']['tables']), migrations=len(data['database']['migrations']))}</h2>
{"<table><tr><th>" + t("headers.table", lang) + "</th><th>" + t("headers.source", lang) + "</th></tr>" + tables_rows + "</table>" if tables_rows else '<p class="note">' + t("scan_report.no_tables", lang) + '</p>'}

<h2>{t("scan_report.authentication", lang)}</h2>
<div class="card">
    <p><strong>{t("scan_report.auth_method", lang)}</strong> {_e(data['auth']['method'])}</p>
    <p><strong>{t("scan_report.auth_mfa", lang)}</strong> {'<span class="badge badge-green">' + t("common.detected", lang) + '</span>' if data['auth']['mfa'] else '<span class="badge badge-red">' + t("common.not_detected", lang) + '</span>'}</p>
    <p><strong>{t("scan_report.auth_rbac", lang)}</strong> {'<span class="badge badge-green">' + t("common.detected", lang) + '</span>' if data['auth']['rbac'] else '<span class="badge badge-red">' + t("common.not_detected", lang) + '</span>'}</p>
    <p class="evidence" style="margin-top:8px">{t("scan_report.auth_evidence", lang)} {', '.join(data['auth']['evidence'][:5]) or '—'}</p>
</div>

<h2>{t("scan_report.security_controls", lang)}</h2>
<table><tr><th>{t("headers.control", lang)}</th><th>{t("headers.status", lang)}</th><th>{t("headers.evidence", lang)}</th></tr>{sec_rows}</table>

<h2>{t("scan_report.integrations_title", lang).format(count=len(data['integrations']))}</h2>
{"<table><tr><th>" + t("headers.service", lang) + "</th><th>" + t("headers.source", lang) + "</th></tr>" + integrations_rows + "</table>" if integrations_rows else '<p class="note">' + t("scan_report.no_integrations", lang) + '</p>'}

<h2>{t("scan_report.tests", lang)}</h2>
<div class="card">
    <p><strong>{t("scan_report.test_files", lang)}</strong> {data['tests']['test_files']}</p>
    <p><strong>{t("scan_report.source_files", lang)}</strong> {data['tests']['source_files']}</p>
    <p><strong>{t("scan_report.ratio", lang)}</strong> {int(data['tests']['test_files'] / max(1, data['tests']['source_files']) * 100)}%</p>
</div>

<h2>{t("scan_report.deps_title", lang).format(count=data['dependencies']['total'], manager=_e(data['dependencies']['manager']))}</h2>
{"<table><tr><th>" + t("headers.package", lang) + "</th><th>" + t("headers.version", lang) + "</th></tr>" + deps_rows + "</table>" if deps_rows else '<p class="note">' + t("scan_report.no_deps", lang) + '</p>'}

<h2>{t("scan_report.code_health", lang).format(count=data['health']['todos'])}</h2>
{"<table><tr><th>" + t("headers.location", lang) + "</th><th>" + t("headers.content", lang) + "</th></tr>" + todos_rows + "</table>" if todos_rows else '<p class="badge badge-green">' + t("scan_report.no_todos", lang) + '</p>'}

<h2>{t("scan_report.git_history", lang)}</h2>
<div class="card">
    <p><strong>{t("scan_report.total_commits", lang)}</strong> {data['git']['commits']}</p>
    <p><strong>{t("scan_report.contributors", lang)}</strong> {', '.join(data['git']['contributors'][:10]) or t("common.na", lang)}</p>
    <p><strong>{t("scan_report.last_30_days", lang)}</strong> {data['git']['recent_commits']} {t("scan_report.commits_suffix", lang)}</p>
</div>
<h3>{t("scan_report.recent_commits", lang)}</h3>
{"<table><tr><th>" + t("headers.commit", lang) + "</th></tr>" + git_rows + "</table>" if git_rows else '<p class="note">' + t("scan_report.no_git", lang) + '</p>'}
"""
    return _wrap_html(f"{t('scan_report.title', lang)} — {name}", body, lang)


def render_sales_datasheet(data, lang="pt-BR", target=None):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    score, _ = _risk_score(data, lang)

    total_files = sum(v["files"] for v in data["languages"].values())
    total_loc = sum(v["lines"] for v in data["languages"].values())
    langs = ", ".join(sorted(data["languages"].keys(), key=lambda x: -data["languages"][x]["files"]))

    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = len(data["security"])

    features = ""
    seen_dirs = set()
    for ep in data["endpoints"]:
        dir_name = ep["file"].split("/")[0] if "/" in ep["file"] else "core"
        if dir_name not in seen_dirs and len(seen_dirs) < 10:
            seen_dirs.add(dir_name)
            module_eps = [e for e in data["endpoints"] if e["file"].startswith(dir_name)]
            features += f"""
            <div class="card">
                <h3 style="color:var(--accent);margin-top:0">{_e(dir_name.replace('-', ' ').replace('_', ' ').title())}</h3>
                <p>{t("sales.endpoints_detected", lang).format(count=len(module_eps))}</p>
                <p class="evidence">Source: {_e(dir_name)}/</p>
            </div>"""

    integrations_list = ""
    for integ in data["integrations"][:10]:
        integrations_list += f'<span class="badge badge-blue">{_e(integ["service"])}</span> '

    limitations = ""
    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    if tf == 0 and sf > 0:
        limitations += f"<li><strong>{t('sales.limitation_zero_tests', lang).format(sf=sf)}</strong></li>"
    elif sf > 0:
        ratio = int(tf / sf * 100)
        if ratio < 20:
            limitations += f"<li>{t('sales.limitation_low_tests', lang).format(ratio=ratio, tf=tf, sf=sf)}</li>"
    if not data["auth"]["mfa"]:
        limitations += f"<li>{t('sales.limitation_no_mfa', lang)}</li>"
    for control, info in data["security"].items():
        if not info["detected"]:
            limitations += f"<li>{control.replace('_', ' ').title()}: {t('common.not_detected', lang)}</li>"
    contributors = len(data["git"]["contributors"])
    if contributors <= 2:
        limitations += f"<li>{t('sales.limitation_bus_factor', lang).format(contributors=contributors)}</li>"
    limitations += f"<li>{t('sales.limitation_sla', lang)}</li>"

    body = f"""
<div class="hero" style="border-color:var(--accent)">
    <p style="color:var(--accent);font-size:13px;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px">{company}</p>
    <h1 style="font-size:36px">{name}</h1>
    <p class="subtitle" style="font-size:14px;max-width:700px;margin:0 auto">{_product_description(data, lang)}</p>
    <div class="grid" style="max-width:800px;margin:24px auto 0">
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{len(data['endpoints'])}</div><div class="metric-label">API {t("common.endpoints_short", lang)}</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{len(data['database']['tables'])}</div><div class="metric-label">Data Tables</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{len(data['integrations'])}</div><div class="metric-label">{t("sales.integrations", lang)}</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--{_score_color(score)})">{score}/100</div><div class="metric-label">{t("common.risk_score_short", lang)}</div></div>
    </div>
    <p style="margin-top:16px;font-size:13px;color:var(--fg2)">{_e(_risk_narrative(score, data, lang))}</p>
</div>

<h2>{t("sales.overview", lang)}</h2>
<div class="card">
    <table style="margin:0">
        <tr><td><strong>{t("sales.stack", lang)}</strong></td><td>{langs}</td></tr>
        <tr><td><strong>{t("sales.codebase", lang)}</strong></td><td>{t("sales.codebase_value", lang).format(files=total_files, loc=f"{total_loc:,}")}</td></tr>
        <tr><td><strong>{t("sales.database", lang)}</strong></td><td>{t("sales.database_value", lang).format(tables=len(data['database']['tables']), migrations=len(data['database']['migrations']))}</td></tr>
        <tr><td><strong>{t("sales.authentication", lang)}</strong></td><td>{_e(data['auth']['method'])}</td></tr>
        <tr><td><strong>{t("sales.contributors", lang)}</strong></td><td>{len(data['git']['contributors'])}</td></tr>
        <tr><td><strong>{t("sales.maturity", lang)}</strong></td><td>{t("sales.maturity_value", lang).format(commits=data['git']['commits'])}</td></tr>
    </table>
</div>

{_sales_target_note(target, name, lang)}

<h2>{t("sales.modules", lang)}</h2>
{features if features else '<p class="note">' + t("sales.modules_note", lang) + '</p>'}

<h2>{t("sales.integrations", lang)}</h2>
<div class="card">
    {integrations_list if integrations_list else '<p>' + t("scan_report.no_integrations_source", lang) + '</p>'}
</div>

<h2>{t("sales.security_overview", lang)}</h2>
<div class="card">
    <p><strong>{t("sales.auth_label", lang)}</strong> {_e(data['auth']['method'])}</p>
    <p><strong>{t("sales.controls_label", lang)}</strong> {t("sales.controls_value", lang).format(count=sec_count, total=sec_total)}</p>
    <p><strong>{t("sales.mfa_label", lang)}</strong> {t("sales.mfa_supported", lang) if data['auth']['mfa'] else t("common.not_detected", lang)}</p>
    <p><strong>{t("sales.rbac_label", lang)}</strong> {t("sales.mfa_supported", lang) if data['auth']['rbac'] else t("common.not_detected", lang)}</p>
</div>

<h2>{t("sales.honest_limitations", lang)}</h2>
<div class="warn">
    <strong>{t("sales.limitations_intro", lang)}</strong>
    <ul style="margin-top:8px">
        {limitations}
    </ul>
    <p style="margin-top:8px;font-size:12px;color:var(--fg2)">{t("sales.limitations_note", lang)}</p>
</div>

<h2>{t("sales.whats_included", lang)}</h2>
<div class="card">
  <table style="margin:0">
    <tr><th>{t("headers.deliverable", lang)}</th><th>{t("headers.value_for_client", lang)}</th></tr>
    <tr><td>Scan Report</td><td>{t("sales.scan_report_value", lang)}</td></tr>
    <tr><td>Technical Spec</td><td>{t("sales.tech_spec_value", lang)}</td></tr>
    <tr><td>Migration Plan</td><td>{t("sales.migration_value", lang)}</td></tr>
    <tr><td>Sales Datasheet</td><td>{t("sales.sales_value", lang)}</td></tr>
    <tr><td>Decision Brief</td><td>{t("sales.decision_brief_value", lang)}</td></tr>
  </table>
</div>
<div class="note">
  <strong>{t("sales.value_prop_label", lang)}</strong> {t("sales.value_prop", lang)}
</div>

<h2>{t("sales.next_steps", lang)}</h2>
<p class="note">{t("sales.next_steps_note", lang)}</p>
"""
    return _wrap_html(f"{name} — {t('sales.title', lang)}", body, lang)


def render_technical_spec(data, lang="pt-BR", target=None):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    score, score_details = _risk_score(data, lang)

    total_files = sum(v["files"] for v in data["languages"].values())
    total_loc = sum(v["lines"] for v in data["languages"].values())
    langs = ", ".join(sorted(data["languages"].keys(), key=lambda x: -data["languages"][x]["files"]))

    langs_str = ", ".join(sorted(data["languages"].keys(), key=lambda x: -data["languages"][x]["files"]))
    if data["dependencies"]["manager"] == "npm":
        hosting = t("tech_spec.a_hosting_web", lang).format(langs=langs_str)
    elif any(fw["name"] in ("WinForms", "WPF") for fw in data.get("migration", {}).get("frameworks", [])):
        hosting = t("tech_spec.a_hosting_desktop", lang).format(langs=langs_str)
    else:
        hosting = t("tech_spec.a_hosting_generic", lang).format(langs=langs_str)
    data_flow = t("tech_spec.a_data_flow", lang).format(tables=len(data["database"]["tables"]), integrations=len(data["integrations"]))
    integration = t("tech_spec.a_integration", lang).format(endpoints=len(data["endpoints"]), method=data["auth"]["method"])
    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    security_summary = t("tech_spec.a_security", lang).format(count=sec_count, total=len(data["security"]))

    ep_rows = ""
    for ep in data["endpoints"][:60]:
        ep_rows += f"<tr><td><code>{_e(ep['method'])}</code></td><td><code>{_e(ep['path'])}</code></td><td class='evidence'>{_e(ep['file'])}:{ep['line']}</td></tr>"

    sec_rows = ""
    for control, info in data["security"].items():
        label = control.replace("_", " ").title()
        status = _status_badge(info["detected"], lang)
        evidence = ", ".join(f"{f}" for f in info["files"][:3]) if info["files"] else "—"
        sec_rows += f"<tr><td>{label}</td><td>{status}</td><td class='evidence'>{_e(evidence)}</td></tr>"

    db_rows = ""
    for tbl in data["database"]["tables"]:
        db_rows += f"<tr><td><code>{_e(tbl['name'])}</code></td><td class='evidence'>{_e(tbl['file'])}:{tbl['line']}</td></tr>"

    integ_rows = ""
    for integ in data["integrations"]:
        integ_rows += f"<tr><td>{_e(integ['service'])}</td><td class='evidence'>{_e(integ['file'])}:{integ['line']}</td></tr>"

    dep_rows = ""
    for dep in data["dependencies"]["items"][:30]:
        dep_rows += f"<tr><td>{_e(dep['name'])}</td><td>{_e(dep['version'])}</td></tr>"

    gaps = ""
    gap_items = []
    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    if tf == 0 and sf > 0:
        gap_items.append((t("tech_spec.automated_tests", lang), f"0 tests / {sf} source files", t("tech_spec.gap_zero_tests", lang)))
    elif sf > 0 and tf / sf < 0.1:
        gap_items.append((t("tech_spec.test_coverage", lang), f"{int(tf/sf*100)}% ({tf}/{sf})", t("tech_spec.gap_low_tests", lang)))
    if not data["auth"]["mfa"]:
        gap_items.append(("MFA/2FA", t("tech_spec.gap_not_detected", lang), t("tech_spec.gap_no_mfa", lang)))
    for control, info in data["security"].items():
        if not info["detected"]:
            gap_items.append((control.replace("_", " ").title(), t("tech_spec.gap_not_detected", lang), t("tech_spec.gap_verify", lang)))
    contributors = len(data["git"]["contributors"])
    if contributors <= 2:
        gap_items.append((t("tech_spec.bus_factor", lang), f"{contributors} contributor(s)", t("tech_spec.gap_bus_factor", lang)))
    gap_items.append((t("tech_spec.gap_sla_label", lang), t("tech_spec.gap_not_in_code", lang), t("tech_spec.gap_sla", lang)))
    gap_items.append((t("tech_spec.gap_hosting_label", lang), t("tech_spec.gap_not_in_code", lang), t("tech_spec.gap_hosting", lang)))

    for label, status, note in gap_items:
        gaps += f"<tr><td>{label}</td><td><span class='badge badge-red'>{status}</span></td><td>{note}</td></tr>"

    body = f"""
<div class="hero" style="border-color:var(--accent2)">
    <p style="color:var(--accent2);font-size:11px;text-transform:uppercase;letter-spacing:3px;margin-bottom:12px">{t("tech_spec.confidential", lang)}</p>
    <h1>{name}</h1>
    <p class="subtitle">{company} — {t("tech_spec.generated", lang).format(date=date)}</p>
</div>

<h2>{t("tech_spec.six_answers", lang)}</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div class="card"><h3>{t("tech_spec.q_where", lang)}</h3><p>{hosting}</p></div>
    <div class="card"><h3>{t("tech_spec.q_data_flow", lang)}</h3><p>{data_flow}</p></div>
    <div class="card"><h3>{t("tech_spec.q_integrate", lang)}</h3><p>{integration}</p></div>
    <div class="card"><h3>{t("tech_spec.q_security", lang)}</h3><p>{security_summary}</p></div>
    <div class="card"><h3>{t("tech_spec.q_sla", lang)}</h3><p>{t("tech_spec.a_sla", lang)}</p></div>
    <div class="card"><h3>{t("tech_spec.q_it_provision", lang)}</h3><p>{t("tech_spec.a_it_provision", lang)}</p></div>
</div>

<h2>{t("tech_spec.architecture", lang)}</h2>
<div class="card">
    <table style="margin:0">
        <tr><th>{t("headers.layer", lang)}</th><th>{t("headers.technology", lang)}</th><th>{t("headers.evidence", lang)}</th></tr>
        {"".join(f"<tr><td>{_e(l).title()}</td><td>{info['files']} files</td><td>{info['lines']:,} lines</td></tr>" for l, info in sorted(data['languages'].items(), key=lambda x: -x[1]['files']))}
    </table>
</div>
<div class="card">
    <h3>{t("tech_spec.directory_structure", lang)}</h3>
    <pre style="color:var(--fg2);font-size:12px">{chr(10).join(_e(d) for d in data['structure'][:20])}</pre>
</div>

<h2>{t("tech_spec.api_reference", lang).format(count=len(data['endpoints']))}</h2>
{"<table><tr><th>" + t("headers.method", lang) + "</th><th>" + t("headers.path", lang) + "</th><th>" + t("headers.source", lang) + "</th></tr>" + ep_rows + "</table>" if ep_rows else '<p class="note">' + t("scan_report.no_endpoints", lang) + '</p>'}

<h2>{t("tech_spec.data_model", lang).format(count=len(data['database']['tables']))}</h2>
{"<table><tr><th>" + t("headers.table", lang) + "</th><th>" + t("headers.source", lang) + "</th></tr>" + db_rows + "</table>" if db_rows else '<p class="note">' + t("scan_report.no_tables", lang) + '</p>'}

<h2>{t("tech_spec.auth_title", lang)}</h2>
<div class="card">
    <table style="margin:0">
        <tr><td><strong>{t("headers.method", lang)}</strong></td><td>{_e(data['auth']['method'])}</td></tr>
        <tr><td><strong>MFA/2FA</strong></td><td>{t("common.detected", lang) if data['auth']['mfa'] else t("common.not_detected", lang)}</td></tr>
        <tr><td><strong>RBAC</strong></td><td>{t("common.detected", lang) if data['auth']['rbac'] else t("common.not_detected", lang)}</td></tr>
        <tr><td><strong>{t("headers.evidence", lang)}</strong></td><td class="evidence">{', '.join(data['auth']['evidence'][:5]) or '—'}</td></tr>
    </table>
</div>

<h2>{t("tech_spec.security_matrix", lang)}</h2>
<table><tr><th>{t("headers.control", lang)}</th><th>{t("headers.status", lang)}</th><th>{t("headers.evidence", lang)}</th></tr>{sec_rows}</table>

<h2>{t("tech_spec.ext_services", lang)}</h2>
{"<table><tr><th>" + t("headers.service", lang) + "</th><th>" + t("headers.source", lang) + "</th></tr>" + integ_rows + "</table>" if integ_rows else '<p class="note">' + t("scan_report.no_integrations", lang) + '</p>'}
<p class="note">{t("tech_spec.ext_services_note", lang)}</p>

<h2>{t("scan_report.deps_title", lang).format(count=data['dependencies']['total'], manager=_e(data['dependencies']['manager']))}</h2>
{"<table><tr><th>" + t("headers.package", lang) + "</th><th>" + t("headers.version", lang) + "</th></tr>" + dep_rows + "</table>" if dep_rows else '<p class="note">' + t("scan_report.no_deps", lang) + '</p>'}

<h2>{t("tech_spec.risk_score_title", lang).format(score=score)}</h2>
<div class="{'warn' if score <= 50 else 'note'}"><strong>{_e(_risk_narrative(score, data, lang))}</strong></div>
<table><tr><th>{t("headers.dimension", lang)}</th><th>{t("headers.score", lang)}</th><th>{t("headers.evidence", lang)}</th></tr>
{"".join(f"<tr><td>{label}</td><td><span class='badge badge-{_score_color(val)}'>{val}/100</span></td><td class='evidence'>{_e(ev)}</td></tr>" for label, val, ev in score_details)}
</table>

<h2>{t("tech_spec.known_gaps", lang)}</h2>
<div class="warn">
    <strong>{t("tech_spec.gaps_intro", lang)}</strong>
</div>
{"<table><tr><th>" + t("headers.gap", lang) + "</th><th>" + t("headers.status", lang) + "</th><th>" + t("headers.impact", lang) + "</th></tr>" + gaps + "</table>"}

{_render_audit_readiness(data, lang)}

<h2>{t("tech_spec.sla_dr", lang)}</h2>
<p class="note">{t("sla.subtitle", lang)}</p>
{_render_sla_by_size(lang)}

<h2>{t("tech_spec.release_compat", lang)}</h2>
<div class="card">
    <p><strong>{t("tech_spec.commits_label", lang)}</strong> {data['git']['commits']}</p>
    <p><strong>{t("tech_spec.active_contributors", lang)}</strong> {len(data['git']['contributors'])}</p>
    <p><strong>{t("tech_spec.recent_activity", lang)}</strong> {t("tech_spec.recent_activity_value", lang).format(count=data['git']['recent_commits'])}</p>
    <p>{t("tech_spec.release_note", lang)}</p>
    {_techspec_target_note(target, lang)}
</div>
"""
    return _wrap_html(f"{name} — {t('tech_spec.title', lang)}", body, lang)


def render_migration_plan(data, plan, lang="pt-BR"):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    summary = plan["summary"]

    severity_colors = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "amber", "LOW": "blue"}
    complexity_colors = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
    quadrant_colors = {"QUICK_WIN": "green", "MAJOR_PROJECT": "yellow", "FILL_IN": "blue", "AVOID": "red"}

    blocker_rows = ""
    for b in plan["blockers"]:
        sev = b.get("severity", "LOW")
        color = severity_colors.get(sev, "blue")
        blocker_rows += f"""<tr>
            <td><span class="badge badge-{color}">{_e(sev)}</span></td>
            <td><strong>{_e(b.get('type', ''))}</strong></td>
            <td>{_e(b.get('description', ''))}</td>
            <td>{_e(b.get('recommendation', ''))}</td>
            <td>{b.get('files_affected', '—')}</td>
        </tr>"""

    module_rows = ""
    for mod in plan["modules"]:
        cx = mod["complexity"]
        pr = mod["priority"]
        cx_color = complexity_colors.get(cx["level"], "blue")
        pr_color = quadrant_colors.get(pr["quadrant"], "blue")
        module_rows += f"""<tr>
            <td><strong>{_e(mod['name'])}</strong><br><span class="evidence">{_e(mod['path'])}</span></td>
            <td>{mod.get('files', '—')}</td>
            <td>{mod.get('endpoints', 0)}</td>
            <td><span class="badge badge-{cx_color}">{cx['level']} ({cx['score']})</span></td>
            <td>{cx['story_points']} SP</td>
            <td>~{cx['estimated_hours']}h</td>
            <td><span class="badge badge-{pr_color}">{pr['quadrant'].replace('_', ' ')}</span></td>
        </tr>"""

    phases_html = ""
    for phase in plan["phases"]:
        mod_list = ""
        phase_hours = 0
        for mod in phase["modules"]:
            phase_hours += mod["complexity"]["estimated_hours"]
            mod_list += f"<li>{_e(mod['name'])} — {mod['complexity']['estimated_hours']}h ({mod['complexity']['level']})</li>"

        phases_html += f"""
        <div class="card" style="border-left:3px solid var(--accent2)">
            <h3 style="margin-top:0;color:var(--accent2)">{t("migration.phase_title", lang).format(number=phase['number'], name=_e(phase['name']))}</h3>
            <p><strong>{t("migration.duration", lang)}</strong> {_e(phase['duration'])}</p>
            <p><strong>{t("migration.goal", lang)}</strong> {_e(phase['goal'])}</p>
            <p><strong>{t("migration.success_criteria", lang)}</strong> {_e(phase['success_criteria'])}</p>
            {"<p><strong>" + t("migration.estimated_effort_label", lang) + "</strong> " + str(phase_hours) + "h</p>" if phase_hours else ""}
            {"<ul>" + mod_list + "</ul>" if mod_list else "<p class='evidence'>" + t("migration.no_modules_assigned", lang) + "</p>"}
        </div>"""

    erp_html = ""
    for erp_name, plan_data in plan.get("erp_plans", {}).items():
        apis_list = "".join(f"<li>{_e(api)}</li>" for api in plan_data.get("apis", []))
        risks_list = "".join(f"<li>{_e(risk)}</li>" for risk in plan_data.get("risks", []))
        erp_html += f"""
        <div class="card">
            <h3 style="margin-top:0;color:var(--accent)">{_e(erp_name)}</h3>
            <table style="margin:0">
                <tr><td><strong>{t("migration.erp_pattern", lang)}</strong></td><td>{_e(plan_data.get('pattern', ''))}</td></tr>
                <tr><td><strong>{t("migration.erp_auth", lang)}</strong></td><td>{_e(plan_data.get('auth', ''))}</td></tr>
                <tr><td><strong>{t("headers.recommendation", lang)}</strong></td><td>{_e(plan_data.get('recommendation', ''))}</td></tr>
            </table>
            <h4 style="margin-top:12px">{t("migration.erp_available_apis", lang)}</h4>
            <ul>{apis_list}</ul>
            <h4>{t("migration.erp_risks", lang)}</h4>
            <ul>{risks_list}</ul>
        </div>"""

    quick_wins = [m for m in plan["modules"] if m["priority"]["quadrant"] == "QUICK_WIN"]
    major = [m for m in plan["modules"] if m["priority"]["quadrant"] == "MAJOR_PROJECT"]
    defer = [m for m in plan["modules"] if m["priority"]["quadrant"] == "AVOID"]
    qw_hours = sum(m["complexity"]["estimated_hours"] for m in quick_wins)
    mj_hours = sum(m["complexity"]["estimated_hours"] for m in major)
    proxy_name = "YARP" if _is_dotnet_project(data) else "Nginx/Traefik"

    ti = summary.get("target_info") or {}
    ti_label = _e(ti.get("label", summary["target_platform"]))
    ti_frontend = _e(ti.get("frontend", "—"))
    ti_backend = _e(ti.get("backend", "—"))
    ti_orm = _e(ti.get("orm", "—"))
    ti_best = _e(ti.get("best_for", "—"))
    ti_pros = "".join(f"<li>{_e(p)}</li>" for p in ti.get("pros", []))
    ti_cons = "".join(f"<li>{_e(c)}</li>" for c in ti.get("cons", []))
    ri = summary.get("recommended_info") or {}

    body = f"""
<div class="hero" style="border-color:var(--accent)">
    <p style="color:var(--accent);font-size:11px;text-transform:uppercase;letter-spacing:3px;margin-bottom:12px">{t("migration.hero_label", lang)}</p>
    <h1>{name}</h1>
    <p class="subtitle">{company} — {t("tech_spec.generated", lang).format(date=date)}</p>
    <div class="grid" style="max-width:800px;margin:24px auto 0">
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{summary['total_modules']}</div><div class="metric-label">{t("common.modules", lang)}</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{summary['total_hours']:,}h</div><div class="metric-label">{t("common.estimated_effort", lang)}</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--{'red' if summary['critical_blockers'] > 0 else 'green'})">{summary['critical_blockers']}</div><div class="metric-label">{t("common.critical_blockers", lang)}</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent2)">{len(summary['erp_integrations'])}</div><div class="metric-label">{t("common.erp_integrations", lang)}</div></div>
    </div>
</div>

<h2>{t("migration.exec_summary", lang)}</h2>
{"<div class='card' style='border-left:3px solid var(--accent);padding:20px'><p style='font-size:16px;color:#fff;margin-bottom:12px'><strong>Recommendation:</strong> Migrate backend to <strong>" + _e(ri.get('backend', '')) + "</strong>, keeping <strong>" + _e(ri.get('frontend', '')) + "</strong> frontend. " + str(summary['total_modules']) + " modules, " + f"{summary['total_hours']:,}" + "h estimated effort (~" + str(summary['total_weeks']) + " weeks), " + str(summary['critical_blockers']) + " blockers to resolve first.</p><p class='evidence'>" + _e(summary.get('recommended_reason', '')) + "</p></div>" if summary.get("is_neutral") else ""}
<div class="card">
    <table style="margin:0">
        <tr><td><strong>{t("headers.current_platform", lang)}</strong></td><td>{', '.join(summary['current_frameworks']) or _e(', '.join(data.get('languages', {}).keys()))}</td></tr>
        <tr><td><strong>{t("headers.recommended_target", lang)}</strong></td><td>{ti_label if not summary.get('is_neutral') else _e(ri.get('label', summary['target_platform']))}</td></tr>
        <tr><td><strong>{t("headers.total_modules", lang)}</strong></td><td>{summary['total_modules']}</td></tr>
        <tr><td><strong>{t("common.estimated_effort", lang)}</strong></td><td>{summary['total_hours']:,}h (~{summary['total_weeks']} weeks)</td></tr>
        <tr><td><strong>{t("headers.quick_wins", lang)}</strong></td><td>{len(quick_wins)} modules ({qw_hours}h) — {t("migration.start_here", lang)}</td></tr>
        <tr><td><strong>{t("headers.major_projects", lang)}</strong></td><td>{len(major)} modules ({mj_hours}h) — {t("migration.plan_carefully", lang)}</td></tr>
        <tr><td><strong>{t("headers.defer_avoid", lang)}</strong></td><td>{len(defer)} modules — {t("migration.validate_before", lang)}</td></tr>
        <tr><td><strong>{t("headers.blockers", lang)}</strong></td><td><span class="badge badge-{'red' if summary['critical_blockers'] > 0 else 'green'}">{summary['critical_blockers']} {t("migration.to_resolve", lang)}</span></td></tr>
        <tr><td><strong>{t("common.erp_integrations", lang)}</strong></td><td>{', '.join(summary['erp_integrations']) or t("common.none_detected", lang)}</td></tr>
    </table>
</div>

{_target_summary_html(summary['target_key'], lang) if not summary.get('is_neutral') else _neutral_note_html(lang)}

<div class="card" style="border-left:3px solid var(--green)">
  <h3 style="margin-top:0;color:var(--green)">{t("migration.roi_title", lang)}</h3>
  <table style="margin:0">
    <tr><th>{t("headers.scenario", lang)}</th><th>{t("headers.estimated_cost", lang)}</th><th>{t("headers.risk", lang)}</th></tr>
    <tr>
      <td><strong>{t("migration.roi_full", lang).format(weeks=summary['total_weeks'])}</strong></td>
      <td>{t("migration.roi_full_cost", lang).format(hours=f"{summary['total_hours']:,}")}</td>
      <td><span class="badge badge-green">{t("badges.controlled_risk", lang)}</span></td>
    </tr>
    <tr>
      <td><strong>{t("migration.roi_no_migrate", lang)}</strong></td>
      <td>{t("migration.roi_no_migrate_cost", lang).format(blockers=summary['critical_blockers'])}</td>
      <td><span class="badge badge-red">{t("badges.growing_risk", lang)}</span></td>
    </tr>
    <tr>
      <td><strong>{t("migration.roi_partial", lang).format(weeks=max(1, qw_hours // 40))}</strong></td>
      <td>{t("migration.roi_partial_cost", lang).format(hours=qw_hours)}</td>
      <td><span class="badge badge-yellow">{t("badges.moderate_risk", lang)}</span></td>
    </tr>
  </table>
  <p class="evidence" style="margin-top:12px">{t("migration.roi_note", lang)}</p>
</div>

{"" if summary.get("is_neutral") else f'''<h2>{t("migration.target_platform", lang).format(name=ti_label)}</h2>
<div class="card" style="border-left:3px solid var(--accent)">
    <table style="margin:0">
        <tr><td><strong>{t("headers.frontend", lang)}</strong></td><td>{ti_frontend}</td></tr>
        <tr><td><strong>{t("headers.backend", lang)}</strong></td><td>{ti_backend}</td></tr>
        <tr><td><strong>ORM</strong></td><td>{ti_orm}</td></tr>
        <tr><td><strong>{t("headers.best_for", lang)}</strong></td><td>{ti_best}</td></tr>
    </table>
    <h3 style="margin-top:16px;color:var(--green)">{t("headers.pros", lang)}</h3>
    <ul>{ti_pros}</ul>
    <h3 style="margin-top:12px;color:var(--red)">{t("headers.cons", lang)}</h3>
    <ul>{ti_cons}</ul>
</div>'''}

<h2>{t("migration.migration_options", lang) if summary.get("is_neutral") else t("migration.alternative_targets", lang)}</h2>
{"<div class='card' style='border-left:3px solid var(--green)'><h3 style='margin-top:0;color:var(--green)'>Recommended: " + _e(ri.get('label', '')) + "</h3><p>" + _e(summary.get('recommended_reason', '')) + "</p></div>" if summary.get("is_neutral") else ""}
<table>
    <tr><th>{t("headers.platform", lang)}</th><th>{t("headers.frontend", lang)}</th><th>{t("headers.backend", lang)}</th><th>{t("headers.best_for", lang)}</th><th>{t("headers.pros", lang)}</th><th>{t("headers.cons", lang)}</th></tr>
    {"".join(f'''<tr{"  style='background:rgba(34,197,94,.08);border-left:3px solid var(--green)'" if k == summary.get("target_key") and not summary.get("is_neutral") else ""}><td><strong>{_e(tgt.get("label", k))}</strong>{" <span class='badge badge-green'>" + t("migration.recommended_label", lang) + "</span>" if k == summary.get("recommended_key") and summary.get("is_neutral") else " <span class='badge badge-green'>" + t("migration.selected_label", lang) + "</span>" if k == summary.get("target_key") and not summary.get("is_neutral") else ""}</td><td>{_e(tgt.get("frontend", "—"))}</td><td>{_e(tgt.get("backend", "—"))}</td><td>{_e(tgt.get("best_for", "—"))}</td><td style="font-size:12px">{"<br>".join(_e(p) for p in tgt.get("pros", []))}</td><td style="font-size:12px">{"<br>".join(_e(c) for c in tgt.get("cons", []))}</td></tr>''' for k, tgt in plan.get("all_targets", {}).items())}
</table>

<h2>{t("migration.tech_equiv_map", lang)}</h2>
<div class="note">
    <strong>{t("migration.accuracy_labels", lang)}</strong>
    <span class="badge badge-green">{t("migration.accuracy_green", lang)}</span> {t("migration.accuracy_green_desc", lang)}
    <span class="badge badge-yellow">{t("migration.accuracy_yellow", lang)}</span> {t("migration.accuracy_yellow_desc", lang)}
    <span class="badge badge-red">{t("migration.accuracy_red", lang)}</span> {t("migration.accuracy_red_desc", lang)}
</div>
<table>
    <tr><th>{t("headers.current_tech", lang)}</th><th>{t("headers.target_equiv", lang)}</th><th>{t("headers.conversion_safety", lang)}</th></tr>
    {"".join(f'''<tr><td><strong>{_e(eq["current"])}</strong></td><td>{_e(eq["target"])}</td><td><span class="badge badge-{eq["accuracy"].lower()}">{_e(eq["accuracy_label"])}</span></td></tr>''' for eq in plan.get("equivalences", []))}
</table>
{f'<p class="evidence">' + t("migration.no_tech_mapping", lang) + '</p>' if not plan.get("equivalences") else ""}

{f'''<h2>{t("migration.package_equiv", lang).format(target=_e(plan.get("package_map", [dict()])[0].get("target_ecosystem", "target") if plan.get("package_map") else "target"))}</h2>
<table>
    <tr><th>{t("headers.category", lang)}</th><th>Current (NuGet)</th><th>Target</th><th>{t("headers.safety", lang)}</th></tr>
    {"".join(f'<tr><td>{_e(p["category"])}</td><td><code>{_e(p["current"])}</code></td><td><code>{_e(p["target"])}</code></td><td><span class="badge badge-{p["accuracy"].lower()}">{_e(p["accuracy"])}</span></td></tr>' for p in plan.get("package_map", []))}
</table>''' if plan.get("package_map") else '<div class="note"><strong>' + t("migration.package_equiv_note", lang) + '</strong></div>'}

<h2>{t("migration.blockers_title", lang).format(count=len(plan['blockers']))}</h2>
{"<div class='warn'><strong>" + t("migration.blockers_warning", lang) + "</strong></div>" if plan['blockers'] else ""}
{"<table><tr><th>" + t("headers.severity", lang) + "</th><th>" + t("headers.type", lang) + "</th><th>" + t("headers.description", lang) + "</th><th>" + t("headers.recommendation", lang) + "</th><th>" + t("headers.files", lang) + "</th></tr>" + blocker_rows + "</table>" if blocker_rows else '<p class="badge badge-green">' + t("migration.no_blockers", lang) + '</p>'}

<h2>{t("migration.module_inventory", lang)}</h2>
<div class="note">
    <strong>{t("migration.priority_quadrants", lang)}</strong>
    <span class="badge badge-green">{t("badges.quick_win", lang)}</span> {t("migration.qw_desc", lang)}
    <span class="badge badge-yellow">{t("badges.major_project", lang)}</span> {t("migration.mp_desc", lang)}
    <span class="badge badge-blue">{t("badges.fill_in", lang)}</span> {t("migration.fi_desc", lang)}
    <span class="badge badge-red">{t("badges.avoid", lang)}</span> {t("migration.av_desc", lang)}
</div>
<table>
    <tr><th>{t("headers.module", lang)}</th><th>{t("headers.files", lang)}</th><th>{t("common.endpoints_short", lang)}</th><th>{t("headers.complexity", lang)}</th><th>{t("headers.effort", lang)}</th><th>{t("headers.hours", lang)}</th><th>{t("headers.priority", lang)}</th></tr>
    {module_rows}
</table>

<h2>{t("migration.phased_roadmap", lang)}</h2>
<div class="note">
    <strong>{t("migration.pattern_label", lang)}</strong> {t("migration.pattern_desc_yarp" if _is_dotnet_project(data) else "migration.pattern_desc_nginx", lang)}<br>
    <strong>{t("migration.migration_order_label", lang)}</strong> {t("migration.migration_order", lang)}<br>
    <strong>{t("migration.rollback_label", lang)}</strong> {t("migration.rollback_desc", lang)}
</div>
{phases_html}

{"<h2>" + t("migration.erp_plans", lang) + "</h2>" + erp_html if erp_html else ""}

<h2>{t("migration.recommended_arch", lang)}</h2>
{"" if _is_dotnet_project(data) else "<div class='card'><h3 style='margin-top:0'>" + t("migration.hybrid_period", lang) + "</h3><pre style='color:var(--fg2);font-size:12px'>" + """
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Clients   │────▶│   Reverse Proxy  │────▶│  Modern App      │
│  (Browser)  │     │ (Nginx/Traefik)  │     │  (API + SPA)     │
└─────────────┘     └────────┬─────────┘     └──────────────────┘
                             │
                             │ routes not yet migrated
                             ▼
                    ┌──────────────────┐
                    │   Legacy App     │
                    │  (Current Stack) │
                    └──────────────────┘
""" + "</pre><p class='evidence'>" + t("migration.hybrid_route_migration", lang) + "</p><p class='evidence'>" + t("migration.hybrid_rollback", lang) + "</p></div>"}
{"<div class='card'><h3 style='margin-top:0'>" + t("migration.hybrid_period_dotnet", lang) + "</h3><pre style='color:var(--fg2);font-size:12px'>" + """
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Clients   │────▶│   YARP Reverse   │────▶│  Modern App      │
│  (Browser)  │     │     Proxy        │     │  (API + SPA)     │
└─────────────┘     └────────┬─────────┘     └──────────────────┘
                             │
                             │ routes not yet migrated
                             ▼
                    ┌──────────────────┐
                    │   Legacy App     │
                    │  (MVC/WinForms)  │
                    └──────────────────┘
""" + "</pre><p class='evidence'>" + t("migration.dotnet_adapters", lang) + "</p><p class='evidence'>" + t("migration.dotnet_flags", lang) + "</p></div>" if _is_dotnet_project(data) else ""}

{"<div class='card'><h3 style='margin-top:0'>" + t("migration.erp_arch_title", lang) + "</h3><pre style='color:var(--fg2);font-size:12px'>" + """
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Modern App  │────▶│  API Gateway     │────▶│  SAP        │
│  (API)       │     │  (Auth + Rate    │     │  (OData/RFC)│
└──────────────┘     │   Limiting)      │     └─────────────┘
                     │                  │
                     │                  │────▶┌─────────────┐
                     │                  │     │  TOTVS      │
                     └──────────────────┘     │  (REST API) │
                                              └─────────────┘
""" + "</pre><p class='evidence'>" + t("migration.erp_anti_pattern", lang) + "</p></div>" if plan.get("erp_plans") else ""}

<h2>{t("migration.effort_estimates", lang)}</h2>
<div class="card">
    <table style="margin:0">
        <tr><th>{t("headers.category", lang)}</th><th>{t("common.modules", lang)}</th><th>{t("headers.hours", lang)}</th><th>{t("headers.weeks_1_dev", lang)}</th></tr>
        <tr><td><span class="badge badge-green">{t("badges.quick_win", lang)}</span></td><td>{len(quick_wins)}</td><td>{qw_hours}</td><td>{max(1, qw_hours // 40)}</td></tr>
        <tr><td><span class="badge badge-yellow">{t("badges.major_project", lang)}</span></td><td>{len(major)}</td><td>{mj_hours}</td><td>{max(1, mj_hours // 40)}</td></tr>
        <tr><td><strong>{t("common.total", lang)}</strong></td><td><strong>{summary['total_modules']}</strong></td><td><strong>{summary['total_hours']:,}</strong></td><td><strong>{summary['total_weeks']}</strong></td></tr>
    </table>
    <p class="evidence" style="margin-top:12px">{t("migration.effort_note", lang)}</p>
</div>

<h2>{t("migration.recommendations", lang)}</h2>
<div class="card">
    <ol>
        <li><strong>{t("badges.quick_win", lang)}</strong> — {t("migration.rec_quick_wins", lang).format(count=len(quick_wins), hours=qw_hours)}</li>
        <li><strong>{t("headers.blockers", lang)}</strong> — {t("migration.rec_blockers", lang).format(count=summary['critical_blockers'])}</li>
        <li>{t("migration.rec_extract_dotnet", lang) if _is_dotnet_project(data) else t("migration.rec_extract_generic", lang)}</li>
        <li>{t("migration.rec_strangler", lang).format(proxy=proxy_name)}</li>
        <li>{t("migration.rec_ghost", lang).format(count=len(defer))}</li>
        {"<li>" + t("migration.rec_erp", lang).format(erps=", ".join(summary["erp_integrations"])) + "</li>" if summary['erp_integrations'] else ""}
    </ol>
</div>

{_target_recs_html(summary['target_key'], lang) if not summary.get('is_neutral') else ''}

<h2>{t("migration.next_steps", lang)}</h2>
<table>
  <tr><th>{t("headers.action", lang)}</th><th>{t("headers.responsible", lang)}</th><th>{t("headers.deadline", lang)}</th><th>{t("headers.completion_criteria", lang)}</th></tr>
  <tr>
    <td>{t("migration.ns_validate_priority", lang)}</td>
    <td>{t("migration.ns_validate_responsible", lang)}</td>
    <td>{t("migration.week_1", lang)}</td>
    <td>{t("migration.ns_validate_criteria", lang)}</td>
  </tr>
  <tr>
    <td>{t("migration.ns_calibrate", lang)}</td>
    <td>{t("migration.ns_validate_responsible", lang)}</td>
    <td>{t("migration.week_1", lang)}</td>
    <td>{t("migration.ns_calibrate_criteria", lang).format(hours=f"{summary['total_hours']:,}")}</td>
  </tr>
  {"<tr><td>" + t("migration.ns_resolve_blockers", lang).format(count=summary['critical_blockers']) + "</td><td>" + t("migration.ns_resolve_responsible", lang) + "</td><td>" + t("migration.two_weeks", lang) + "</td><td>" + t("migration.ns_resolve_criteria", lang) + "</td></tr>" if summary['critical_blockers'] > 0 else ""}
  {"<tr><td>" + t("migration.ns_erp_credentials", lang).format(erps=", ".join(summary["erp_integrations"])) + "</td><td>" + t("migration.ns_erp_responsible", lang) + "</td><td>" + t("migration.week_2", lang) + "</td><td>" + t("migration.ns_erp_criteria", lang) + "</td></tr>" if summary['erp_integrations'] else ""}
  {"<tr><td>" + t("migration.ns_proxy", lang) + "</td><td>" + t("migration.ns_proxy_responsible", lang) + "</td><td>" + t("migration.week_1_2", lang) + "</td><td>" + t("migration.ns_proxy_criteria", lang) + "</td></tr>" if _is_dotnet_project(data) else ""}
  <tr>
    <td>{t("migration.ns_metrics", lang)}</td>
    <td>{t("migration.ns_metrics_responsible", lang)}</td>
    <td>{t("migration.week_2", lang)}</td>
    <td>{t("migration.ns_metrics_criteria", lang)}</td>
  </tr>
</table>
"""
    return _wrap_html(f"{name} — {t('migration.title', lang)}", body, lang)


def render_decision_brief(data, plan=None, lang="pt-BR"):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    score, score_details = _risk_score(data, lang)
    sc = _score_color(score)
    verdict = _executive_verdict(score, data, lang)

    tf = data["tests"]["test_files"]
    sf = data["tests"]["source_files"]
    contributors = len(data["git"]["contributors"])
    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = len(data["security"])

    works_well = []
    if data["auth"]["method"] != "NOT DETECTED":
        works_well.append(t("decision.auth_via", lang).format(method=data["auth"]["method"]))
    if data["auth"]["rbac"]:
        works_well.append(t("decision.rbac_access", lang))
    if sec_count >= sec_total * 0.7:
        works_well.append(t("decision.security_controls", lang).format(count=sec_count, total=sec_total))
    if data["git"]["commits"] > 100:
        works_well.append(t("decision.maturity_commits", lang).format(commits=data["git"]["commits"]))
    if len(data["endpoints"]) > 50:
        works_well.append(t("decision.wide_coverage", lang).format(endpoints=len(data["endpoints"])))
    if len(data["integrations"]) > 0:
        works_well.append(t("decision.active_integrations", lang).format(count=len(data["integrations"])))
    if not works_well:
        works_well.append(t("decision.system_functional", lang))

    needs_attention = []
    if tf == 0 and sf > 0:
        needs_attention.append(t("decision.zero_tests", lang).format(sf=sf))
    elif sf > 0 and tf / sf < 0.1:
        needs_attention.append(t("decision.low_tests", lang).format(ratio=int(tf/sf*100)))
    if contributors <= 2:
        needs_attention.append(t("decision.bus_factor_risk", lang).format(contributors=contributors))
    if sec_count < sec_total * 0.7:
        needs_attention.append(t("decision.missing_security", lang).format(missing=sec_total - sec_count))
    ghost_count = len(data.get("ghost_features", []))
    if ghost_count > 0:
        needs_attention.append(t("decision.ghost_features", lang).format(count=ghost_count))
    deprecated_count = len(data.get("deprecated_functions", []))
    if deprecated_count > 0:
        needs_attention.append(t("decision.deprecated_calls", lang).format(count=deprecated_count))
    if not needs_attention:
        needs_attention.append(t("decision.no_critical_gap", lang))

    recommend_now = []
    if tf == 0:
        recommend_now.append(t("decision.implement_tests", lang))
    if contributors <= 2:
        recommend_now.append(t("decision.document_onboarding", lang))
    if sec_count < sec_total * 0.7:
        recommend_now.append(t("decision.implement_security", lang).format(missing=sec_total - sec_count))
    if deprecated_count > 0:
        recommend_now.append(t("decision.eliminate_deprecated", lang))
    if not recommend_now:
        recommend_now.append(t("verdict.action_maintain", lang))

    works_html = "".join(f"<li>{item}</li>" for item in works_well[:5])
    attention_html = "".join(f"<li>{item}</li>" for item in needs_attention[:5])
    recommend_html = "".join(f"<li>{item}</li>" for item in recommend_now[:4])

    scenarios_html = ""
    if plan:
        summary = plan["summary"]
        quick_wins = [m for m in plan["modules"] if m["priority"]["quadrant"] == "QUICK_WIN"]
        qw_hours = sum(m["complexity"]["estimated_hours"] for m in quick_wins)
        target_key = summary.get("target_key", "all")
        migration_label_suffix = ""
        if target_key != "all":
            tl = TARGET_LABELS.get(target_key, {}).get(lang, "")
            if tl:
                migration_label_suffix = f" — {tl}"
        full_label = t("decision.full_migration", lang) + migration_label_suffix
        scenarios_html = f"""
<h2>{t("decision.investment_scenarios", lang)}</h2>
<table>
  <tr><th>{t("headers.scenario", lang)}</th><th>{t("common.estimated_effort", lang)}</th><th>{t("headers.deadline", lang)}</th><th>{t("headers.risk", lang)}</th></tr>
  <tr>
    <td><strong>{full_label}</strong></td>
    <td>{summary['total_hours']:,}h</td>
    <td>{t("decision.weeks_approx", lang).format(weeks=summary['total_weeks'])}</td>
    <td><span class="badge badge-green">{t("decision.controlled", lang)}</span></td>
  </tr>
  <tr>
    <td><strong>{t("decision.keep_legacy", lang)}</strong></td>
    <td>{t("decision.legacy_cost", lang)}</td>
    <td>{t("decision.continuous", lang)}</td>
    <td><span class="badge badge-red">{t("decision.growing", lang)}</span></td>
  </tr>
  <tr>
    <td><strong>{t("decision.partial_migration", lang)}</strong></td>
    <td>{qw_hours}h</td>
    <td>{t("decision.weeks_approx", lang).format(weeks=max(1, qw_hours // 40))}</td>
    <td><span class="badge badge-yellow">{t("decision.moderate", lang)}</span></td>
  </tr>
</table>"""

    actions_items = []
    if tf == 0:
        actions_items.append((t("decision.implement_tests", lang), t("decision.senior_dev", lang), t("decision.thirty_days", lang)))
    if contributors <= 2:
        actions_items.append((t("decision.document_onboarding", lang), t("decision.tech_lead", lang), t("decision.fifteen_days", lang)))
    if sec_count < sec_total * 0.7:
        actions_items.append((t("decision.implement_security", lang).format(missing=sec_total - sec_count), t("decision.senior_dev", lang), t("decision.thirty_days", lang)))
    if deprecated_count > 0:
        actions_items.append((t("decision.eliminate_deprecated", lang), t("decision.backend_dev", lang), t("decision.fifteen_days", lang)))
    if plan and plan["summary"]["critical_blockers"] > 0:
        actions_items.append((t("decision.resolve_blockers", lang).format(count=plan["summary"]["critical_blockers"]), t("decision.senior_dev", lang), t("decision.two_weeks", lang)))
    if not actions_items:
        actions_items.append((t("decision.external_audit", lang), t("decision.ciso_consultancy", lang), t("decision.sixty_days", lang)))

    actions_rows = ""
    for action, responsible, deadline in actions_items[:3]:
        actions_rows += f"<tr><td>{action}</td><td>{responsible}</td><td>{deadline}</td></tr>"

    body = f"""
<div class="hero">
    <h1>{name}</h1>
    <p class="subtitle">{t("decision.title", lang)} — {company} — {date}</p>
    <div class="grid" style="max-width:400px;margin:24px auto 0">
        <div class="metric">
            <div class="metric-value" style="font-size:56px;color:var(--{sc})">{score}</div>
            <div class="metric-label">{t("common.risk_score", lang)}</div>
        </div>
    </div>
    <h3 style="margin-top:20px;color:var(--accent)">{t("verdict.title", lang)}</h3>
    <p style="margin-top:8px;font-size:15px;color:var(--fg);max-width:600px;margin-left:auto;margin-right:auto">{verdict['diagnosis']}</p>
</div>

<div class="grid" style="grid-template-columns:repeat(3,1fr)">
    <div class="card" style="border-top:3px solid var(--green)">
        <h3 style="margin-top:0;color:var(--green)">{t("decision.what_works", lang)}</h3>
        <ul style="padding-left:16px">{works_html}</ul>
    </div>
    <div class="card" style="border-top:3px solid var(--yellow)">
        <h3 style="margin-top:0;color:var(--yellow)">{t("decision.what_needs_attention", lang)}</h3>
        <ul style="padding-left:16px">{attention_html}</ul>
    </div>
    <div class="card" style="border-top:3px solid var(--accent2)">
        <h3 style="margin-top:0;color:var(--accent2)">{t("decision.what_we_recommend", lang)}</h3>
        <ul style="padding-left:16px">{recommend_html}</ul>
    </div>
</div>

{scenarios_html}

<h2>{t("decision.next_3_actions", lang)}</h2>
<table>
  <tr><th>{t("headers.action", lang)}</th><th>{t("headers.responsible", lang)}</th><th>{t("headers.deadline", lang)}</th></tr>
  {actions_rows}
</table>

<div class="footer" style="margin-top:24px;padding-top:16px">
    <p>{t("footer.trust_line", lang)}</p>
    <p style="font-size:11px;color:var(--fg2)">{t("footer.codedocs_tagline", lang)}</p>
</div>
"""
    return _wrap_html(f"{name} — {t('decision.title', lang)}", body, lang)
