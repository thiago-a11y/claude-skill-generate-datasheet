"""Markdown renderer — generates Layer 1, 4, 5 documentation from scan data."""


def render_architecture(data):
    name = data["project"]["name"]
    langs = data["languages"]
    endpoints = data["endpoints"]
    tables = data["database"]["tables"]
    integrations = data["integrations"]
    structure = data["structure"]

    lang_table = "| Language | Files | Lines |\n|----------|-------|-------|\n"
    for lang, info in sorted(langs.items(), key=lambda x: -x[1]["files"]):
        lang_table += f"| {lang} | {info['files']} | {info['lines']:,} |\n"

    struct_tree = "\n".join(f"  {d}" for d in structure[:25])

    integ_list = "\n".join(f"- {i['service']} (`{i['file']}:{i['line']}`)" for i in integrations[:15])

    return f"""# Architecture — {name}

## Stack

{lang_table}

## Directory Structure

```
{struct_tree}
```

## API Surface

- **{len(endpoints)}** endpoints detected
- **{len(tables)}** database tables
- **{len(integrations)}** external integrations

## External Integrations

{integ_list if integ_list else "No external integrations detected."}

## Authentication

- **Method:** {data['auth']['method']}
- **MFA/2FA:** {'Detected' if data['auth']['mfa'] else 'Not Detected'}
- **RBAC:** {'Detected' if data['auth']['rbac'] else 'Not Detected'}

## Dependencies

- **Manager:** {data['dependencies']['manager']}
- **Total:** {data['dependencies']['total']}
"""


def render_data_dictionary(data):
    tables = data["database"]["tables"]
    if not tables:
        return "# Data Dictionary\n\nNo database tables detected.\n"

    rows = "| Table | Source |\n|-------|--------|\n"
    for t in tables:
        rows += f"| `{t['name']}` | `{t['file']}:{t['line']}` |\n"

    return f"""# Data Dictionary

## Tables ({len(tables)} detected)

{rows}

> Source: CREATE TABLE / Schema::create / migration files detected by scanner.
> Column-level detail requires manual inspection of each migration.
"""


def render_endpoints(data):
    eps = data["endpoints"]
    if not eps:
        return "# API Endpoints\n\nNo endpoints detected.\n"

    rows = "| Method | Path | Source |\n|--------|------|--------|\n"
    for ep in eps:
        rows += f"| `{ep['method']}` | `{ep['path']}` | `{ep['file']}:{ep['line']}` |\n"

    crit_counts = {}
    for ep in eps:
        c = ep.get("criticality", "operational")
        crit_counts[c] = crit_counts.get(c, 0) + 1

    crit_summary = ", ".join(f"{k}: {v}" for k, v in sorted(crit_counts.items(), key=lambda x: -x[1]))

    return f"""# API Endpoints

## Summary

- **Total:** {len(eps)} endpoints
- **By criticality:** {crit_summary}

## Full Inventory

{rows}
"""


def render_glossary(data):
    terms = []

    if data["auth"]["method"] != "NOT DETECTED":
        terms.append(("JWT", "JSON Web Token — authentication method used by this system"))
    if data["auth"]["rbac"]:
        terms.append(("RBAC", "Role-Based Access Control — permission system based on user roles"))
    if data["auth"]["mfa"]:
        terms.append(("MFA/2FA", "Multi-Factor Authentication — additional security layer beyond password"))

    for integ in data["integrations"][:10]:
        terms.append((integ["service"], f"External service integrated at `{integ['file']}:{integ['line']}`"))

    rows = "| Term | Definition |\n|------|------------|\n"
    for term, defn in terms:
        rows += f"| {term} | {defn} |\n"

    return f"""# Glossary

{rows if terms else "No domain terms automatically detected. Add project-specific terms manually."}
"""


def render_changelog(data):
    commits = data["git"]["last_10"]
    total = data["git"]["commits"]
    contributors = data["git"]["contributors"]
    recent = data["git"]["recent_commits"]

    commit_list = "\n".join(f"- {c}" for c in commits) if commits else "No git history detected."

    return f"""# Changelog

## Summary

- **Total commits:** {total}
- **Contributors:** {', '.join(contributors[:10]) or 'N/A'}
- **Last 30 days:** {recent} commits

## Recent Changes

{commit_list}

> Full history: `git log --oneline`
"""


def render_security(data):
    controls = data["security"]

    rows = "| Control | Status | Evidence |\n|---------|--------|----------|\n"
    for control, info in controls.items():
        label = control.replace("_", " ").title()
        status = "✅ Detected" if info["detected"] else "❌ Not Detected"
        evidence = ", ".join(info["files"][:3]) if info["files"] else "—"
        rows += f"| {label} | {status} | `{evidence}` |\n"

    detected = sum(1 for v in controls.values() if v["detected"])
    total = len(controls)

    return f"""# Security Controls

## Summary

- **Controls detected:** {detected}/{total}
- **Auth method:** {data['auth']['method']}
- **MFA:** {'Detected' if data['auth']['mfa'] else 'Not Detected'}
- **RBAC:** {'Detected' if data['auth']['rbac'] else 'Not Detected'}

## Controls Matrix

{rows}

## External Services & Data Residency

| Service | Classification | Data Residency | Source |
|---------|---------------|----------------|--------|
"""  + "\n".join(
        f"| {i['service']} | {i.get('classification', 'unknown')} | {i.get('data_residency', 'Unknown')} | `{i['file']}:{i['line']}` |"
        for i in data["integrations"]
    ) + "\n"


def render_bugs_known(data):
    todos = data["health"]["todo_items"]

    if not todos:
        return "# Known Bugs & Issues\n\nNo TODOs/FIXMEs/HACKs found in codebase.\n"

    rows = "| Location | Content |\n|----------|--------|\n"
    for item in todos:
        rows += f"| `{item['file']}:{item['line']}` | {item['content']} |\n"

    return f"""# Known Bugs & Issues

## TODOs/FIXMEs ({data['health']['todos']} found)

{rows}

> Source: grep for TODO, FIXME, HACK, XXX, WORKAROUND in source files.
"""


def render_contributing(data):
    name = data["project"]["name"]
    dep_mgr = data["dependencies"]["manager"]

    setup = "```bash\n"
    if dep_mgr == "npm":
        setup += "npm install\nnpm run dev\n"
    elif dep_mgr == "composer":
        setup += "composer install\nphp artisan serve\n"
    elif dep_mgr == "pip":
        setup += "pip install -r requirements.txt\npython manage.py runserver\n"
    else:
        setup += "# Check project README for setup instructions\n"
    setup += "```"

    return f"""# Contributing to {name}

## Setup

{setup}

## Dependencies

- **Package manager:** {dep_mgr}
- **Total packages:** {data['dependencies']['total']}

## Code Structure

- **Source files:** {data['tests']['source_files']}
- **Test files:** {data['tests']['test_files']}
- **Test coverage:** {int(data['tests']['test_files'] / max(1, data['tests']['source_files']) * 100)}%

## Before Submitting

1. Run existing tests
2. Add tests for new functionality
3. Check for TODOs: {data['health']['todos']} existing
4. Follow existing code patterns and conventions
"""


def render_health_score(data):
    from codedocs.renderer import _risk_score
    score, details = _risk_score(data, "en-US")

    rows = "| Dimension | Score | Evidence |\n|-----------|-------|----------|\n"
    for label, val, evidence in details:
        rows += f"| {label} | {val}/100 | {evidence} |\n"

    return f"""# Health Score

## Overall: {score}/100

{rows}

## Key Metrics

- **Source files:** {data['tests']['source_files']}
- **Test files:** {data['tests']['test_files']}
- **Coverage:** {int(data['tests']['test_files'] / max(1, data['tests']['source_files']) * 100)}%
- **Contributors:** {len(data['git']['contributors'])}
- **Commits (30d):** {data['git']['recent_commits']}
- **TODOs/FIXMEs:** {data['health']['todos']}
- **Dependencies:** {data['dependencies']['total']} ({data['dependencies']['manager']})
"""


def render_bus_factor(data):
    modules = data["git"].get("bus_factor_modules", {})
    if not modules:
        return "# Bus Factor Report\n\nNo git history available for bus factor analysis.\n"

    critical = []
    high = []
    medium = []

    for mod, info in sorted(modules.items(), key=lambda x: x[1]["count"]):
        row = f"| {mod} | {', '.join(info['contributors'][:3]) or '—'} | {info['count']} | {info['files']} | {info['endpoints']} |"
        if info["count"] <= 1:
            critical.append(row)
        elif info["count"] <= 2:
            high.append(row)
        else:
            medium.append(row)

    header = "| Module | Contributors | Count | Files | Endpoints |\n|--------|-------------|-------|-------|-----------|\n"

    sections = ""
    if critical:
        sections += f"\n### Critical Risk (single contributor)\n\n{header}" + "\n".join(critical) + "\n"
    if high:
        sections += f"\n### High Risk (2 contributors)\n\n{header}" + "\n".join(high) + "\n"
    if medium:
        sections += f"\n### Moderate Risk (3+ contributors)\n\n{header}" + "\n".join(medium) + "\n"

    return f"""# Bus Factor Report

## Summary

- **Modules analyzed:** {len(modules)}
- **Critical risk (1 contributor):** {len(critical)}
- **High risk (2 contributors):** {len(high)}
- **Moderate risk (3+):** {len(medium)}
{sections}
## Action Items

"""  + "\n".join(
        f"{i+1}. **{mod}** has only {info['count']} contributor(s) with {info['endpoints']} endpoints. Pair another developer on this module."
        for i, (mod, info) in enumerate(sorted(modules.items(), key=lambda x: x[1]["count"])[:5])
        if info["count"] <= 2
    ) + "\n"


def render_evolution_report(data):
    deps = data["dependencies"]["items"][:30]
    deprecated = data.get("deprecated_functions", [])
    ghost = data.get("ghost_features", [])

    dep_rows = "| Package | Version |\n|---------|--------|\n"
    for d in deps:
        dep_rows += f"| {d['name']} | {d['version']} |\n"

    deprecated_rows = ""
    if deprecated:
        deprecated_rows = "| Function | Replacement | Severity | File |\n|----------|------------|----------|------|\n"
        seen = set()
        for d in deprecated:
            key = f"{d['function']}:{d['file']}"
            if key not in seen:
                seen.add(key)
                deprecated_rows += f"| `{d['function']}` | `{d['replacement']}` | {d['severity']} | `{d['file']}:{d['line']}` |\n"

    ghost_rows = ""
    if ghost:
        ghost_rows = "| File | Last Commit | Days Ago |\n|------|------------|----------|\n"
        for g in ghost:
            ghost_rows += f"| `{g['file']}` | {g['last_commit']} | {g['days_ago']} |\n"

    return f"""# Evolution Report

## Dependencies ({data['dependencies']['total']} — {data['dependencies']['manager']})

{dep_rows if deps else "No dependencies detected."}

## Deprecated Functions ({len(deprecated)} found)

{deprecated_rows if deprecated_rows else "No deprecated functions detected."}

## Ghost Features (no commits in 90+ days)

{ghost_rows if ghost_rows else "No ghost features detected — all endpoint files have recent activity."}

## Tech Debt

- **TODOs/FIXMEs:** {data['health']['todos']}
- **LOC:** {data['health']['loc']:,}
- **Density:** {data['health']['todos'] / max(1, data['health']['loc'] / 1000):.1f} per KLOC
"""


def render_all_md(data):
    return {
        "architecture.md": render_architecture(data),
        "data-dictionary.md": render_data_dictionary(data),
        "endpoints.md": render_endpoints(data),
        "glossary.md": render_glossary(data),
        "CHANGELOG.md": render_changelog(data),
        "security.md": render_security(data),
        "bugs-known.md": render_bugs_known(data),
        "contributing.md": render_contributing(data),
        "health-score.md": render_health_score(data),
        "bus-factor-report.md": render_bus_factor(data),
        "evolution-report.md": render_evolution_report(data),
    }
