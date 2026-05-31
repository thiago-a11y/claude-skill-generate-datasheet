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


TARGET_PLATFORMS = {
    "react+fastapi": {
        "label": "React + FastAPI (Python)",
        "frontend": "React (TypeScript)",
        "backend": "FastAPI (Python)",
        "orm": "Prisma or SQLAlchemy",
        "pros": [
            "Largest ecosystem (React) + fastest Python framework (FastAPI)",
            "TypeScript catches errors at compile time",
            "Pydantic validation = automatic OpenAPI docs",
            "Huge talent pool for hiring",
        ],
        "cons": [
            "Two languages (TypeScript + Python) to maintain",
            "Python async learning curve for C# devs",
            "State management complexity (Redux/Zustand)",
        ],
        "best_for": "Teams willing to adopt Python, greenfield APIs, microservices",
    },
    "react+express": {
        "label": "React + Express (Node.js)",
        "frontend": "React (TypeScript)",
        "backend": "Express / NestJS (TypeScript)",
        "orm": "Prisma",
        "pros": [
            "Single language (TypeScript) across frontend + backend",
            "Massive npm ecosystem",
            "Easy hiring — JavaScript is the most popular language",
            "NestJS has structure similar to ASP.NET MVC (DI, modules, guards)",
        ],
        "cons": [
            "Node.js single-threaded (CPU-bound tasks need workers)",
            "Express is minimalist — needs many middleware packages",
            "Callback/Promise patterns differ from C# async/await",
        ],
        "best_for": "Full-stack TypeScript teams, rapid prototyping, real-time apps",
    },
    "angular+express": {
        "label": "Angular + Express (Node.js)",
        "frontend": "Angular (TypeScript)",
        "backend": "Express / NestJS (TypeScript)",
        "orm": "Prisma or TypeORM",
        "pros": [
            "Angular structure closest to ASP.NET MVC (DI, modules, services)",
            "Enterprise-grade framework with batteries included",
            "Single language (TypeScript)",
            "Strong typing and decorators familiar to C# devs",
        ],
        "cons": [
            "Steeper learning curve than React",
            "Larger bundle size",
            "Smaller community than React",
        ],
        "best_for": "Enterprise teams, complex forms, devs coming from C# MVC",
    },
    "blazor": {
        "label": "Blazor + .NET 8",
        "frontend": "Blazor (C#)",
        "backend": "ASP.NET Core (C#)",
        "orm": "EF Core",
        "pros": [
            "No language change — C# everywhere",
            "Reuse existing .NET libraries directly",
            "Razor syntax is familiar to MVC devs",
            "Server-side rendering for SEO",
        ],
        "cons": [
            "Smaller ecosystem than React/Angular",
            "WASM bundle size (first load slower)",
            "Limited third-party component libraries vs React",
            "Less talent pool for hiring",
        ],
        "best_for": "C#-only teams, simple migration from MVC, internal apps",
    },
    "vue+fastapi": {
        "label": "Vue 3 + FastAPI (Python)",
        "frontend": "Vue 3 (TypeScript)",
        "backend": "FastAPI (Python)",
        "orm": "SQLAlchemy or Prisma",
        "pros": [
            "Vue is easiest to learn (simplest template syntax)",
            "FastAPI automatic OpenAPI docs",
            "Lightweight — small bundle, fast builds",
            "Composition API similar to React hooks",
        ],
        "cons": [
            "Smaller ecosystem than React",
            "Two languages (TypeScript + Python)",
            "Fewer enterprise-grade component libraries",
        ],
        "best_for": "Small teams, lightweight apps, devs new to frontend",
    },
    "go+react": {
        "label": "React + Go (Gin)",
        "frontend": "React (TypeScript)",
        "backend": "Gin / Echo (Go)",
        "orm": "GORM",
        "pros": [
            "Go compiles to single binary — easy deployment",
            "Excellent concurrency (goroutines)",
            "Very fast — lower cloud costs",
            "Strong typing, similar feel to C#",
        ],
        "cons": [
            "Go ecosystem smaller than Node/Python for web",
            "No generics until recently — boilerplate",
            "Fewer ORM features than EF Core/Prisma",
            "Two very different languages to maintain",
        ],
        "best_for": "Performance-critical APIs, microservices, DevOps teams",
    },
}

TECH_EQUIVALENCES = {
    "ASP.NET MVC Controller": {
        "react+fastapi": ("FastAPI router + Pydantic models", "GREEN"),
        "react+express": ("Express/NestJS controller", "GREEN"),
        "angular+express": ("NestJS controller (decorators)", "GREEN"),
        "blazor": ("ASP.NET Core Minimal API / Controller", "GREEN"),
        "vue+fastapi": ("FastAPI router + Pydantic models", "GREEN"),
        "go+react": ("Gin handler + struct binding", "GREEN"),
    },
    "Entity Framework 6": {
        "react+fastapi": ("Prisma ORM or SQLAlchemy", "YELLOW"),
        "react+express": ("Prisma ORM", "YELLOW"),
        "angular+express": ("Prisma ORM or TypeORM", "YELLOW"),
        "blazor": ("EF Core (Code-First)", "GREEN"),
        "vue+fastapi": ("SQLAlchemy or Prisma", "YELLOW"),
        "go+react": ("GORM", "YELLOW"),
    },
    "EF Core": {
        "react+fastapi": ("Prisma ORM or SQLAlchemy", "YELLOW"),
        "react+express": ("Prisma ORM", "GREEN"),
        "angular+express": ("Prisma ORM or TypeORM", "GREEN"),
        "blazor": ("EF Core (keep as-is)", "GREEN"),
        "vue+fastapi": ("SQLAlchemy or Prisma", "YELLOW"),
        "go+react": ("GORM", "YELLOW"),
    },
    "Razor Views (.cshtml)": {
        "react+fastapi": ("React TSX components", "YELLOW"),
        "react+express": ("React TSX components", "YELLOW"),
        "angular+express": ("Angular components + templates", "YELLOW"),
        "blazor": ("Razor Components (.razor)", "GREEN"),
        "vue+fastapi": ("Vue 3 SFC (.vue)", "YELLOW"),
        "go+react": ("React TSX components", "YELLOW"),
    },
    "Web Forms (.aspx)": {
        "react+fastapi": ("React components (full rewrite)", "RED"),
        "react+express": ("React components (full rewrite)", "RED"),
        "angular+express": ("Angular components (full rewrite)", "RED"),
        "blazor": ("Blazor components (rewrite, same language)", "YELLOW"),
        "vue+fastapi": ("Vue components (full rewrite)", "RED"),
        "go+react": ("React components (full rewrite)", "RED"),
    },
    "WinForms": {
        "react+fastapi": ("React SPA (full rewrite UI)", "RED"),
        "react+express": ("React SPA (full rewrite UI)", "RED"),
        "angular+express": ("Angular SPA (full rewrite UI)", "RED"),
        "blazor": ("Blazor components (rewrite, same language)", "YELLOW"),
        "vue+fastapi": ("Vue SPA (full rewrite UI)", "RED"),
        "go+react": ("React SPA (full rewrite UI)", "RED"),
    },
    "WPF (XAML)": {
        "react+fastapi": ("React SPA or Electron (full rewrite)", "RED"),
        "react+express": ("React SPA or Electron (full rewrite)", "RED"),
        "angular+express": ("Angular SPA (full rewrite)", "RED"),
        "blazor": ("Blazor Hybrid / MAUI", "YELLOW"),
        "vue+fastapi": ("Vue SPA or Tauri (full rewrite)", "RED"),
        "go+react": ("React SPA or Tauri (full rewrite)", "RED"),
    },
    "Stored Procedures": {
        "react+fastapi": ("Python service functions", "RED"),
        "react+express": ("TypeScript service functions", "RED"),
        "angular+express": ("TypeScript service functions", "RED"),
        "blazor": ("C# service layer", "YELLOW"),
        "vue+fastapi": ("Python service functions", "RED"),
        "go+react": ("Go service functions", "RED"),
    },
    "COM Interop / P/Invoke": {
        "react+fastapi": ("gRPC wrapper service or REST adapter", "RED"),
        "react+express": ("gRPC wrapper service or REST adapter", "RED"),
        "angular+express": ("gRPC wrapper service or REST adapter", "RED"),
        "blazor": ("gRPC wrapper or keep in Windows service", "YELLOW"),
        "vue+fastapi": ("gRPC wrapper service or REST adapter", "RED"),
        "go+react": ("gRPC wrapper service or REST adapter", "RED"),
    },
    "System.Web": {
        "react+fastapi": ("FastAPI middleware (no equivalent)", "RED"),
        "react+express": ("Express middleware", "RED"),
        "angular+express": ("Express middleware", "RED"),
        "blazor": ("ASP.NET Core middleware + System.Web Adapters", "YELLOW"),
        "vue+fastapi": ("FastAPI middleware", "RED"),
        "go+react": ("Gin middleware", "RED"),
    },
    "System.Drawing": {
        "react+fastapi": ("Pillow (Python) or Sharp (Node via API)", "YELLOW"),
        "react+express": ("Sharp (Node.js)", "YELLOW"),
        "angular+express": ("Sharp (Node.js)", "YELLOW"),
        "blazor": ("SixLabors.ImageSharp", "GREEN"),
        "vue+fastapi": ("Pillow (Python)", "YELLOW"),
        "go+react": ("disintegration/imaging (Go)", "YELLOW"),
    },
    "NuGet Packages": {
        "react+fastapi": ("pip (Python) + npm (frontend)", "GREEN"),
        "react+express": ("npm", "GREEN"),
        "angular+express": ("npm", "GREEN"),
        "blazor": ("NuGet (keep as-is)", "GREEN"),
        "vue+fastapi": ("pip + npm", "GREEN"),
        "go+react": ("go modules + npm", "GREEN"),
    },
    "web.config / appsettings.json": {
        "react+fastapi": (".env + python-dotenv", "GREEN"),
        "react+express": (".env + dotenv", "GREEN"),
        "angular+express": (".env + dotenv", "GREEN"),
        "blazor": ("appsettings.json (keep as-is)", "GREEN"),
        "vue+fastapi": (".env + python-dotenv", "GREEN"),
        "go+react": (".env + godotenv", "GREEN"),
    },
}

PACKAGE_EQUIVALENCES = {
    "Auth (JWT)": {
        "nuget": "Microsoft.AspNetCore.Authentication.JwtBearer",
        "npm": "jsonwebtoken",
        "pip": "PyJWT",
        "go": "github.com/golang-jwt/jwt",
        "accuracy": "GREEN",
    },
    "Logging": {
        "nuget": "Serilog",
        "npm": "winston",
        "pip": "loguru",
        "go": "github.com/sirupsen/logrus",
        "accuracy": "GREEN",
    },
    "ORM": {
        "nuget": "EntityFramework / EF Core",
        "npm": "prisma",
        "pip": "SQLAlchemy",
        "go": "gorm.io/gorm",
        "accuracy": "GREEN",
    },
    "HTTP Client": {
        "nuget": "HttpClient (System.Net.Http)",
        "npm": "axios",
        "pip": "httpx",
        "go": "net/http (stdlib)",
        "accuracy": "GREEN",
    },
    "Testing": {
        "nuget": "xUnit / NUnit",
        "npm": "jest / vitest",
        "pip": "pytest",
        "go": "testing (stdlib)",
        "accuracy": "GREEN",
    },
    "Caching": {
        "nuget": "Microsoft.Extensions.Caching",
        "npm": "node-cache / ioredis",
        "pip": "redis-py",
        "go": "github.com/go-redis/redis",
        "accuracy": "GREEN",
    },
    "Messaging": {
        "nuget": "Azure.ServiceBus / MassTransit",
        "npm": "kafkajs / amqplib",
        "pip": "aiokafka / pika",
        "go": "github.com/segmentio/kafka-go",
        "accuracy": "YELLOW",
    },
    "Validation": {
        "nuget": "FluentValidation",
        "npm": "joi / zod",
        "pip": "pydantic",
        "go": "github.com/go-playground/validator",
        "accuracy": "GREEN",
    },
    "Background Jobs": {
        "nuget": "Hangfire",
        "npm": "bull / bullmq",
        "pip": "celery",
        "go": "github.com/robfig/cron",
        "accuracy": "YELLOW",
    },
    "DTO Mapping": {
        "nuget": "AutoMapper",
        "npm": "class-transformer",
        "pip": "pydantic (built-in)",
        "go": "github.com/jinzhu/copier",
        "accuracy": "YELLOW",
    },
}

ACCURACY_LABELS = {
    "GREEN": {"label": "Safe (90%+)", "description": "Automated conversion reliable, minimal manual review"},
    "YELLOW": {"label": "Medium (70-85%)", "description": "Automated mapping works, manual review recommended"},
    "RED": {"label": "Manual (50-70%)", "description": "Requires significant manual rewrite and human judgment"},
}


def analyze_migration(data, target_platform="web", target_erps=None):
    if target_erps is None:
        target_erps = []

    target_key = _resolve_target(target_platform)
    target_info = TARGET_PLATFORMS.get(target_key, TARGET_PLATFORMS["react+fastapi"])

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

    equivalences = _build_equivalence_map(data, target_key)
    package_map = _build_package_map(target_key)

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
            "target_key": target_key,
            "target_info": target_info,
            "current_frameworks": [f["name"] for f in data.get("migration", {}).get("frameworks", [])],
            "target_framework": data.get("migration", {}).get("target_framework", "NOT DETECTED"),
            "erp_integrations": all_erps,
        },
        "modules": modules,
        "phases": phases,
        "blockers": blockers,
        "erp_plans": erp_plans,
        "equivalences": equivalences,
        "package_map": package_map,
        "all_targets": TARGET_PLATFORMS,
    }


def _resolve_target(target_input):
    t = target_input.lower().strip()
    aliases = {
        "web": "react+fastapi",
        "react": "react+fastapi",
        "react+fastapi": "react+fastapi",
        "react+python": "react+fastapi",
        "react+node": "react+express",
        "react+express": "react+express",
        "angular": "angular+express",
        "angular+node": "angular+express",
        "angular+express": "angular+express",
        "blazor": "blazor",
        "vue": "vue+fastapi",
        "vue+fastapi": "vue+fastapi",
        "vue+python": "vue+fastapi",
        "go": "go+react",
        "go+react": "go+react",
        "react+go": "go+react",
    }
    return aliases.get(t, "react+fastapi")


def _build_equivalence_map(data, target_key):
    detected_techs = set()

    langs = data.get("languages", {})
    if "csharp" in langs or "c" in langs:
        detected_techs.add("ASP.NET MVC Controller")
        detected_techs.add("NuGet Packages")
        detected_techs.add("web.config / appsettings.json")

    migration = data.get("migration", {})
    ef = migration.get("ef_version", "NOT DETECTED")
    if "EF6" in ef:
        detected_techs.add("Entity Framework 6")
    elif "EF Core" in ef:
        detected_techs.add("EF Core")

    if migration.get("views", {}).get("cshtml", 0) > 0:
        detected_techs.add("Razor Views (.cshtml)")
    if migration.get("views", {}).get("aspx", 0) > 0:
        detected_techs.add("Web Forms (.aspx)")

    for fw in migration.get("frameworks", []):
        if fw["name"] == "WinForms":
            detected_techs.add("WinForms")
        elif fw["name"] == "WPF":
            detected_techs.add("WPF (XAML)")
        elif fw["name"] == "Web Forms":
            detected_techs.add("Web Forms (.aspx)")
        elif "MVC" in fw["name"] or "API" in fw["name"]:
            detected_techs.add("ASP.NET MVC Controller")

    if migration.get("stored_procedures", 0) > 0:
        detected_techs.add("Stored Procedures")
    if migration.get("com_interop"):
        detected_techs.add("COM Interop / P/Invoke")
    if migration.get("pinvoke"):
        detected_techs.add("COM Interop / P/Invoke")
    if migration.get("system_web"):
        detected_techs.add("System.Web")
    if migration.get("system_drawing"):
        detected_techs.add("System.Drawing")

    if data.get("endpoints"):
        detected_techs.add("ASP.NET MVC Controller")

    result = []
    for tech in TECH_EQUIVALENCES:
        if tech in detected_techs and target_key in TECH_EQUIVALENCES[tech]:
            target_tech, accuracy = TECH_EQUIVALENCES[tech][target_key]
            result.append({
                "current": tech,
                "target": target_tech,
                "accuracy": accuracy,
                "accuracy_label": ACCURACY_LABELS[accuracy]["label"],
                "accuracy_desc": ACCURACY_LABELS[accuracy]["description"],
            })

    result.sort(key=lambda x: {"GREEN": 0, "YELLOW": 1, "RED": 2}.get(x["accuracy"], 3))
    return result


def _build_package_map(target_key):
    target_info = TARGET_PLATFORMS.get(target_key, {})
    backend = target_info.get("backend", "")

    if "Python" in backend or "FastAPI" in backend:
        pkg_key = "pip"
    elif "Node" in backend or "Express" in backend or "NestJS" in backend:
        pkg_key = "npm"
    elif "Go" in backend or "Gin" in backend:
        pkg_key = "go"
    elif "C#" in backend or "ASP.NET" in backend:
        pkg_key = "nuget"
    else:
        pkg_key = "npm"

    result = []
    for category, pkgs in PACKAGE_EQUIVALENCES.items():
        result.append({
            "category": category,
            "current": pkgs.get("nuget", "—"),
            "target": pkgs.get(pkg_key, "—"),
            "target_ecosystem": pkg_key,
            "accuracy": pkgs.get("accuracy", "YELLOW"),
        })
    return result


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
