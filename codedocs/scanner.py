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
