"""Migration planner — analyzes scan data and generates migration plan."""

import os


SEVERITY_WEIGHT = {"CRITICAL": 5, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

ERP_INTEGRATION_PLANS = {
    "SAP": {
        "pattern": "OData (preferred) or RFC/BAPI with anti-corruption layer",
        "auth": "OAuth 2.0 / X.509 certificates for RFC over SNC",
        "apis": [
            "SAP OData Services — modern, JSON, REST",
            "SAP .NET Connector (NCo) — high-performance RFC calls",
            "SAP BAPI — standard business APIs",
        ],
        "risks": [
            "Complex authentication (OAuth/JWT), user ID passing across hops",
            "RFC requires SAP GUI / SAP Logon installed",
            "BAPI interfaces may change between SAP versions",
        ],
        "recommendation": "Start with OData for read operations, RFC/BAPI for transactions",
    },
    "TOTVS": {
        "pattern": "TOTVS API Services (REST) + TOTVS iPaaS",
        "auth": "API Key / OAuth 2.0 via TOTVS Identity",
        "apis": [
            "TOTVS API Services — REST APIs for Protheus/RM/Datasul",
            "TOTVS iPaaS — low-code integration platform with pre-defined connectors",
            "ADVPL REST endpoints — custom Protheus APIs",
        ],
        "risks": [
            "Customizations isolated → high integration cost",
            "API versions may differ between Protheus releases",
            "iPaaS licensing costs for advanced orchestration",
        ],
        "recommendation": "Use TOTVS API Services REST for standard entities, iPaaS for complex workflows",
    },
    "Oracle ERP": {
        "pattern": "REST API + middleware (Azure Logic Apps or MuleSoft)",
        "auth": "OAuth 2.0 with Oracle Identity Cloud",
        "apis": [
            "Oracle ERP Cloud REST APIs — comprehensive CRUD",
            "Oracle Integration Cloud (OIC) — managed iPaaS",
            "SOAP APIs — legacy, still supported",
        ],
        "risks": [
            "REST APIs require custom .NET HttpClient wrappers",
            "Large payloads may need pagination handling",
            "Oracle licensing complexity for API access",
        ],
        "recommendation": "REST API with dedicated integration service layer, avoid direct DB access",
    },
}


def analyze_migration(data, target_platform="web", target_erps=None):
    if target_erps is None:
        target_erps = []

    detected_erps = [i["service"] for i in data.get("integrations", []) if i["service"] in ERP_INTEGRATION_PLANS]
    all_erps = list(set(target_erps + detected_erps))

    modules = _build_module_inventory(data)
    for mod in modules:
        mod["complexity"] = _calc_complexity(mod, data)
        mod["priority"] = _calc_priority(mod)

    modules.sort(key=lambda m: (-m["priority"]["score"], -m["complexity"]["score"]))

    phases = _generate_phases(modules, data)
    erp_plans = {erp: ERP_INTEGRATION_PLANS[erp] for erp in all_erps if erp in ERP_INTEGRATION_PLANS}

    blockers = data.get("migration", {}).get("blockers", [])
    blockers.sort(key=lambda b: -SEVERITY_WEIGHT.get(b.get("severity", "LOW"), 1))

    total_hours = sum(m["complexity"]["estimated_hours"] for m in modules)
    critical_blockers = sum(1 for b in blockers if b.get("severity") == "CRITICAL")
    high_blockers = sum(1 for b in blockers if b.get("severity") == "HIGH")

    return {
        "summary": {
            "total_modules": len(modules),
            "total_hours": total_hours,
            "total_weeks": max(1, total_hours // 40),
            "critical_blockers": critical_blockers,
            "high_blockers": high_blockers,
            "target_platform": target_platform,
            "current_frameworks": [f["name"] for f in data.get("migration", {}).get("frameworks", [])],
            "target_framework": data.get("migration", {}).get("target_framework", "NOT DETECTED"),
            "erp_integrations": all_erps,
        },
        "modules": modules,
        "phases": phases,
        "blockers": blockers,
        "erp_plans": erp_plans,
    }


def _build_module_inventory(data):
    modules = []
    dirs_seen = set()

    for ep in data.get("endpoints", []):
        dir_name = os.path.dirname(ep["file"]) or ep["file"].split("/")[0] if "/" in ep["file"] else "root"
        if dir_name not in dirs_seen:
            dirs_seen.add(dir_name)
            dir_endpoints = [e for e in data["endpoints"] if (os.path.dirname(e["file"]) or "root") == dir_name]
            modules.append({
                "name": dir_name.replace("/", " / ").replace("_", " ").replace("-", " ").title(),
                "path": dir_name,
                "type": "api",
                "files": len(set(e["file"] for e in dir_endpoints)),
                "endpoints": len(dir_endpoints),
            })

    for fw in data.get("migration", {}).get("frameworks", []):
        fw_name = fw["name"]
        if fw_name in ("WinForms", "WPF", "Web Forms") and fw_name.lower().replace(" ", "_") not in dirs_seen:
            modules.append({
                "name": fw_name,
                "path": fw["files"][0] if fw["files"] else "—",
                "type": "ui",
                "files": len(fw["files"]),
                "endpoints": 0,
            })

    if not modules:
        for d in data.get("structure", [])[:15]:
            d_clean = d.lstrip("./")
            if d_clean and d_clean.count("/") == 0 and d_clean not in dirs_seen:
                dirs_seen.add(d_clean)
                modules.append({
                    "name": d_clean.replace("_", " ").replace("-", " ").title(),
                    "path": d_clean,
                    "type": "module",
                    "files": 0,
                    "endpoints": 0,
                })

    return modules


def _calc_complexity(module, data):
    score = 0
    factors = []

    if module.get("endpoints", 0) > 20:
        score += 15
        factors.append(f"{module['endpoints']} endpoints (high)")
    elif module.get("endpoints", 0) > 5:
        score += 8
        factors.append(f"{module['endpoints']} endpoints (medium)")

    if module.get("files", 0) > 30:
        score += 15
        factors.append(f"{module['files']} files (high)")
    elif module.get("files", 0) > 10:
        score += 8
        factors.append(f"{module['files']} files (medium)")

    migration = data.get("migration", {})
    mod_path = module.get("path", "")

    for blocker in migration.get("blockers", []):
        if blocker.get("type") in ("COM_INTEROP", "PINVOKE"):
            score += 25
            factors.append(f"Blocker: {blocker['type']}")
        elif blocker.get("type") in ("SYSTEM_WEB", "WEB_FORMS", "WINFORMS"):
            score += 15
            factors.append(f"Blocker: {blocker['type']}")
        elif blocker.get("type") in ("EF6_EDMX", "STORED_PROCEDURES", "SYSTEM_DRAWING"):
            score += 10
            factors.append(f"Blocker: {blocker['type']}")

    for item in migration.get("com_interop", []):
        if mod_path and mod_path in item.get("file", ""):
            score += 20
            break

    if module.get("type") == "ui":
        score += 20
        factors.append("UI layer (requires rewrite)")

    if score <= 20:
        level = "LOW"
        sp = 2
        hours = 16
    elif score <= 50:
        level = "MEDIUM"
        sp = 5
        hours = 40
    else:
        level = "HIGH"
        sp = 13
        hours = 104

    hours = max(hours, module.get("files", 1) * 4)

    return {
        "score": score,
        "level": level,
        "story_points": sp,
        "estimated_hours": hours,
        "factors": factors,
    }


def _calc_priority(module):
    value = 50
    effort = module["complexity"]["score"]

    if module.get("endpoints", 0) > 10:
        value += 30
    elif module.get("endpoints", 0) > 0:
        value += 15

    if module.get("type") == "api":
        value += 20

    if effort <= 20 and value >= 60:
        quadrant = "QUICK_WIN"
        label = "Quick Win (High Value, Low Effort)"
    elif effort > 20 and value >= 60:
        quadrant = "MAJOR_PROJECT"
        label = "Major Project (High Value, High Effort)"
    elif effort <= 20 and value < 60:
        quadrant = "FILL_IN"
        label = "Fill-in (Low Value, Low Effort)"
    else:
        quadrant = "AVOID"
        label = "Defer (Low Value, High Effort)"

    return {"value": value, "effort": effort, "quadrant": quadrant, "label": label, "score": value - effort}


def _generate_phases(modules, data):
    phases = [
        {
            "number": 0,
            "name": "Assessment & Planning",
            "duration": "1-2 weeks",
            "goal": "Complete scan, identify blockers, define migration order",
            "modules": [],
            "success_criteria": "All modules scored, blockers identified, team aligned",
        },
        {
            "number": 1,
            "name": "Foundation — Extract Shared Logic",
            "duration": "2-4 weeks",
            "goal": "Extract business logic and data access to shared libraries",
            "modules": [],
            "success_criteria": "DAL/BLL in shared library, tested independently",
        },
        {
            "number": 2,
            "name": "Low-Risk Migration",
            "duration": "4-8 weeks",
            "goal": "Migrate read-only lookups and admin pages",
            "modules": [],
            "success_criteria": "5-10 screens modernized, E2E tests passing",
        },
        {
            "number": 3,
            "name": "Medium-Risk Migration",
            "duration": "8-12 weeks",
            "goal": "Migrate internal workflows and non-revenue-critical features",
            "modules": [],
            "success_criteria": "Feature flags deployed, rollback tested",
        },
        {
            "number": 4,
            "name": "High-Risk Core Migration",
            "duration": "12-20 weeks",
            "goal": "Migrate revenue-critical transactions",
            "modules": [],
            "success_criteria": "Zero-downtime cutover, A/B validated",
        },
        {
            "number": 5,
            "name": "Decommission Legacy",
            "duration": "1-2 weeks",
            "goal": "Retire legacy system, remove proxy routing",
            "modules": [],
            "success_criteria": "Legacy server shut down, all traffic on new platform",
        },
    ]

    for mod in modules:
        level = mod["complexity"]["level"]
        quadrant = mod["priority"]["quadrant"]

        if quadrant == "AVOID":
            continue
        elif level == "LOW" or quadrant == "QUICK_WIN":
            phases[2]["modules"].append(mod)
        elif level == "MEDIUM":
            phases[3]["modules"].append(mod)
        else:
            phases[4]["modules"].append(mod)

    return phases
