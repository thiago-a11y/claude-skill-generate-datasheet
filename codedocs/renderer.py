"""HTML renderer — generates documentation from scan data. Zero dependencies."""

import html


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


def _status_badge(detected):
    if detected:
        return '<span class="badge badge-green">Implemented</span>'
    return '<span class="badge badge-red">Not Detected</span>'


def _score_color(score):
    if score >= 70:
        return "green"
    if score >= 40:
        return "yellow"
    return "red"


def _health_score(data):
    scores = []
    sf = max(1, data["tests"]["source_files"])
    test_ratio = data["tests"]["test_files"] / sf
    scores.append(("Test Coverage", min(100, int(test_ratio * 200)), f"{data['tests']['test_files']}/{sf} files"))

    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = max(1, len(data["security"]))
    scores.append(("Security Controls", int(sec_count / sec_total * 100), f"{sec_count}/{sec_total} controls"))

    loc = max(1, data["health"]["loc"])
    debt = data["health"]["todos"] / (loc / 1000)
    debt_score = max(0, 100 - int(debt * 15))
    scores.append(("Tech Debt", debt_score, f"{data['health']['todos']} items in {loc:,} LOC"))

    doc_score = min(100, len(data["existing_docs"]) * 12)
    scores.append(("Documentation", doc_score, f"{len(data['existing_docs'])} markdown files"))

    contributors = len(data["git"]["contributors"])
    git_score = min(100, contributors * 20) if contributors > 0 else 0
    scores.append(("Team Health", git_score, f"{contributors} contributors"))

    dep_score = 80 if data["dependencies"]["manager"] != "NOT DETECTED" else 20
    scores.append(("Dependency Mgmt", dep_score, data["dependencies"]["manager"]))

    weights = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
    composite = min(100, int(sum(s[1] * w for s, w in zip(scores, weights))))
    return composite, scores


def _wrap_html(title, body, accent="var(--accent)"):
    return f"""<!DOCTYPE html>
<html lang="en">
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
Generated by CodeDocs v1.0 — Offline codebase documentation generator<br>
Zero AI · Zero internet · Zero data egress<br>
{_e(title)} — scanned on {_e(body.split('scan_date_placeholder')[0] if 'scan_date_placeholder' in body else '')}
</div>
</div>
</body>
</html>"""


def render_scan_report(data):
    name = _e(data["project"]["name"])
    date = _e(data["project"]["scan_date"])
    score, score_details = _health_score(data)
    sc = _score_color(score)

    langs_rows = ""
    for lang, info in sorted(data["languages"].items(), key=lambda x: -x[1]["files"]):
        langs_rows += f"<tr><td>{_e(lang)}</td><td>{info['files']}</td><td>{info['lines']:,}</td></tr>"
    total_files = sum(v["files"] for v in data["languages"].values())
    total_loc = sum(v["lines"] for v in data["languages"].values())
    langs_rows += f"<tr><td><strong>TOTAL</strong></td><td><strong>{total_files}</strong></td><td><strong>{total_loc:,}</strong></td></tr>"

    endpoints_rows = ""
    for ep in data["endpoints"][:50]:
        endpoints_rows += f"<tr><td><code>{_e(ep['method'])}</code></td><td>{_e(ep['path'])}</td><td class='evidence'>{_e(ep['file'])}:{ep['line']}</td></tr>"

    tables_rows = ""
    for t in data["database"]["tables"]:
        tables_rows += f"<tr><td>{_e(t['name'])}</td><td class='evidence'>{_e(t['file'])}:{t['line']}</td></tr>"

    sec_rows = ""
    for control, info in data["security"].items():
        label = control.replace("_", " ").title()
        status = _status_badge(info["detected"])
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
    <p class="subtitle">Codebase Scan Report — {date}</p>
    <div class="grid" style="max-width:600px;margin:20px auto 0">
        <div class="metric"><div class="metric-value" style="color:var(--{sc})">{score}</div><div class="metric-label">Health Score</div></div>
        <div class="metric"><div class="metric-value">{total_files}</div><div class="metric-label">Source Files</div></div>
        <div class="metric"><div class="metric-value">{total_loc:,}</div><div class="metric-label">Lines of Code</div></div>
        <div class="metric"><div class="metric-value">{len(data['endpoints'])}</div><div class="metric-label">Endpoints</div></div>
    </div>
</div>

<h2>Health Score Breakdown</h2>
<table><tr><th>Dimension</th><th>Score</th><th>Evidence</th></tr>{score_rows}</table>

<h2>Languages</h2>
<table><tr><th>Language</th><th>Files</th><th>Lines</th></tr>{langs_rows}</table>

<h2>Endpoints ({len(data['endpoints'])} detected)</h2>
{"<table><tr><th>Method</th><th>Path</th><th>Source</th></tr>" + endpoints_rows + "</table>" if endpoints_rows else '<p class="note">No endpoints detected.</p>'}

<h2>Database ({len(data['database']['tables'])} tables, {len(data['database']['migrations'])} migrations)</h2>
{"<table><tr><th>Table</th><th>Source</th></tr>" + tables_rows + "</table>" if tables_rows else '<p class="note">No database tables detected.</p>'}

<h2>Authentication</h2>
<div class="card">
    <p><strong>Method:</strong> {_e(data['auth']['method'])}</p>
    <p><strong>MFA/2FA:</strong> {'<span class="badge badge-green">Detected</span>' if data['auth']['mfa'] else '<span class="badge badge-red">Not Detected</span>'}</p>
    <p><strong>RBAC:</strong> {'<span class="badge badge-green">Detected</span>' if data['auth']['rbac'] else '<span class="badge badge-red">Not Detected</span>'}</p>
    <p class="evidence" style="margin-top:8px">Evidence: {', '.join(data['auth']['evidence'][:5]) or '—'}</p>
</div>

<h2>Security Controls</h2>
<table><tr><th>Control</th><th>Status</th><th>Evidence</th></tr>{sec_rows}</table>

<h2>External Integrations ({len(data['integrations'])})</h2>
{"<table><tr><th>Service</th><th>Source</th></tr>" + integrations_rows + "</table>" if integrations_rows else '<p class="note">No external integrations detected.</p>'}

<h2>Tests</h2>
<div class="card">
    <p><strong>Test files:</strong> {data['tests']['test_files']}</p>
    <p><strong>Source files:</strong> {data['tests']['source_files']}</p>
    <p><strong>Ratio:</strong> {int(data['tests']['test_files'] / max(1, data['tests']['source_files']) * 100)}%</p>
</div>

<h2>Dependencies ({data['dependencies']['total']} — {_e(data['dependencies']['manager'])})</h2>
{"<table><tr><th>Package</th><th>Version</th></tr>" + deps_rows + "</table>" if deps_rows else '<p class="note">No dependency manager detected.</p>'}

<h2>Code Health ({data['health']['todos']} TODOs/FIXMEs)</h2>
{"<table><tr><th>Location</th><th>Content</th></tr>" + todos_rows + "</table>" if todos_rows else '<p class="badge badge-green">No TODOs/FIXMEs found.</p>'}

<h2>Git History</h2>
<div class="card">
    <p><strong>Total commits:</strong> {data['git']['commits']}</p>
    <p><strong>Contributors:</strong> {', '.join(data['git']['contributors'][:10]) or 'N/A'}</p>
    <p><strong>Last 30 days:</strong> {data['git']['recent_commits']} commits</p>
</div>
<h3>Recent Commits</h3>
{"<table><tr><th>Commit</th></tr>" + git_rows + "</table>" if git_rows else '<p class="note">No git history detected.</p>'}
"""
    return _wrap_html(f"Scan Report — {name}", body)


def render_sales_datasheet(data):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    score, _ = _health_score(data)

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
                <p>{len(module_eps)} endpoints detected</p>
                <p class="evidence">Source: {_e(dir_name)}/</p>
            </div>"""

    integrations_list = ""
    for integ in data["integrations"][:10]:
        integrations_list += f'<span class="badge badge-blue">{_e(integ["service"])}</span> '

    limitations = ""
    if not data["auth"]["mfa"]:
        limitations += "<li>MFA/2FA: Not Detected</li>"
    for control, info in data["security"].items():
        if not info["detected"]:
            limitations += f"<li>{control.replace('_', ' ').title()}: Not Detected</li>"
    if data["tests"]["test_files"] == 0:
        limitations += "<li>Automated tests: Not Detected</li>"

    body = f"""
<div class="hero" style="border-color:var(--accent)">
    <p style="color:var(--accent);font-size:13px;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px">{company}</p>
    <h1 style="font-size:36px">{name}</h1>
    <p class="subtitle">[MANUAL — add product description]</p>
    <div class="grid" style="max-width:800px;margin:24px auto 0">
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{len(data['endpoints'])}</div><div class="metric-label">API Endpoints</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{len(data['database']['tables'])}</div><div class="metric-label">Data Tables</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{len(data['integrations'])}</div><div class="metric-label">Integrations</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{score}/100</div><div class="metric-label">Health Score</div></div>
    </div>
</div>

<h2>Overview</h2>
<div class="card">
    <table style="margin:0">
        <tr><td><strong>Stack</strong></td><td>{langs}</td></tr>
        <tr><td><strong>Codebase</strong></td><td>{total_files} files · {total_loc:,} lines of code</td></tr>
        <tr><td><strong>Database</strong></td><td>{len(data['database']['tables'])} tables · {len(data['database']['migrations'])} migrations</td></tr>
        <tr><td><strong>Authentication</strong></td><td>{_e(data['auth']['method'])}</td></tr>
        <tr><td><strong>Contributors</strong></td><td>{len(data['git']['contributors'])}</td></tr>
        <tr><td><strong>Maturity</strong></td><td>{data['git']['commits']} commits</td></tr>
    </table>
</div>

<h2>Modules</h2>
{features if features else '<p class="note">[MANUAL — describe product modules]</p>'}

<h2>Integrations</h2>
<div class="card">
    {integrations_list if integrations_list else '<p>[MANUAL — list integrations]</p>'}
</div>

<h2>Security Overview</h2>
<div class="card">
    <p><strong>Authentication:</strong> {_e(data['auth']['method'])}</p>
    <p><strong>Security controls:</strong> {sec_count}/{sec_total} implemented</p>
    <p><strong>MFA:</strong> {'Supported' if data['auth']['mfa'] else 'Not Detected'}</p>
    <p><strong>RBAC:</strong> {'Supported' if data['auth']['rbac'] else 'Not Detected'}</p>
</div>

<h2>Honest Limitations</h2>
<div class="warn">
    <strong>What this product does NOT have (based on code scan):</strong>
    <ul style="margin-top:8px">
        {limitations if limitations else '<li>No significant gaps detected</li>'}
    </ul>
    <p style="margin-top:8px;font-size:12px;color:var(--fg2)">This section is mandatory. Hiding limitations breaks trust.</p>
</div>

<h2>Commercial Model</h2>
<p class="note">[MANUAL — describe pricing, licensing, and support tiers]</p>

<h2>Next Steps</h2>
<p class="note">[MANUAL — add demo link, contact information, and CTA]</p>
"""
    return _wrap_html(f"{name} — Sales Datasheet", body)


def render_technical_spec(data):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    score, score_details = _health_score(data)

    total_files = sum(v["files"] for v in data["languages"].values())
    total_loc = sum(v["lines"] for v in data["languages"].values())
    langs = ", ".join(sorted(data["languages"].keys(), key=lambda x: -data["languages"][x]["files"]))

    # Quick answers
    hosting = "[MANUAL — describe hosting]"
    data_flow = f"{len(data['database']['tables'])} tables, {len(data['integrations'])} external services"
    integration = f"{len(data['endpoints'])} REST endpoints, auth via {data['auth']['method']}"
    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    security_summary = f"{sec_count}/{len(data['security'])} controls detected"

    # Endpoints table
    ep_rows = ""
    for ep in data["endpoints"][:60]:
        ep_rows += f"<tr><td><code>{_e(ep['method'])}</code></td><td><code>{_e(ep['path'])}</code></td><td class='evidence'>{_e(ep['file'])}:{ep['line']}</td></tr>"

    # Security matrix
    sec_rows = ""
    for control, info in data["security"].items():
        label = control.replace("_", " ").title()
        status = _status_badge(info["detected"])
        evidence = ", ".join(f"{f}" for f in info["files"][:3]) if info["files"] else "—"
        sec_rows += f"<tr><td>{label}</td><td>{status}</td><td class='evidence'>{_e(evidence)}</td></tr>"

    # Database
    db_rows = ""
    for t in data["database"]["tables"]:
        db_rows += f"<tr><td><code>{_e(t['name'])}</code></td><td class='evidence'>{_e(t['file'])}:{t['line']}</td></tr>"

    # Integrations
    integ_rows = ""
    for integ in data["integrations"]:
        integ_rows += f"<tr><td>{_e(integ['service'])}</td><td class='evidence'>{_e(integ['file'])}:{integ['line']}</td></tr>"

    # Dependencies
    dep_rows = ""
    for dep in data["dependencies"]["items"][:30]:
        dep_rows += f"<tr><td>{_e(dep['name'])}</td><td>{_e(dep['version'])}</td></tr>"

    # Known gaps
    gaps = ""
    gap_items = []
    if not data["auth"]["mfa"]:
        gap_items.append(("MFA/2FA", "Not Detected", "Critical for enterprise"))
    for control, info in data["security"].items():
        if not info["detected"]:
            gap_items.append((control.replace("_", " ").title(), "Not Detected", "Security gap"))
    if data["tests"]["test_files"] == 0:
        gap_items.append(("Automated Tests", "0 test files", "Quality risk"))

    for label, status, note in gap_items:
        gaps += f"<tr><td>{label}</td><td><span class='badge badge-red'>{status}</span></td><td>{note}</td></tr>"

    body = f"""
<div class="hero" style="border-color:var(--accent2)">
    <p style="color:var(--accent2);font-size:11px;text-transform:uppercase;letter-spacing:3px;margin-bottom:12px">CONFIDENTIAL — TECHNICAL SPECIFICATION</p>
    <h1>{name}</h1>
    <p class="subtitle">{company} — Generated {date}</p>
</div>

<h2>6 Answers in 60 Seconds</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div class="card"><h3>Where does it run?</h3><p>{hosting}</p></div>
    <div class="card"><h3>How does data flow?</h3><p>{data_flow}</p></div>
    <div class="card"><h3>How do we integrate?</h3><p>{integration}</p></div>
    <div class="card"><h3>Security posture?</h3><p>{security_summary}</p></div>
    <div class="card"><h3>SLA?</h3><p>[MANUAL — uptime, RPO, RTO]</p></div>
    <div class="card"><h3>What does IT provision?</h3><p>[MANUAL — client requirements]</p></div>
</div>

<h2>Architecture</h2>
<div class="card">
    <table style="margin:0">
        <tr><th>Layer</th><th>Technology</th><th>Evidence</th></tr>
        {"".join(f"<tr><td>{_e(lang).title()}</td><td>{info['files']} files</td><td>{info['lines']:,} lines</td></tr>" for lang, info in sorted(data['languages'].items(), key=lambda x: -x[1]['files']))}
    </table>
</div>
<div class="card">
    <h3>Directory Structure</h3>
    <pre style="color:var(--fg2);font-size:12px">{chr(10).join(_e(d) for d in data['structure'][:20])}</pre>
</div>

<h2>API Reference ({len(data['endpoints'])} endpoints)</h2>
{"<table><tr><th>Method</th><th>Path</th><th>Source</th></tr>" + ep_rows + "</table>" if ep_rows else '<p class="note">No endpoints detected.</p>'}

<h2>Data Model ({len(data['database']['tables'])} tables)</h2>
{"<table><tr><th>Table</th><th>Source</th></tr>" + db_rows + "</table>" if db_rows else '<p class="note">No database tables detected.</p>'}

<h2>Authentication &amp; Authorization</h2>
<div class="card">
    <table style="margin:0">
        <tr><td><strong>Method</strong></td><td>{_e(data['auth']['method'])}</td></tr>
        <tr><td><strong>MFA/2FA</strong></td><td>{'Detected' if data['auth']['mfa'] else 'NOT DETECTED'}</td></tr>
        <tr><td><strong>RBAC</strong></td><td>{'Detected' if data['auth']['rbac'] else 'NOT DETECTED'}</td></tr>
        <tr><td><strong>Evidence</strong></td><td class="evidence">{', '.join(data['auth']['evidence'][:5]) or '—'}</td></tr>
    </table>
</div>

<h2>Security Controls Matrix</h2>
<table><tr><th>Control</th><th>Status</th><th>Evidence</th></tr>{sec_rows}</table>

<h2>External Services &amp; Data Residency</h2>
{"<table><tr><th>Service</th><th>Source</th></tr>" + integ_rows + "</table>" if integ_rows else '<p class="note">No external services detected.</p>'}
<p class="note">[MANUAL — confirm data residency regions for each service]</p>

<h2>Dependencies ({data['dependencies']['total']} — {_e(data['dependencies']['manager'])})</h2>
{"<table><tr><th>Package</th><th>Version</th></tr>" + dep_rows + "</table>" if dep_rows else '<p class="note">No dependency manager detected.</p>'}

<h2>Health Score: {score}/100</h2>
<table><tr><th>Dimension</th><th>Score</th><th>Evidence</th></tr>
{"".join(f"<tr><td>{label}</td><td><span class='badge badge-{_score_color(val)}'>{val}/100</span></td><td class='evidence'>{_e(ev)}</td></tr>" for label, val, ev in score_details)}
</table>

<h2>Known Gaps</h2>
<div class="warn">
    <strong>Transparency — what this system does NOT have:</strong>
</div>
{"<table><tr><th>Gap</th><th>Status</th><th>Impact</th></tr>" + gaps + "</table>" if gaps else '<p class="badge badge-green">No significant gaps detected.</p>'}

<h2>SLA &amp; Disaster Recovery</h2>
<p class="note">[MANUAL — define uptime SLA, RPO, RTO, backup frequency, restore process]</p>

<h2>Release &amp; Compatibility</h2>
<div class="card">
    <p><strong>Commits:</strong> {data['git']['commits']}</p>
    <p><strong>Active contributors:</strong> {len(data['git']['contributors'])}</p>
    <p><strong>Recent activity:</strong> {data['git']['recent_commits']} commits in last 30 days</p>
    <p>[MANUAL — release cadence, versioning policy, backward compatibility]</p>
</div>
"""
    return _wrap_html(f"{name} — Technical Specification", body)


def render_migration_plan(data, plan):
    name = _e(data["project"]["name"])
    company = _e(data["project"].get("company", ""))
    date = _e(data["project"]["scan_date"])
    summary = plan["summary"]

    severity_colors = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "amber", "LOW": "blue"}
    complexity_colors = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
    quadrant_colors = {"QUICK_WIN": "green", "MAJOR_PROJECT": "yellow", "FILL_IN": "blue", "AVOID": "red"}

    # Blockers
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

    # Module inventory
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

    # Phases
    phases_html = ""
    for phase in plan["phases"]:
        mod_list = ""
        phase_hours = 0
        for mod in phase["modules"]:
            phase_hours += mod["complexity"]["estimated_hours"]
            mod_list += f"<li>{_e(mod['name'])} — {mod['complexity']['estimated_hours']}h ({mod['complexity']['level']})</li>"

        phases_html += f"""
        <div class="card" style="border-left:3px solid var(--accent2)">
            <h3 style="margin-top:0;color:var(--accent2)">Phase {phase['number']}: {_e(phase['name'])}</h3>
            <p><strong>Duration:</strong> {_e(phase['duration'])}</p>
            <p><strong>Goal:</strong> {_e(phase['goal'])}</p>
            <p><strong>Success criteria:</strong> {_e(phase['success_criteria'])}</p>
            {"<p><strong>Estimated effort:</strong> " + str(phase_hours) + "h</p>" if phase_hours else ""}
            {"<ul>" + mod_list + "</ul>" if mod_list else "<p class='evidence'>No modules assigned — planning phase</p>"}
        </div>"""

    # ERP Integration Plans
    erp_html = ""
    for erp_name, plan_data in plan.get("erp_plans", {}).items():
        apis_list = "".join(f"<li>{_e(api)}</li>" for api in plan_data.get("apis", []))
        risks_list = "".join(f"<li>{_e(risk)}</li>" for risk in plan_data.get("risks", []))
        erp_html += f"""
        <div class="card">
            <h3 style="margin-top:0;color:var(--accent)">{_e(erp_name)}</h3>
            <table style="margin:0">
                <tr><td><strong>Pattern</strong></td><td>{_e(plan_data.get('pattern', ''))}</td></tr>
                <tr><td><strong>Auth</strong></td><td>{_e(plan_data.get('auth', ''))}</td></tr>
                <tr><td><strong>Recommendation</strong></td><td>{_e(plan_data.get('recommendation', ''))}</td></tr>
            </table>
            <h4 style="margin-top:12px">Available APIs</h4>
            <ul>{apis_list}</ul>
            <h4>Risks</h4>
            <ul>{risks_list}</ul>
        </div>"""

    # Effort summary
    quick_wins = [m for m in plan["modules"] if m["priority"]["quadrant"] == "QUICK_WIN"]
    major = [m for m in plan["modules"] if m["priority"]["quadrant"] == "MAJOR_PROJECT"]
    defer = [m for m in plan["modules"] if m["priority"]["quadrant"] == "AVOID"]
    qw_hours = sum(m["complexity"]["estimated_hours"] for m in quick_wins)
    mj_hours = sum(m["complexity"]["estimated_hours"] for m in major)

    body = f"""
<div class="hero" style="border-color:var(--accent)">
    <p style="color:var(--accent);font-size:11px;text-transform:uppercase;letter-spacing:3px;margin-bottom:12px">MIGRATION PLAN</p>
    <h1>{name}</h1>
    <p class="subtitle">{company} — Generated {date}</p>
    <div class="grid" style="max-width:800px;margin:24px auto 0">
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{summary['total_modules']}</div><div class="metric-label">Modules</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent)">{summary['total_hours']:,}h</div><div class="metric-label">Estimated Effort</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--{'red' if summary['critical_blockers'] > 0 else 'green'})">{summary['critical_blockers']}</div><div class="metric-label">Critical Blockers</div></div>
        <div class="metric"><div class="metric-value" style="color:var(--accent2)">{len(summary['erp_integrations'])}</div><div class="metric-label">ERP Integrations</div></div>
    </div>
</div>

<h2>Executive Summary</h2>
<div class="card">
    <table style="margin:0">
        <tr><td><strong>Current Platform</strong></td><td>{', '.join(summary['current_frameworks']) or 'NOT DETECTED'}</td></tr>
        <tr><td><strong>Target Framework</strong></td><td>{_e(summary['target_framework'])}</td></tr>
        <tr><td><strong>Target Platform</strong></td><td>{_e(summary['target_platform']).title()}</td></tr>
        <tr><td><strong>Total Modules</strong></td><td>{summary['total_modules']}</td></tr>
        <tr><td><strong>Estimated Effort</strong></td><td>{summary['total_hours']:,} hours (~{summary['total_weeks']} weeks)</td></tr>
        <tr><td><strong>Quick Wins</strong></td><td>{len(quick_wins)} modules ({qw_hours}h)</td></tr>
        <tr><td><strong>Major Projects</strong></td><td>{len(major)} modules ({mj_hours}h)</td></tr>
        <tr><td><strong>Defer/Avoid</strong></td><td>{len(defer)} modules</td></tr>
        <tr><td><strong>Critical Blockers</strong></td><td><span class="badge badge-{'red' if summary['critical_blockers'] > 0 else 'green'}">{summary['critical_blockers']}</span></td></tr>
        <tr><td><strong>ERP Integrations</strong></td><td>{', '.join(summary['erp_integrations']) or 'None detected'}</td></tr>
    </table>
</div>

<h2>Target Platform: {_e(summary.get('target_info', {}).get('label', summary['target_platform']))}</h2>
<div class="card" style="border-left:3px solid var(--accent)">
    <table style="margin:0">
        <tr><td><strong>Frontend</strong></td><td>{_e(summary.get('target_info', {}).get('frontend', '—'))}</td></tr>
        <tr><td><strong>Backend</strong></td><td>{_e(summary.get('target_info', {}).get('backend', '—'))}</td></tr>
        <tr><td><strong>ORM</strong></td><td>{_e(summary.get('target_info', {}).get('orm', '—'))}</td></tr>
        <tr><td><strong>Best for</strong></td><td>{_e(summary.get('target_info', {}).get('best_for', '—'))}</td></tr>
    </table>
    <h3 style="margin-top:16px;color:var(--green)">Pros</h3>
    <ul>{"".join(f"<li>{_e(p)}</li>" for p in summary.get('target_info', {}).get('pros', []))}</ul>
    <h3 style="margin-top:12px;color:var(--red)">Cons</h3>
    <ul>{"".join(f"<li>{_e(c)}</li>" for c in summary.get('target_info', {}).get('cons', []))}</ul>
</div>

<h3>Alternative Targets</h3>
<table>
    <tr><th>Platform</th><th>Frontend</th><th>Backend</th><th>Best For</th></tr>
    {"".join(f'''<tr><td><strong>{_e(t.get("label", k))}</strong>{"  ← selected" if k == summary.get("target_key") else ""}</td><td>{_e(t.get("frontend", "—"))}</td><td>{_e(t.get("backend", "—"))}</td><td>{_e(t.get("best_for", "—"))}</td></tr>''' for k, t in plan.get("all_targets", {}).items())}
</table>

<h2>Technology Equivalence Map</h2>
<div class="note">
    <strong>Accuracy labels:</strong>
    <span class="badge badge-green">GREEN — Safe (90%+)</span> automated conversion reliable.
    <span class="badge badge-yellow">YELLOW — Medium (70-85%)</span> needs manual review.
    <span class="badge badge-red">RED — Manual (50-70%)</span> requires significant rewrite.
</div>
<table>
    <tr><th>Current Technology</th><th>Target Equivalent</th><th>Conversion Safety</th></tr>
    {"".join(f'''<tr><td><strong>{_e(eq["current"])}</strong></td><td>{_e(eq["target"])}</td><td><span class="badge badge-{eq["accuracy"].lower()}">{_e(eq["accuracy_label"])}</span></td></tr>''' for eq in plan.get("equivalences", []))}
</table>
{f'<p class="evidence">No technologies detected for mapping.</p>' if not plan.get("equivalences") else ""}

<h2>Package Equivalences (NuGet → {_e(plan.get("package_map", [{}])[0].get("target_ecosystem", "target") if plan.get("package_map") else "target")})</h2>
<table>
    <tr><th>Category</th><th>Current (NuGet)</th><th>Target</th><th>Safety</th></tr>
    {"".join(f'''<tr><td>{_e(p["category"])}</td><td><code>{_e(p["current"])}</code></td><td><code>{_e(p["target"])}</code></td><td><span class="badge badge-{p["accuracy"].lower()}">{_e(p["accuracy"])}</span></td></tr>''' for p in plan.get("package_map", []))}
</table>

<h2>Migration Blockers ({len(plan['blockers'])})</h2>
{"<div class='warn'><strong>Resolve blockers before starting migration.</strong></div>" if plan['blockers'] else ""}
{"<table><tr><th>Severity</th><th>Type</th><th>Description</th><th>Recommendation</th><th>Files</th></tr>" + blocker_rows + "</table>" if blocker_rows else '<p class="badge badge-green">No blockers detected.</p>'}

<h2>Module Inventory &amp; Priority Matrix</h2>
<div class="note">
    <strong>Priority quadrants:</strong>
    <span class="badge badge-green">QUICK WIN</span> High value, low effort — migrate first.
    <span class="badge badge-yellow">MAJOR PROJECT</span> High value, high effort — plan carefully.
    <span class="badge badge-blue">FILL IN</span> Low value, low effort — fit between phases.
    <span class="badge badge-red">AVOID</span> Low value, high effort — don't migrate.
</div>
<table>
    <tr><th>Module</th><th>Files</th><th>Endpoints</th><th>Complexity</th><th>Effort</th><th>Hours</th><th>Priority</th></tr>
    {module_rows}
</table>

<h2>Phased Migration Roadmap</h2>
<div class="note">
    <strong>Pattern:</strong> Strangler Fig — run legacy + modern side-by-side via YARP reverse proxy.<br>
    <strong>Migration order:</strong> Read-only lookups → Admin pages → Revenue-critical transactions.<br>
    <strong>Rollback:</strong> Proxy config change (&lt; 1 minute).
</div>
{phases_html}

{"<h2>ERP Integration Plans</h2>" + erp_html if erp_html else ""}

<h2>Recommended Architecture</h2>
<div class="card">
    <h3 style="margin-top:0">Hybrid Period (Legacy + Modern)</h3>
    <pre style="color:var(--fg2);font-size:12px">
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
    </pre>
    <p class="evidence">System.Web Adapters share session/auth between old and new.</p>
    <p class="evidence">Feature flags toggle between old/new endpoints per environment.</p>
</div>

{"<div class='card'><h3 style=\"margin-top:0\">ERP Integration Architecture</h3><pre style=\"color:var(--fg2);font-size:12px\">" + """
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Modern App  │────▶│  API Gateway     │────▶│  SAP        │
│  (API)       │     │  (Auth + Rate    │     │  (OData/RFC)│
└──────────────┘     │   Limiting)      │     └─────────────┘
                     │                  │
                     │                  │────▶┌─────────────┐
                     │                  │     │  TOTVS      │
                     └──────────────────┘     │  (REST API) │
                                              └─────────────┘
""" + "</pre><p class='evidence'>Anti-pattern: avoid point-to-point integrations. Use API Gateway for centralized auth and monitoring.</p></div>" if plan.get("erp_plans") else ""}

<h2>Effort Estimates</h2>
<div class="card">
    <table style="margin:0">
        <tr><th>Category</th><th>Modules</th><th>Hours</th><th>Weeks (1 dev)</th></tr>
        <tr><td><span class="badge badge-green">Quick Wins</span></td><td>{len(quick_wins)}</td><td>{qw_hours}</td><td>{max(1, qw_hours // 40)}</td></tr>
        <tr><td><span class="badge badge-yellow">Major Projects</span></td><td>{len(major)}</td><td>{mj_hours}</td><td>{max(1, mj_hours // 40)}</td></tr>
        <tr><td><strong>TOTAL</strong></td><td><strong>{summary['total_modules']}</strong></td><td><strong>{summary['total_hours']:,}</strong></td><td><strong>{summary['total_weeks']}</strong></td></tr>
    </table>
    <p class="evidence" style="margin-top:12px">Estimates based on complexity score × calibration factor (8h/story point). [VERIFY] — calibrate with team velocity.</p>
</div>

<h2>Recommendations</h2>
<div class="card">
    <ol>
        <li><strong>Start with Quick Wins</strong> — {len(quick_wins)} modules, {qw_hours}h. Build confidence and momentum.</li>
        <li><strong>Resolve critical blockers first</strong> — {summary['critical_blockers']} blockers must be addressed before migration.</li>
        <li><strong>Extract shared logic</strong> — Move DAL/BLL to .NET Standard 2.0 library shared by legacy and modern.</li>
        <li><strong>Use Strangler Fig pattern</strong> — YARP proxy for route-by-route migration with instant rollback.</li>
        <li><strong>Don't migrate ghost features</strong> — {len(defer)} modules flagged as low-value. Validate usage before migrating.</li>
        {"<li><strong>Plan ERP integration early</strong> — " + ', '.join(summary['erp_integrations']) + " detected. Set up API Gateway and auth before module migration.</li>" if summary['erp_integrations'] else ""}
    </ol>
</div>

<h2>Next Steps</h2>
<div class="note">
    <ol>
        <li>[MANUAL] — Validate module priority with product owner (business value may differ from code analysis)</li>
        <li>[MANUAL] — Calibrate effort estimates with team velocity (hours per story point)</li>
        <li>[MANUAL] — Define target platform and framework (React, Blazor, Angular)</li>
        <li>[MANUAL] — Set up YARP proxy and System.Web Adapters for hybrid period</li>
        {"<li>[MANUAL] — Obtain ERP API credentials and test connectivity (" + ', '.join(summary['erp_integrations']) + ")</li>" if summary['erp_integrations'] else ""}
        <li>[MANUAL] — Define success metrics and rollback criteria per phase</li>
    </ol>
</div>
"""
    return _wrap_html(f"{name} — Migration Plan", body)
