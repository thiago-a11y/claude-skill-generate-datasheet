"""Codebase scanner — runs grep/find/git locally, returns structured data."""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


def _run(cmd, cwd, timeout=30):
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _count_lines(output):
    if not output:
        return 0
    try:
        return int(output.strip().split()[0])
    except (ValueError, IndexError):
        return 0


def _lines(output):
    if not output:
        return []
    return [l.strip() for l in output.strip().split("\n") if l.strip()]


LANG_EXTENSIONS = {
    "php": [".php"],
    "typescript": [".ts", ".tsx"],
    "javascript": [".js", ".jsx"],
    "python": [".py"],
    "go": [".go"],
    "rust": [".rs"],
    "java": [".java"],
    "csharp": [".cs"],
    "ruby": [".rb"],
    "dart": [".dart"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".hpp", ".cc"],
}

EXCLUDE_DIRS = {
    "node_modules", "vendor", ".git", "dist", "build", "__pycache__",
    ".next", ".nuxt", "target", "bin", "obj", "venv", ".venv",
}


def scan(project_path, progress_callback=None):
    p = Path(project_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")

    data = {
        "project": {"name": p.name, "path": str(p), "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M")},
        "languages": {},
        "structure": [],
        "endpoints": [],
        "database": {"tables": [], "migrations": []},
        "auth": {"method": "NOT DETECTED", "evidence": [], "mfa": False, "rbac": False},
        "security": {},
        "integrations": [],
        "tests": {"test_files": 0, "source_files": 0},
        "git": {"commits": 0, "contributors": [], "recent_commits": 0, "last_10": []},
        "health": {"todos": 0, "todo_items": [], "loc": 0},
        "dependencies": {"manager": "NOT DETECTED", "total": 0, "items": []},
        "existing_docs": [],
        "migration": {
            "blockers": [],
            "frameworks": [],
            "target_framework": "NOT DETECTED",
            "views": {"razor": 0, "aspx": 0, "cshtml": 0},
            "ef_version": "NOT DETECTED",
            "has_edmx": False,
            "stored_procedures": 0,
            "com_interop": [],
            "pinvoke": [],
            "system_web": [],
            "system_drawing": [],
            "configs": [],
        },
    }

    steps = [
        ("Detecting languages", _scan_languages),
        ("Scanning structure", _scan_structure),
        ("Scanning endpoints", _scan_endpoints),
        ("Scanning database", _scan_database),
        ("Scanning authentication", _scan_auth),
        ("Scanning security controls", _scan_security),
        ("Scanning integrations", _scan_integrations),
        ("Scanning tests", _scan_tests),
        ("Scanning git history", _scan_git),
        ("Scanning code health", _scan_health),
        ("Scanning dependencies", _scan_dependencies),
        ("Scanning existing docs", _scan_docs),
        ("Scanning migration blockers", _scan_migration),
    ]

    for i, (label, fn) in enumerate(steps):
        if progress_callback:
            progress_callback(i + 1, len(steps), label)
        fn(data, str(p))

    return data


def _scan_languages(data, cwd):
    for lang, exts in LANG_EXTENSIONS.items():
        for ext in exts:
            find_cmd = f"find . -name '*{ext}' -not -path '*/{'/'.join(f'-not -path \"*/{d}/*\"' for d in EXCLUDE_DIRS).replace('-not -path ', '')}'"
            simple_cmd = f"find . -name '*{ext}' | grep -v node_modules | grep -v vendor | grep -v '.git/' | grep -v __pycache__"
            out = _run(simple_cmd, cwd)
            files = _lines(out)
            if files:
                loc = 0
                for f in files[:100]:
                    wc = _run(f"wc -l < '{f}'", cwd)
                    try:
                        loc += int(wc.strip())
                    except (ValueError, TypeError):
                        pass
                if lang in data["languages"]:
                    data["languages"][lang]["files"] += len(files)
                    data["languages"][lang]["lines"] += loc
                else:
                    data["languages"][lang] = {"files": len(files), "lines": loc, "extensions": exts}


def _scan_structure(data, cwd):
    out = _run("find . -maxdepth 2 -type d -not -path '*/.git*' -not -path '*/node_modules*' -not -path '*/vendor*' | sort | head -50", cwd)
    data["structure"] = _lines(out)


def _scan_endpoints(data, cwd):
    patterns = [
        (r"router\.", "router"),
        (r"app\.(get|post|put|delete|patch)\(", "express"),
        (r"Route::", "laravel"),
        (r"@app\.(get|post|put|delete|patch)", "flask/fastapi"),
        (r"@(Get|Post|Put|Delete|Patch)\(", "nestjs/spring"),
        (r"r\.HandleFunc\(", "go-mux"),
        (r"http\.HandleFunc\(", "go-stdlib"),
    ]

    include = "--include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.rs' --include='*.java' --include='*.rb'"
    out = _run(
        f"grep -rn 'router\\.\\.\\|app\\.get\\|app\\.post\\|app\\.put\\|app\\.delete\\|app\\.patch\\|Route::\\|@app\\.\\|@Get\\|@Post\\|@Put\\|@Delete\\|HandleFunc' {include} 2>/dev/null | grep -v node_modules | grep -v vendor | head -100",
        cwd,
    )
    for line in _lines(out):
        parts = line.split(":", 2)
        if len(parts) >= 3:
            filepath = parts[0].lstrip("./")
            try:
                lineno = int(parts[1])
            except ValueError:
                lineno = 0
            content = parts[2].strip()

            method = "GET"
            for m in ["post", "put", "delete", "patch", "POST", "PUT", "DELETE", "PATCH"]:
                if m.lower() in content.lower():
                    method = m.upper()
                    break

            path_match = re.search(r"""['"](/[^'"]*?)['"]""", content)
            path = path_match.group(1) if path_match else "[VERIFY]"

            data["endpoints"].append({
                "method": method,
                "path": path,
                "file": filepath,
                "line": lineno,
                "raw": content[:120],
            })


def _scan_database(data, cwd):
    migrations = _run(
        "find . -name '*migrat*' -o -name '*schema*' -o -name '*.prisma' -o -name '*.sql' | grep -v node_modules | grep -v vendor | head -30",
        cwd,
    )
    data["database"]["migrations"] = _lines(migrations)

    include = "--include='*.sql' --include='*.php' --include='*.py' --include='*.ts' --include='*.prisma'"
    tables_out = _run(
        f"grep -rn 'CREATE TABLE\\|Schema::create\\|createTable\\|class.*Migration' {include} 2>/dev/null | grep -v node_modules | grep -v vendor | head -50",
        cwd,
    )
    for line in _lines(tables_out):
        parts = line.split(":", 2)
        if len(parts) >= 3:
            filepath = parts[0].lstrip("./")
            content = parts[2].strip()
            table_match = re.search(r"""(?:CREATE TABLE|Schema::create|createTable)\s*\(?[`'"]*(\w+)""", content, re.IGNORECASE)
            table_name = table_match.group(1) if table_match else "[VERIFY]"
            data["database"]["tables"].append({
                "name": table_name,
                "file": filepath,
                "line": parts[1],
            })


def _scan_auth(data, cwd):
    include = "--include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.java'"

    jwt = _run(f"grep -rln 'jwt\\|JWT\\|jsonwebtoken\\|jose' {include} 2>/dev/null | grep -v node_modules | head -10", cwd)
    oauth = _run(f"grep -rln 'oauth\\|OAuth\\|passport' {include} 2>/dev/null | grep -v node_modules | head -10", cwd)
    session = _run(f"grep -rln 'session\\|cookie.*auth\\|express-session' {include} 2>/dev/null | grep -v node_modules | head -10", cwd)
    apikey = _run(f"grep -rln 'api.key\\|apiKey\\|x-api-key\\|API_KEY' {include} 2>/dev/null | grep -v node_modules | head -10", cwd)
    mfa = _run(f"grep -rln 'totp\\|2fa\\|mfa\\|two.factor\\|authenticator' {include} 2>/dev/null | grep -v node_modules | head -5", cwd)
    rbac = _run(f"grep -rln 'role\\|permission\\|isAdmin\\|authorize\\|hasRole\\|guard' {include} 2>/dev/null | grep -v node_modules | head -10", cwd)

    if _lines(jwt):
        data["auth"]["method"] = "JWT"
        data["auth"]["evidence"] = _lines(jwt)
    elif _lines(oauth):
        data["auth"]["method"] = "OAuth"
        data["auth"]["evidence"] = _lines(oauth)
    elif _lines(session):
        data["auth"]["method"] = "Session"
        data["auth"]["evidence"] = _lines(session)
    elif _lines(apikey):
        data["auth"]["method"] = "API Key"
        data["auth"]["evidence"] = _lines(apikey)

    data["auth"]["mfa"] = len(_lines(mfa)) > 0
    data["auth"]["rbac"] = len(_lines(rbac)) > 0


def _scan_security(data, cwd):
    include = "--include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.conf'"
    checks = {
        "cors": "cors\\|Access-Control-Allow",
        "helmet": "helmet\\|security.headers",
        "csrf": "csrf\\|CSRF\\|xsrf",
        "rate_limiting": "rate.limit\\|throttle\\|RateLimit",
        "input_validation": "sanitize\\|escape\\|htmlspecialchars\\|validator\\|joi\\|zod\\|yup",
        "encryption": "encrypt\\|decrypt\\|AES\\|RSA\\|crypto\\.create\\|bcrypt\\|argon",
        "https_enforced": "HSTS\\|Strict-Transport\\|forceSSL\\|redirect.*https",
        "audit_logging": "audit.*log\\|activity.*log\\|log.*action",
        "security_headers": "X-Frame-Options\\|X-Content-Type\\|Content-Security-Policy\\|Referrer-Policy",
    }
    for control, pattern in checks.items():
        out = _run(f"grep -rln '{pattern}' {include} 2>/dev/null | grep -v node_modules | grep -v vendor | head -5", cwd)
        files = _lines(out)
        data["security"][control] = {"detected": len(files) > 0, "files": files}


def _scan_integrations(data, cwd):
    include = "--include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.env*'"
    out = _run(
        f"grep -rn 'https://.*api\\|amazonaws\\|googleapis\\|graph\\.facebook\\|api\\.openai\\|api\\.anthropic\\|stripe\\|twilio\\|sendgrid\\|mailgun\\|api\\.slack\\|mqtt\\|rabbitmq\\|redis\\|sap\\|oracle' {include} 2>/dev/null | grep -v node_modules | grep -v vendor | head -40",
        cwd,
    )
    seen = set()
    for line in _lines(out):
        parts = line.split(":", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
            url_match = re.search(r'(https?://[^\s\'"<>]+)', content)
            if url_match:
                domain = url_match.group(1).split("/")[2] if len(url_match.group(1).split("/")) > 2 else url_match.group(1)
                if domain not in seen:
                    seen.add(domain)
                    data["integrations"].append({
                        "service": domain,
                        "file": parts[0].lstrip("./"),
                        "line": parts[1],
                    })

    keywords = {
        "stripe": "Stripe", "twilio": "Twilio", "sendgrid": "SendGrid",
        "mailgun": "Mailgun", "sentry": "Sentry", "datadog": "Datadog",
        "firebase": "Firebase", "supabase": "Supabase", "aws": "AWS",
        "sap": "SAP", "oracle": "Oracle", "mqtt": "MQTT", "redis": "Redis",
        "rabbitmq": "RabbitMQ", "kafka": "Kafka",
    }
    for kw, name in keywords.items():
        if not any(name.lower() in i["service"].lower() for i in data["integrations"]):
            check = _run(f"grep -rln '{kw}' --include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.yml' --include='*.yaml' --include='*.json' 2>/dev/null | grep -v node_modules | grep -v vendor | head -3", cwd)
            files = _lines(check)
            if files:
                data["integrations"].append({"service": name, "file": files[0].lstrip("./"), "line": "—"})


def _scan_tests(data, cwd):
    tests = _run("find . -name '*.test.*' -o -name '*.spec.*' -o -name 'test_*' -o -name '*_test.*' -o -name '*Test.php' -o -name '*_test.go' | grep -v node_modules | grep -v vendor | wc -l", cwd)
    source = _run("find . -name '*.ts' -o -name '*.js' -o -name '*.py' -o -name '*.php' -o -name '*.go' -o -name '*.rs' -o -name '*.java' | grep -v node_modules | grep -v vendor | grep -v '.test.' | grep -v '.spec.' | grep -v 'test_' | wc -l", cwd)
    data["tests"]["test_files"] = _count_lines(tests)
    data["tests"]["source_files"] = _count_lines(source)


def _scan_git(data, cwd):
    if not os.path.exists(os.path.join(cwd, ".git")):
        return

    commits = _run("git log --oneline 2>/dev/null | wc -l", cwd)
    data["git"]["commits"] = _count_lines(commits)

    contributors = _run("git log --format='%an' 2>/dev/null | sort -u", cwd)
    data["git"]["contributors"] = _lines(contributors)

    recent = _run("git log --since='30 days ago' --oneline 2>/dev/null | wc -l", cwd)
    data["git"]["recent_commits"] = _count_lines(recent)

    last = _run("git log --oneline -10 2>/dev/null", cwd)
    data["git"]["last_10"] = _lines(last)


def _scan_health(data, cwd):
    include = "--include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.rs' --include='*.java'"
    todo_count = _run(f"grep -rn 'TODO\\|FIXME\\|HACK\\|XXX\\|WORKAROUND' {include} 2>/dev/null | grep -v node_modules | grep -v vendor | wc -l", cwd)
    data["health"]["todos"] = _count_lines(todo_count)

    todo_items = _run(f"grep -rn 'TODO\\|FIXME\\|HACK' {include} 2>/dev/null | grep -v node_modules | grep -v vendor | head -20", cwd)
    for line in _lines(todo_items):
        parts = line.split(":", 2)
        if len(parts) >= 3:
            data["health"]["todo_items"].append({
                "file": parts[0].lstrip("./"),
                "line": parts[1],
                "content": parts[2].strip()[:100],
            })

    loc = _run(f"find . -name '*.ts' -o -name '*.js' -o -name '*.py' -o -name '*.php' -o -name '*.go' -o -name '*.rs' -o -name '*.java' | grep -v node_modules | grep -v vendor | xargs wc -l 2>/dev/null | tail -1", cwd)
    data["health"]["loc"] = _count_lines(loc)


def _scan_dependencies(data, cwd):
    pkg = os.path.join(cwd, "package.json")
    composer = os.path.join(cwd, "composer.json")
    req = os.path.join(cwd, "requirements.txt")
    gomod = os.path.join(cwd, "go.mod")
    cargo = os.path.join(cwd, "Cargo.toml")

    if os.path.exists(pkg):
        data["dependencies"]["manager"] = "npm"
        out = _run("cat package.json", cwd)
        deps = re.findall(r'"([^"]+)":\s*"([^"]+)"', out)
        in_deps = False
        for name, version in deps:
            if name in ("dependencies", "devDependencies"):
                in_deps = True
                continue
            if in_deps and not name.startswith("@"):
                data["dependencies"]["items"].append({"name": name, "version": version})
        data["dependencies"]["total"] = len(data["dependencies"]["items"])

    elif os.path.exists(composer):
        data["dependencies"]["manager"] = "composer"
        out = _run("cat composer.json", cwd)
        deps = re.findall(r'"([^"]+/[^"]+)":\s*"([^"]+)"', out)
        for name, version in deps:
            data["dependencies"]["items"].append({"name": name, "version": version})
        data["dependencies"]["total"] = len(data["dependencies"]["items"])

    elif os.path.exists(req):
        data["dependencies"]["manager"] = "pip"
        out = _run("cat requirements.txt", cwd)
        for line in _lines(out):
            if "==" in line:
                parts = line.split("==")
                data["dependencies"]["items"].append({"name": parts[0].strip(), "version": parts[1].strip()})
            elif line and not line.startswith("#"):
                data["dependencies"]["items"].append({"name": line.strip(), "version": "latest"})
        data["dependencies"]["total"] = len(data["dependencies"]["items"])

    elif os.path.exists(gomod):
        data["dependencies"]["manager"] = "go mod"
    elif os.path.exists(cargo):
        data["dependencies"]["manager"] = "cargo"


def _scan_docs(data, cwd):
    out = _run("find . -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' | sort | head -30", cwd)
    data["existing_docs"] = _lines(out)


def _scan_migration(data, cwd):
    inc_cs = "--include='*.cs' --include='*.csproj' --include='*.sln' --include='*.config'"
    inc_all = "--include='*.cs' --include='*.ts' --include='*.js' --include='*.py' --include='*.php' --include='*.go' --include='*.java'"

    # .NET target framework
    tf = _run(f"grep -rn 'TargetFramework\\|TargetFrameworkVersion' --include='*.csproj' 2>/dev/null | head -5", cwd)
    for line in _lines(tf):
        match = re.search(r'>(net\S+|v\d+\.\d+)<', line)
        if match:
            data["migration"]["target_framework"] = match.group(1)
            break

    # MVC controllers
    controllers = _run(f"grep -rln 'Controller\\|\\[HttpGet\\]\\|\\[HttpPost\\]\\|\\[Route\\]\\|\\[ApiController\\]' --include='*.cs' 2>/dev/null | grep -v bin | grep -v obj | head -30", cwd)
    if _lines(controllers):
        data["migration"]["frameworks"].append({"name": "ASP.NET MVC/API", "files": _lines(controllers)})

    # Web Forms
    aspx = _run("find . -name '*.aspx' -o -name '*.ascx' -o -name '*.master' | grep -v bin | grep -v obj | wc -l", cwd)
    aspx_count = _count_lines(aspx)
    if aspx_count > 0:
        data["migration"]["views"]["aspx"] = aspx_count
        data["migration"]["frameworks"].append({"name": "Web Forms", "files": _lines(_run("find . -name '*.aspx' | head -20", cwd))})
        data["migration"]["blockers"].append({
            "type": "WEB_FORMS", "severity": "HIGH",
            "description": f"{aspx_count} Web Forms pages — no direct .NET Core equivalent",
            "recommendation": "Strangler Fig pattern: YARP proxy + migrate page by page",
            "files_affected": aspx_count,
        })

    # Razor views
    cshtml = _run("find . -name '*.cshtml' | grep -v bin | grep -v obj | wc -l", cwd)
    data["migration"]["views"]["cshtml"] = _count_lines(cshtml)
    razor = _run("find . -name '*.razor' | grep -v bin | grep -v obj | wc -l", cwd)
    data["migration"]["views"]["razor"] = _count_lines(razor)

    # WinForms
    winforms = _run(f"grep -rln 'System\\.Windows\\.Forms\\|InitializeComponent\\|partial class.*Form' --include='*.cs' 2>/dev/null | grep -v bin | grep -v obj | head -20", cwd)
    if _lines(winforms):
        data["migration"]["frameworks"].append({"name": "WinForms", "files": _lines(winforms)})
        data["migration"]["blockers"].append({
            "type": "WINFORMS", "severity": "HIGH",
            "description": f"{len(_lines(winforms))} WinForms files — UI tightly coupled to business logic",
            "recommendation": "Extract business logic to shared library, rewrite UI in web framework",
            "files_affected": len(_lines(winforms)),
        })

    # WPF
    wpf = _run("find . -name '*.xaml' | grep -v bin | grep -v obj | wc -l", cwd)
    if _count_lines(wpf) > 0:
        data["migration"]["frameworks"].append({"name": "WPF", "files": _lines(_run("find . -name '*.xaml' | head -20", cwd))})

    # Entity Framework
    ef6 = _run(f"grep -rln 'DbContext\\|DbSet\\|ObjectContext\\|EntityFramework' --include='*.cs' --include='*.config' --include='*.csproj' 2>/dev/null | grep -v bin | grep -v obj | head -15", cwd)
    if _lines(ef6):
        edmx = _run("find . -name '*.edmx' | grep -v bin | wc -l", cwd)
        data["migration"]["has_edmx"] = _count_lines(edmx) > 0
        if _count_lines(edmx) > 0:
            data["migration"]["ef_version"] = "EF6 (EDMX)"
            data["migration"]["blockers"].append({
                "type": "EF6_EDMX", "severity": "MEDIUM",
                "description": f"{_count_lines(edmx)} EDMX files — conceptual break migrating to EF Core",
                "recommendation": "Migrate to EF Core Code-First with DbContext",
                "files_affected": _count_lines(edmx),
            })
        else:
            efcore = _run(f"grep -rln 'Microsoft\\.EntityFrameworkCore' --include='*.cs' --include='*.csproj' 2>/dev/null | head -5", cwd)
            data["migration"]["ef_version"] = "EF Core" if _lines(efcore) else "EF6 (Code-First)"

    # Stored procedures
    sp = _run(f"grep -rn 'StoredProcedure\\|EXEC\\s\\|EXECUTE\\s\\|sp_\\|usp_\\|CommandType\\.StoredProcedure' --include='*.cs' --include='*.sql' --include='*.php' --include='*.py' 2>/dev/null | grep -v bin | grep -v obj | wc -l", cwd)
    data["migration"]["stored_procedures"] = _count_lines(sp)
    if _count_lines(sp) > 5:
        data["migration"]["blockers"].append({
            "type": "STORED_PROCEDURES", "severity": "MEDIUM",
            "description": f"{_count_lines(sp)} stored procedure references — business logic trapped in DB",
            "recommendation": "Extract SP logic to service layer before migration",
            "files_affected": _count_lines(sp),
        })

    # COM Interop
    com = _run(f"grep -rn 'DllImport\\|ComImport\\|TypeLib\\|Interop\\|Marshal\\.' --include='*.cs' 2>/dev/null | grep -v bin | grep -v obj | head -20", cwd)
    for line in _lines(com):
        parts = line.split(":", 2)
        if len(parts) >= 3:
            data["migration"]["com_interop"].append({"file": parts[0].lstrip("./"), "line": parts[1], "content": parts[2].strip()[:100]})
    if data["migration"]["com_interop"]:
        data["migration"]["blockers"].append({
            "type": "COM_INTEROP", "severity": "CRITICAL",
            "description": f"{len(data['migration']['com_interop'])} COM/Interop references — Windows-only, blocks containerization",
            "recommendation": "Create wrapper service or replace with managed alternatives",
            "files_affected": len(data["migration"]["com_interop"]),
        })

    # P/Invoke
    pinvoke = _run(f"grep -rn 'DllImport.*kernel32\\|DllImport.*user32\\|DllImport.*gdi32\\|DllImport.*advapi32\\|DllImport.*shell32' --include='*.cs' 2>/dev/null | grep -v bin | grep -v obj | head -20", cwd)
    for line in _lines(pinvoke):
        parts = line.split(":", 2)
        if len(parts) >= 3:
            data["migration"]["pinvoke"].append({"file": parts[0].lstrip("./"), "line": parts[1], "content": parts[2].strip()[:100]})
    if data["migration"]["pinvoke"]:
        data["migration"]["blockers"].append({
            "type": "PINVOKE", "severity": "CRITICAL",
            "description": f"{len(data['migration']['pinvoke'])} P/Invoke calls — blocks Linux/container deployment",
            "recommendation": "Replace with cross-platform .NET APIs or isolate in Windows-only service",
            "files_affected": len(data["migration"]["pinvoke"]),
        })

    # System.Web
    sysweb = _run(f"grep -rln 'System\\.Web\\|HttpContext\\.Current\\|HttpApplication' --include='*.cs' 2>/dev/null | grep -v bin | grep -v obj | head -30", cwd)
    data["migration"]["system_web"] = _lines(sysweb)
    if data["migration"]["system_web"]:
        data["migration"]["blockers"].append({
            "type": "SYSTEM_WEB", "severity": "HIGH",
            "description": f"{len(data['migration']['system_web'])} files use System.Web — not available in .NET Core",
            "recommendation": "Use System.Web Adapters for incremental migration",
            "files_affected": len(data["migration"]["system_web"]),
        })

    # System.Drawing
    sysdraw = _run(f"grep -rln 'System\\.Drawing\\|System\\.Drawing\\.Common' --include='*.cs' --include='*.csproj' 2>/dev/null | grep -v bin | grep -v obj | head -10", cwd)
    data["migration"]["system_drawing"] = _lines(sysdraw)
    if data["migration"]["system_drawing"]:
        data["migration"]["blockers"].append({
            "type": "SYSTEM_DRAWING", "severity": "MEDIUM",
            "description": f"{len(data['migration']['system_drawing'])} files use System.Drawing — Windows-only in .NET 6+",
            "recommendation": "Replace with SixLabors.ImageSharp (cross-platform)",
            "files_affected": len(data["migration"]["system_drawing"]),
        })

    # Config files
    configs = []
    for cfg in ["web.config", "app.config", "appsettings.json", "Startup.cs", "Program.cs", "Global.asax"]:
        found = _run(f"find . -name '{cfg}' -not -path '*/bin/*' -not -path '*/obj/*' | head -5", cwd)
        if _lines(found):
            configs.extend(_lines(found))
    data["migration"]["configs"] = configs

    # NuGet packages from .csproj
    if data["dependencies"]["manager"] == "NOT DETECTED":
        csproj = _run("find . -name '*.csproj' -not -path '*/bin/*' -not -path '*/obj/*' | head -5", cwd)
        for proj_file in _lines(csproj):
            content = _run(f"cat '{proj_file}'", cwd)
            pkgs = re.findall(r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"', content)
            for name, version in pkgs:
                data["dependencies"]["items"].append({"name": name, "version": version})
        if data["dependencies"]["items"]:
            data["dependencies"]["manager"] = "NuGet"
            data["dependencies"]["total"] = len(data["dependencies"]["items"])

    # packages.config (older .NET)
    if data["dependencies"]["manager"] == "NOT DETECTED":
        pkgcfg = _run("find . -name 'packages.config' -not -path '*/bin/*' | head -3", cwd)
        for cfg_file in _lines(pkgcfg):
            content = _run(f"cat '{cfg_file}'", cwd)
            pkgs = re.findall(r'id="([^"]+)"\s+version="([^"]+)"', content)
            for name, version in pkgs:
                data["dependencies"]["items"].append({"name": name, "version": version})
        if data["dependencies"]["items"]:
            data["dependencies"]["manager"] = "NuGet (packages.config)"
            data["dependencies"]["total"] = len(data["dependencies"]["items"])

    # ERP-specific patterns
    erp_patterns = {
        "SAP": "sap\\|SAP\\|BAPI\\|RFC\\|SapNco\\|SAPConnector",
        "TOTVS": "totvs\\|TOTVS\\|protheus\\|Protheus\\|advpl\\|ADVPL",
        "Oracle ERP": "oracle.*erp\\|OracleERP\\|fusion.*cloud",
    }
    for erp_name, pattern in erp_patterns.items():
        erp_found = _run(f"grep -rln '{pattern}' {inc_all} --include='*.config' --include='*.json' --include='*.xml' 2>/dev/null | grep -v node_modules | grep -v vendor | grep -v bin | grep -v obj | head -5", cwd)
        if _lines(erp_found):
            if not any(i["service"] == erp_name for i in data["integrations"]):
                data["integrations"].append({"service": erp_name, "file": _lines(erp_found)[0].lstrip("./"), "line": "—"})

    # Java Spring detection
    spring = _run("grep -rln '@RestController\\|@RequestMapping\\|@SpringBootApplication\\|@Service\\|@Repository' --include='*.java' 2>/dev/null | grep -v target | grep -v build | head -20", cwd)
    if _lines(spring):
        data["migration"]["frameworks"].append({"name": "Spring MVC", "files": _lines(spring)})
    jpa = _run("grep -rln '@Entity\\|@Table\\|JpaRepository\\|CrudRepository' --include='*.java' 2>/dev/null | grep -v target | head -10", cwd)
    if _lines(jpa):
        data["migration"]["frameworks"].append({"name": "Spring Data JPA", "files": _lines(jpa)})
    thymeleaf = _run("find . -name '*.html' -path '*/templates/*' | grep -v target | wc -l", cwd)
    jsp = _run("find . -name '*.jsp' | grep -v target | wc -l", cwd)
    if _count_lines(thymeleaf) > 0 or _count_lines(jsp) > 0:
        data["migration"]["frameworks"].append({"name": "Thymeleaf/JSP", "files": []})

    # PHP detection (all frameworks + procedural)
    laravel = _run("grep -rln 'Illuminate\\\\\\|Route::get\\|Route::post\\|Eloquent\\|extends Model' --include='*.php' 2>/dev/null | grep -v vendor | head -20", cwd)
    if _lines(laravel):
        data["migration"]["frameworks"].append({"name": "Laravel", "files": _lines(laravel)})
    blade = _run("find . -name '*.blade.php' | grep -v vendor | wc -l", cwd)
    if _count_lines(blade) > 0:
        data["migration"]["frameworks"].append({"name": "Blade Templates", "files": []})

    # Symfony
    symfony = _run("grep -rln 'Symfony\\\\\\|AbstractController\\|@Route\\|#\\[Route' --include='*.php' 2>/dev/null | grep -v vendor | head -20", cwd)
    if _lines(symfony):
        data["migration"]["frameworks"].append({"name": "Symfony", "files": _lines(symfony)})
    twig = _run("find . -name '*.twig' | grep -v vendor | wc -l", cwd)
    if _count_lines(twig) > 0:
        data["migration"]["frameworks"].append({"name": "Twig Templates", "files": []})

    # CodeIgniter
    codeigniter = _run("grep -rln 'CI_Controller\\|CodeIgniter\\|\\$this->load->\\|\\$this->input->' --include='*.php' 2>/dev/null | grep -v vendor | head -20", cwd)
    if _lines(codeigniter):
        data["migration"]["frameworks"].append({"name": "CodeIgniter", "files": _lines(codeigniter)})

    # CakePHP
    cakephp = _run("grep -rln 'CakePHP\\|AppController\\|TableRegistry\\|\\$this->loadModel' --include='*.php' 2>/dev/null | grep -v vendor | head -20", cwd)
    if _lines(cakephp):
        data["migration"]["frameworks"].append({"name": "CakePHP", "files": _lines(cakephp)})

    # Procedural PHP (no framework)
    if not _lines(laravel) and not _lines(symfony) and not _lines(codeigniter) and not _lines(cakephp):
        php_files = _run("find . -name '*.php' | grep -v vendor | grep -v node_modules | wc -l", cwd)
        if _count_lines(php_files) > 0:
            raw_sql = _run("grep -rln 'mysql_query\\|mysqli_query\\|pg_query\\|PDO\\|mysql_connect\\|mysqli_connect' --include='*.php' 2>/dev/null | grep -v vendor | head -20", cwd)
            data["migration"]["frameworks"].append({"name": "PHP Procedural", "files": _lines(raw_sql) if _lines(raw_sql) else []})
            if _lines(raw_sql):
                data["migration"]["blockers"].append({
                    "type": "PHP_RAW_SQL", "severity": "MEDIUM",
                    "description": f"{len(_lines(raw_sql))} files with raw SQL (mysql_query/mysqli/PDO) — no ORM, SQL injection risk",
                    "recommendation": "Migrate to ORM (Prisma/SQLAlchemy/EF Core) with parameterized queries",
                    "files_affected": len(_lines(raw_sql)),
                })

    # PHP-specific blockers
    php_deprecated = _run("grep -rln 'mysql_query\\|mysql_connect\\|ereg\\|split(' --include='*.php' 2>/dev/null | grep -v vendor | head -10", cwd)
    if _lines(php_deprecated):
        data["migration"]["blockers"].append({
            "type": "PHP_DEPRECATED", "severity": "HIGH",
            "description": f"{len(_lines(php_deprecated))} files use deprecated PHP functions (mysql_*, ereg, split)",
            "recommendation": "Update to mysqli/PDO, preg_match, explode before cross-platform migration",
            "files_affected": len(_lines(php_deprecated)),
        })

    # PHP session/globals
    php_globals = _run("grep -rln '\\$_SESSION\\|\\$_GLOBALS\\|session_start\\|\\$_REQUEST' --include='*.php' 2>/dev/null | grep -v vendor | head -20", cwd)
    if _lines(php_globals) and len(_lines(php_globals)) > 5:
        data["migration"]["blockers"].append({
            "type": "PHP_SESSIONS", "severity": "MEDIUM",
            "description": f"{len(_lines(php_globals))} files use PHP sessions/globals — stateful, blocks horizontal scaling",
            "recommendation": "Migrate to JWT/token-based auth with stateless API architecture",
            "files_affected": len(_lines(php_globals)),
        })

    # Delphi detection
    delphi = _run("find . -name '*.pas' -o -name '*.dfm' -o -name '*.dpr' -o -name '*.dpk' | wc -l", cwd)
    if _count_lines(delphi) > 0:
        delphi_files = _lines(_run("find . -name '*.pas' -o -name '*.dfm' | head -20", cwd))
        data["migration"]["frameworks"].append({"name": "Delphi VCL/FMX", "files": delphi_files})
        vcl = _run("grep -rln 'TForm\\|TButton\\|TEdit\\|TDataSet\\|TADOQuery' --include='*.pas' 2>/dev/null | head -20", cwd)
        if _lines(vcl):
            data["migration"]["blockers"].append({
                "type": "DELPHI_VCL", "severity": "HIGH",
                "description": f"{len(_lines(vcl))} Delphi VCL files — UI tightly coupled to business logic",
                "recommendation": "Extract business logic to shared library, rewrite UI as web SPA",
                "files_affected": len(_lines(vcl)),
            })
        bde = _run("grep -rln 'BDE\\|TTable\\|TQuery\\|TDatabase' --include='*.pas' 2>/dev/null | head -10", cwd)
        if _lines(bde):
            data["migration"]["blockers"].append({
                "type": "DELPHI_BDE", "severity": "CRITICAL",
                "description": f"{len(_lines(bde))} files use BDE (Borland Database Engine) — discontinued, no modern equivalent",
                "recommendation": "Replace with ADO/dbExpress first, then migrate to modern ORM",
                "files_affected": len(_lines(bde)),
            })

    # VB6 detection
    vb6 = _run("find . -name '*.frm' -o -name '*.bas' -o -name '*.cls' -o -name '*.vbp' | wc -l", cwd)
    if _count_lines(vb6) > 0:
        vb6_files = _lines(_run("find . -name '*.frm' -o -name '*.bas' -o -name '*.cls' | head -20", cwd))
        data["migration"]["frameworks"].append({"name": "VB6", "files": vb6_files})
        data["migration"]["blockers"].append({
            "type": "VB6", "severity": "CRITICAL",
            "description": f"{_count_lines(vb6)} VB6 files — language EOL, no runtime support on modern OS",
            "recommendation": "Use Mobilize.Net for automated VB6→C# conversion (60-70% automated), then migrate to web",
            "files_affected": _count_lines(vb6),
        })
        activex = _run("grep -rln 'CreateObject\\|ActiveX\\|OLE\\|COM' --include='*.frm' --include='*.bas' --include='*.cls' 2>/dev/null | head -10", cwd)
        if _lines(activex):
            data["migration"]["blockers"].append({
                "type": "ACTIVEX", "severity": "CRITICAL",
                "description": f"{len(_lines(activex))} files use ActiveX/COM — no web equivalent, requires wrapper service",
                "recommendation": "Create REST wrapper service for COM components, replace ActiveX with web components",
                "files_affected": len(_lines(activex)),
            })

    # Database detection (SQL Server, Oracle, MySQL, PostgreSQL)
    sqlserver = _run("grep -rln 'SqlConnection\\|SqlCommand\\|SQLOLEDB\\|Data Source=.*\\\\' --include='*.cs' --include='*.config' --include='*.json' --include='*.pas' --include='*.frm' 2>/dev/null | grep -v bin | grep -v obj | head -10", cwd)
    if _lines(sqlserver):
        data["migration"]["frameworks"].append({"name": "SQL Server", "files": _lines(sqlserver)})
    oracle_db = _run("grep -rln 'OracleConnection\\|Oracle\\.ManagedDataAccess\\|OracleClient' --include='*.cs' --include='*.config' --include='*.pas' 2>/dev/null | grep -v bin | head -10", cwd)
    if _lines(oracle_db):
        data["migration"]["frameworks"].append({"name": "Oracle DB", "files": _lines(oracle_db)})

    # Infrastructure detection
    iis = _run("find . -name 'web.config' -o -name 'applicationHost.config' | grep -v bin | grep -v obj | wc -l", cwd)
    if _count_lines(iis) > 0:
        data["migration"]["frameworks"].append({"name": "IIS", "files": []})
    azdevops = _run("find . -name 'azure-pipelines.yml' -o -name 'azure-pipelines.yaml' | wc -l", cwd)
    if _count_lines(azdevops) > 0:
        data["migration"]["frameworks"].append({"name": "Azure DevOps CI/CD", "files": []})

    # UI library detection
    devexpress = _run("grep -rln 'DevExpress\\|DXGrid\\|XtraGrid\\|DxDataGrid' --include='*.cs' --include='*.cshtml' --include='*.config' --include='*.csproj' 2>/dev/null | grep -v bin | grep -v obj | head -10", cwd)
    if _lines(devexpress):
        data["migration"]["frameworks"].append({"name": "DevExpress Controls", "files": _lines(devexpress)})
    telerik = _run("grep -rln 'Telerik\\|Kendo\\|RadGrid\\|TelerikGrid' --include='*.cs' --include='*.cshtml' --include='*.config' --include='*.csproj' 2>/dev/null | grep -v bin | grep -v obj | head -10", cwd)
    if _lines(telerik):
        data["migration"]["frameworks"].append({"name": "Telerik Controls", "files": _lines(telerik)})

    # SignalR detection
    signalr = _run("grep -rln 'SignalR\\|HubConnection\\|IHubContext' --include='*.cs' --include='*.ts' --include='*.js' --include='*.csproj' 2>/dev/null | grep -v bin | grep -v obj | head -10", cwd)
    if _lines(signalr):
        data["migration"]["frameworks"].append({"name": "SignalR", "files": _lines(signalr)})
