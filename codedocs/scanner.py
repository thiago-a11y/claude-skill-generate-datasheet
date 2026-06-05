"""Codebase scanner — pure Python, works on Windows/Mac/Linux.

Replaces all find/grep/wc shell calls with os.walk + re + pathlib.
Keeps git subprocess calls (Git for Windows is widely available).
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


def _run(cmd, cwd, timeout=30):
    """Run a subprocess command (used ONLY for git commands)."""
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
    "abap": [".abap"],
    "cds": [".cds"],
    "hana": [".hdbtable", ".hdbview", ".hdbprocedure", ".hdbcalculationview"],
    "groovy": [".groovy"],
    "xsjs": [".xsjs"],
}

EXCLUDE_DIRS = {
    "node_modules", "vendor", ".git", "dist", "build", "__pycache__",
    ".next", ".nuxt", "target", "bin", "obj", "venv", ".venv",
    ".claude", "worktrees",
}

EXCLUDE_FILE_PATTERNS = [
    re.compile(r"index-.*\.js$"),
    re.compile(r"\.min\.js$"),
    re.compile(r"\.bundle\.js$"),
    re.compile(r"\.chunk\.js$"),
]

# Extra dir patterns to exclude (deploy-*, DEPLOY-*)
EXCLUDE_DIR_PREFIXES = ("deploy-", "DEPLOY-")

REVENUE_KEYWORDS = {"deal", "payment", "invoice", "order", "billing", "subscription", "checkout", "contract", "quote", "proposal", "purchase", "transaction", "revenue", "sale", "price", "cart", "charge"}
ADMIN_KEYWORDS = {"admin", "setting", "config", "manage", "dashboard", "system", "permission", "role"}
READONLY_KEYWORDS = {"list", "get", "fetch", "search", "report", "export", "download", "view", "find", "query", "count", "stat"}

DEPRECATED_PHP_FUNCTIONS = {
    "mysql_query": ("PDO::query() or mysqli_query()", "CRITICAL", "Removed in PHP 7.0"),
    "mysql_connect": ("new PDO() or mysqli_connect()", "CRITICAL", "Removed in PHP 7.0"),
    "mysql_real_escape_string": ("PDO prepared statements", "CRITICAL", "Removed in PHP 7.0"),
    "mysql_fetch_array": ("PDOStatement::fetch() or mysqli_fetch_array()", "HIGH", "Removed in PHP 7.0"),
    "mysql_fetch_assoc": ("PDOStatement::fetch(PDO::FETCH_ASSOC)", "HIGH", "Removed in PHP 7.0"),
    "mysql_num_rows": ("PDOStatement::rowCount() or mysqli_num_rows()", "HIGH", "Removed in PHP 7.0"),
    "mysql_close": ("unset($pdo) or mysqli_close()", "HIGH", "Removed in PHP 7.0"),
    "ereg": ("preg_match()", "HIGH", "Removed in PHP 7.0"),
    "ereg_replace": ("preg_replace()", "HIGH", "Removed in PHP 7.0"),
    "split": ("explode() or preg_split()", "HIGH", "Removed in PHP 7.0"),
    "create_function": ("Anonymous functions (closures)", "HIGH", "Deprecated PHP 7.2, removed PHP 8.0"),
    "each": ("foreach loop", "MEDIUM", "Deprecated PHP 7.2, removed PHP 8.0"),
}

SERVICE_INFO = {
    "stripe": ("critical", "USA"), "paypal": ("critical", "USA"),
    "twilio": ("critical", "USA"), "sendgrid": ("critical", "USA"),
    "firebase": ("critical", "USA"), "supabase": ("critical", "USA"),
    "amazonaws": ("critical", "USA"), "googleapis": ("critical", "USA"),
    "graph.facebook": ("critical", "USA"),
    "api.openai": ("optional", "USA"), "api.anthropic": ("optional", "USA"),
    "mailgun": ("optional", "USA/Europe"), "api.slack": ("optional", "USA"),
    "mqtt": ("critical", "Unknown"), "rabbitmq": ("critical", "Unknown"),
    "redis": ("critical", "Unknown"), "kafka": ("critical", "Unknown"),
    "sentry": ("analytics", "USA"), "datadog": ("analytics", "USA"),
    "newrelic": ("analytics", "USA"), "mixpanel": ("analytics", "USA"),
    "amplitude": ("analytics", "USA"), "segment": ("analytics", "USA"),
    "hotjar": ("analytics", "Europe"),
}

SYSTEM_TYPE_PATTERNS = {
    "CRM": ["crm", "customer", "contact", "lead", "opportunity", "pipeline", "deal"],
    "ERP": ["erp", "inventory", "warehouse", "manufacturing", "procurement", "supply"],
    "E-commerce": ["cart", "checkout", "product", "catalog", "shipping"],
    "SaaS Platform": ["tenant", "subscription", "plan", "billing", "saas"],
}


# ---------------------------------------------------------------------------
# Pure Python helpers (replace find/grep/wc)
# ---------------------------------------------------------------------------

def _should_exclude_dir(dirname, exclude_dirs):
    """Check if a directory name should be excluded."""
    if dirname in exclude_dirs:
        return True
    for prefix in EXCLUDE_DIR_PREFIXES:
        if dirname.lower().startswith(prefix.lower()):
            return True
    return False


def _should_exclude_file(filename):
    """Check if a filename matches exclusion patterns."""
    for pat in EXCLUDE_FILE_PATTERNS:
        if pat.search(filename):
            return True
    return False


def _walk_files(cwd, extensions=None, exclude_dirs=None):
    """Walk directory tree, yield (relative_path, full_path) for matching files.

    Args:
        cwd: Root directory to walk.
        extensions: Optional set/list of extensions to include (e.g. {'.py', '.ts'}).
        exclude_dirs: Set of directory names to skip.

    Yields:
        (relative_path, full_path) tuples.
    """
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS
    if extensions is not None:
        extensions = set(e.lower() for e in extensions)

    for dirpath, dirnames, filenames in os.walk(cwd):
        # Prune excluded directories in-place
        dirnames[:] = [
            d for d in dirnames
            if not _should_exclude_dir(d, exclude_dirs)
        ]

        for fname in filenames:
            if _should_exclude_file(fname):
                continue
            if extensions is not None:
                _, ext = os.path.splitext(fname)
                if ext.lower() not in extensions:
                    continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, cwd)
            yield rel, full


def _search_files(cwd, pattern, extensions=None, exclude_dirs=None, max_results=100, names_only=False):
    """Search file contents with regex.

    Args:
        cwd: Root directory.
        pattern: Regex pattern string.
        extensions: Optional set of file extensions to search.
        exclude_dirs: Set of directory names to skip.
        max_results: Stop after this many matches.
        names_only: If True, return list of relative paths (unique) instead of match details.

    Returns:
        If names_only: list of relative file paths that matched.
        Otherwise: list of {"file": str, "line_number": int, "content": str}.
    """
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error:
        return []

    results = []
    seen_files = set()
    count = 0

    for rel, full in _walk_files(cwd, extensions, exclude_dirs):
        if count >= max_results:
            break
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    if compiled.search(line):
                        if names_only:
                            if rel not in seen_files:
                                seen_files.add(rel)
                                results.append(rel)
                                count += 1
                        else:
                            results.append({
                                "file": rel,
                                "line_number": lineno,
                                "content": line.rstrip("\n\r"),
                            })
                            count += 1
                        if count >= max_results:
                            break
        except (IOError, OSError):
            continue

    return results


def _count_file_lines(filepath):
    """Count lines in a single file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except (IOError, OSError):
        return 0


def _find_files_by_name(cwd, name_pattern, exclude_dirs=None, max_results=30):
    """Find files whose name matches a pattern (shell-style glob via regex).

    Args:
        cwd: Root directory.
        name_pattern: Regex to match against filename (not full path).
        exclude_dirs: Set of directory names to skip.
        max_results: Stop after this many files.

    Returns:
        List of relative paths.
    """
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS
    try:
        compiled = re.compile(name_pattern, re.IGNORECASE)
    except re.error:
        return []

    results = []
    for dirpath, dirnames, filenames in os.walk(cwd):
        dirnames[:] = [
            d for d in dirnames
            if not _should_exclude_dir(d, exclude_dirs)
        ]
        for fname in filenames:
            if compiled.search(fname):
                if _should_exclude_file(fname):
                    continue
                full = os.path.join(dirpath, fname)
                rel = os.path.relpath(full, cwd)
                results.append(rel)
                if len(results) >= max_results:
                    return results
    return results


def _read_file(filepath):
    """Read a file's entire content. Returns empty string on error."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (IOError, OSError):
        return ""


# ---------------------------------------------------------------------------
# Ignore file support
# ---------------------------------------------------------------------------

def _load_codedocsignore(cwd):
    ignore_file = os.path.join(cwd, ".codedocsignore")
    extra = set()
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        extra.add(line.rstrip("/"))
        except IOError:
            pass
    return extra


# ---------------------------------------------------------------------------
# Project name detection
# ---------------------------------------------------------------------------

def _detect_project_name(cwd):
    pkg = os.path.join(cwd, "package.json")
    if os.path.exists(pkg):
        import json as _json
        try:
            with open(pkg, "r", encoding="utf-8") as f:
                pkg_data = _json.load(f)
            name = pkg_data.get("name", "")
            if name and name != "." and len(name) > 1:
                return name
        except (ValueError, IOError):
            pass
    readme = os.path.join(cwd, "README.md")
    if os.path.exists(readme):
        try:
            with open(readme, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            if first_line.startswith("# "):
                return first_line[2:].strip()
        except IOError:
            pass
    return None


# ---------------------------------------------------------------------------
# Main scan function
# ---------------------------------------------------------------------------

def scan(project_path, progress_callback=None):
    p = Path(project_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")

    cwd = str(p)
    extra_ignores = _load_codedocsignore(cwd)
    all_excludes = EXCLUDE_DIRS | extra_ignores

    project_name = _detect_project_name(cwd) or p.name

    data = {
        "project": {"name": project_name, "path": cwd, "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M")},
        "languages": {},
        "structure": [],
        "endpoints": [],
        "database": {"tables": [], "migrations": []},
        "auth": {"method": "NOT DETECTED", "evidence": [], "mfa": False, "rbac": False},
        "security": {},
        "integrations": [],
        "tests": {"test_files": 0, "source_files": 0},
        "ghost_features": [],
        "deprecated_functions": [],
        "sap_stacks": [],
        "git": {"commits": 0, "contributors": [], "recent_commits": 0, "last_10": [], "bus_factor_modules": {}},
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
        ("Classifying endpoints", _classify_endpoints),
        ("Detecting ghost features", _scan_ghost_features),
        ("Analyzing bus factor by module", _scan_bus_factor_modules),
        ("Scanning deprecated functions", _scan_deprecated_functions),
        ("Classifying integrations", _classify_integrations),
        ("Detecting system type", _detect_system_type),
        ("Detecting SAP ecosystem", _scan_sap_ecosystem),
    ]

    for i, (label, fn) in enumerate(steps):
        if progress_callback:
            progress_callback(i + 1, len(steps), label)
        fn(data, cwd, all_excludes)

    return data


# ---------------------------------------------------------------------------
# Scan steps — each receives (data, cwd, excludes)
# ---------------------------------------------------------------------------

def _scan_languages(data, cwd, excludes):
    for lang, exts in LANG_EXTENSIONS.items():
        ext_set = set(e.lower() for e in exts)
        file_count = 0
        loc = 0
        files_counted = 0
        for rel, full in _walk_files(cwd, ext_set, excludes):
            file_count += 1
            if files_counted < 100:
                loc += _count_file_lines(full)
                files_counted += 1
        if file_count > 0:
            if lang in data["languages"]:
                data["languages"][lang]["files"] += file_count
                data["languages"][lang]["lines"] += loc
            else:
                data["languages"][lang] = {"files": file_count, "lines": loc, "extensions": exts}


def _scan_structure(data, cwd, excludes):
    dirs = set()
    for dirpath, dirnames, _ in os.walk(cwd):
        rel = os.path.relpath(dirpath, cwd)
        depth = rel.count(os.sep) if rel != "." else 0
        if depth > 2:
            dirnames.clear()
            continue
        # Prune excluded
        dirnames[:] = [d for d in dirnames if not _should_exclude_dir(d, excludes)]
        # Skip .git* at any level
        basename = os.path.basename(dirpath)
        if basename.startswith(".git") and dirpath != cwd:
            continue
        if basename in excludes and dirpath != cwd:
            continue
        if depth <= 2:
            dirs.add("./" + rel if rel != "." else ".")
    data["structure"] = sorted(dirs)[:50]


def _scan_endpoints(data, cwd, excludes):
    source_exts = {".ts", ".js", ".py", ".php", ".go", ".rs", ".java", ".rb"}

    # Framework-based routing
    route_pattern = re.compile(
        r"router\.|app\.get|app\.post|app\.put|app\.delete|app\.patch|"
        r"Route::|@app\.|@Get|@Post|@Put|@Delete|HandleFunc",
        re.IGNORECASE,
    )

    count = 0
    for rel, full in _walk_files(cwd, source_exts, excludes):
        if count >= 100:
            break
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    if route_pattern.search(line):
                        method = "GET"
                        line_lower = line.lower()
                        for m in ["post", "put", "delete", "patch"]:
                            if m in line_lower:
                                method = m.upper()
                                break

                        path_match = re.search(r"""['"](/[^'"]*?)['"]""", line)
                        path = path_match.group(1) if path_match else "[VERIFY]"

                        data["endpoints"].append({
                            "method": method,
                            "path": path,
                            "file": rel,
                            "line": lineno,
                            "raw": line.strip()[:120],
                        })
                        count += 1
                        if count >= 100:
                            break
        except (IOError, OSError):
            continue

    # PHP file-based routing (api/*.php)
    endpoint_skip = {"env", "config", "install", "migrate", "setup", "seed", "helper", "middleware", "test"}
    for rel, full in _walk_files(cwd, {".php"}, excludes):
        # Only files under an "api" directory
        rel_parts = rel.replace("\\", "/").split("/")
        if "api" not in rel_parts[:-1]:
            continue
        basename = os.path.splitext(os.path.basename(rel))[0].lower()
        if any(skip in basename for skip in endpoint_skip):
            continue
        rel_normalized = rel.replace("\\", "/")
        if any(rel_normalized == ep["file"] for ep in data["endpoints"]):
            continue
        method = "API"
        lower_path = rel_normalized.lower()
        if "get" in lower_path or "list" in lower_path or "fetch" in lower_path:
            method = "GET"
        elif "create" in lower_path or "add" in lower_path or "insert" in lower_path:
            method = "POST"
        elif "update" in lower_path or "edit" in lower_path or "save" in lower_path:
            method = "PUT"
        elif "delete" in lower_path or "remove" in lower_path:
            method = "DELETE"
        path = "/" + rel_normalized.replace(".php", "")
        data["endpoints"].append({
            "method": method,
            "path": path,
            "file": rel_normalized,
            "line": 1,
            "raw": f"PHP file-based endpoint: {rel_normalized}",
        })


def _scan_database(data, cwd, excludes):
    # Find migration files
    migration_pattern = re.compile(r"migrat|schema|\.prisma$|\.sql$", re.IGNORECASE)
    migration_files = []
    for rel, full in _walk_files(cwd, exclude_dirs=excludes):
        fname = os.path.basename(rel).lower()
        if migration_pattern.search(fname):
            migration_files.append("./" + rel.replace("\\", "/"))
            if len(migration_files) >= 30:
                break
    data["database"]["migrations"] = migration_files

    # Find tables
    table_exts = {".sql", ".php", ".py", ".ts", ".prisma"}
    table_pattern = re.compile(
        r"CREATE\s+TABLE|Schema::create|createTable|class\s+\w+.*Migration",
        re.IGNORECASE,
    )
    seen_tables = set()
    count = 0
    for rel, full in _walk_files(cwd, table_exts, excludes):
        if count >= 80:
            break
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    if table_pattern.search(line):
                        table_match = re.search(
                            r"""CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`'"]*(\w+)""",
                            line, re.IGNORECASE,
                        )
                        if not table_match:
                            table_match = re.search(
                                r"""(?:Schema::create|createTable)\s*\(\s*[`'"]+(\w+)""",
                                line, re.IGNORECASE,
                            )
                        table_name = table_match.group(1) if table_match else None
                        if not table_name or table_name.upper() in ("IF", "NOT", "EXISTS", "TABLE"):
                            continue
                        if table_name.lower() in seen_tables:
                            continue
                        seen_tables.add(table_name.lower())
                        data["database"]["tables"].append({
                            "name": table_name,
                            "file": rel.replace("\\", "/"),
                            "line": str(lineno),
                        })
                        count += 1
                        if count >= 80:
                            break
        except (IOError, OSError):
            continue


def _scan_auth(data, cwd, excludes):
    auth_exts = {".ts", ".py", ".php", ".go", ".java"}

    patterns = {
        "jwt": re.compile(r"jwt|JWT|jsonwebtoken|jose", re.IGNORECASE),
        "oauth": re.compile(r"oauth|OAuth|passport", re.IGNORECASE),
        "session": re.compile(r"session|cookie.*auth|express-session", re.IGNORECASE),
        "apikey": re.compile(r"api.key|apiKey|x-api-key|API_KEY", re.IGNORECASE),
    }
    mfa_pattern = re.compile(r"totp|2fa|mfa|two.factor|authenticator", re.IGNORECASE)
    rbac_pattern = re.compile(r"role|permission|isAdmin|authorize|hasRole|guard", re.IGNORECASE)

    auth_files = {"jwt": [], "oauth": [], "session": [], "apikey": []}
    mfa_files = []
    rbac_files = []

    for rel, full in _walk_files(cwd, auth_exts, excludes):
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except (IOError, OSError):
            continue

        rel_normalized = rel.replace("\\", "/")

        for key, pat in patterns.items():
            if pat.search(content) and len(auth_files[key]) < 10:
                auth_files[key].append(rel_normalized)

        if mfa_pattern.search(content) and len(mfa_files) < 5:
            mfa_files.append(rel_normalized)
        if rbac_pattern.search(content) and len(rbac_files) < 10:
            rbac_files.append(rel_normalized)

    if auth_files["jwt"]:
        data["auth"]["method"] = "JWT"
        data["auth"]["evidence"] = auth_files["jwt"]
    elif auth_files["oauth"]:
        data["auth"]["method"] = "OAuth"
        data["auth"]["evidence"] = auth_files["oauth"]
    elif auth_files["session"]:
        data["auth"]["method"] = "Session"
        data["auth"]["evidence"] = auth_files["session"]
    elif auth_files["apikey"]:
        data["auth"]["method"] = "API Key"
        data["auth"]["evidence"] = auth_files["apikey"]

    data["auth"]["mfa"] = len(mfa_files) > 0
    data["auth"]["rbac"] = len(rbac_files) > 0


def _scan_security(data, cwd, excludes):
    sec_exts = {".ts", ".py", ".php", ".go", ".conf"}
    checks = {
        "cors": re.compile(r"cors|Access-Control-Allow", re.IGNORECASE),
        "security_middleware": re.compile(r"helmet|security.headers|header.*X-Frame|header.*X-Content|header.*Strict-Transport", re.IGNORECASE),
        "csrf": re.compile(r"csrf|CSRF|xsrf", re.IGNORECASE),
        "rate_limiting": re.compile(r"rate.limit|throttle|RateLimit", re.IGNORECASE),
        "input_validation": re.compile(r"sanitize|escape|htmlspecialchars|validator|joi|zod|yup", re.IGNORECASE),
        "encryption": re.compile(r"encrypt|decrypt|AES|RSA|crypto\.create|bcrypt|argon", re.IGNORECASE),
        "https_enforced": re.compile(r"HSTS|Strict-Transport|forceSSL|redirect.*https", re.IGNORECASE),
        "audit_logging": re.compile(r"audit.*log|activity.*log|log.*action", re.IGNORECASE),
        "security_headers": re.compile(r"X-Frame-Options|X-Content-Type|Content-Security-Policy|Referrer-Policy", re.IGNORECASE),
    }

    # Initialize all controls
    for control in checks:
        data["security"][control] = {"detected": False, "files": []}

    for rel, full in _walk_files(cwd, sec_exts, excludes):
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except (IOError, OSError):
            continue
        rel_normalized = rel.replace("\\", "/")
        for control, pat in checks.items():
            if pat.search(content) and len(data["security"][control]["files"]) < 5:
                data["security"][control]["detected"] = True
                data["security"][control]["files"].append(rel_normalized)


INTEGRATION_IGNORE_DOMAINS = {
    "radix-ui.com", "shadcn.com", "tailwindcss.com", "fonts.googleapis.com",
    "cdn.jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com",
    "seusite.com", "exemplo.com", "example.com", "empresa.com.br",
    "www.empresa.com", "your-domain.com", "localhost",
    "placeholder.com", "test.com", "foo.com", "bar.com",
}

INTEGRATION_IGNORE_FILES = {"index-", ".min.js", ".bundle.js", ".chunk.js"}


def _scan_integrations(data, cwd, excludes):
    integ_exts = {".ts", ".js", ".py", ".php", ".go"}
    url_pattern = re.compile(
        r"https://.*api|amazonaws|googleapis|graph\.facebook|api\.openai|api\.anthropic|"
        r"stripe|twilio|sendgrid|mailgun|api\.slack|mqtt|rabbitmq|redis",
        re.IGNORECASE,
    )

    seen = set()
    count = 0
    for rel, full in _walk_files(cwd, integ_exts, excludes):
        if count >= 40:
            break
        if any(ign in rel for ign in INTEGRATION_IGNORE_FILES):
            continue
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    if url_pattern.search(line):
                        url_match = re.search(r'(https?://[^\s\'"<>]+)', line)
                        if url_match:
                            parts = url_match.group(1).split("/")
                            domain = parts[2] if len(parts) > 2 else url_match.group(1)
                            if domain in INTEGRATION_IGNORE_DOMAINS or domain in seen:
                                continue
                            if "," in domain:
                                domain = domain.split(",")[0]
                            seen.add(domain)
                            rel_normalized = rel.replace("\\", "/")
                            data["integrations"].append({
                                "service": domain,
                                "file": rel_normalized,
                                "line": str(lineno),
                            })
                            count += 1
                            if count >= 40:
                                break
        except (IOError, OSError):
            continue

    # Keyword-based detection for services not found via URLs
    kw_exts = {".ts", ".py", ".php", ".go", ".yml", ".yaml"}
    keywords = {
        "stripe": "Stripe", "twilio": "Twilio", "sendgrid": "SendGrid",
        "mailgun": "Mailgun", "sentry": "Sentry", "datadog": "Datadog",
        "firebase": "Firebase", "supabase": "Supabase",
        "mqtt": "MQTT", "redis": "Redis",
        "rabbitmq": "RabbitMQ", "kafka": "Kafka",
    }
    for kw, name in keywords.items():
        if any(name.lower() in i["service"].lower() for i in data["integrations"]):
            continue
        found_files = _search_files(cwd, kw, kw_exts, excludes, max_results=5, names_only=True)
        found_files = [f for f in found_files if not any(ign in f for ign in INTEGRATION_IGNORE_FILES)]
        if found_files:
            data["integrations"].append({
                "service": name,
                "file": found_files[0].replace("\\", "/"),
                "line": "—",
            })


def _scan_tests(data, cwd, excludes):
    test_pattern = re.compile(
        r"\.test\.|\.spec\.|^test_|_test\.|Test\.php$|_test\.go$",
    )
    source_exts = {".ts", ".js", ".py", ".php", ".go", ".rs", ".java"}
    test_not_pattern = re.compile(r"\.test\.|\.spec\.|test_")

    test_count = 0
    source_count = 0
    for rel, full in _walk_files(cwd, source_exts, excludes):
        fname = os.path.basename(rel)
        if test_pattern.search(fname):
            test_count += 1
        elif not test_not_pattern.search(fname):
            source_count += 1

    data["tests"]["test_files"] = test_count
    data["tests"]["source_files"] = source_count


def _scan_git(data, cwd, excludes):
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


def _scan_health(data, cwd, excludes):
    health_exts = {".ts", ".js", ".py", ".php", ".go", ".rs", ".java"}
    todo_pattern = re.compile(r"TODO[^S]|TODO$|FIXME|HACK[^a-z]|XXX[^a-z]|WORKAROUND", re.IGNORECASE)
    todo_detail_pattern = re.compile(r"TODO[^S]|TODO$|FIXME|HACK[^a-z]", re.IGNORECASE)

    todo_count = 0
    total_loc = 0
    todo_items_collected = 0

    for rel, full in _walk_files(cwd, health_exts, excludes):
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    total_loc += 1
                    if todo_pattern.search(line):
                        todo_count += 1
                    if todo_detail_pattern.search(line) and todo_items_collected < 20:
                        data["health"]["todo_items"].append({
                            "file": rel.replace("\\", "/"),
                            "line": str(lineno),
                            "content": line.strip()[:100],
                        })
                        todo_items_collected += 1
        except (IOError, OSError):
            continue

    data["health"]["todos"] = todo_count
    data["health"]["loc"] = total_loc


def _scan_dependencies(data, cwd, excludes):
    pkg = os.path.join(cwd, "package.json")
    composer = os.path.join(cwd, "composer.json")
    req = os.path.join(cwd, "requirements.txt")
    gomod = os.path.join(cwd, "go.mod")
    cargo = os.path.join(cwd, "Cargo.toml")

    if os.path.exists(pkg):
        data["dependencies"]["manager"] = "npm"
        import json as _json
        try:
            with open(pkg, "r", encoding="utf-8") as f:
                pkg_data = _json.load(f)
            for section in ("dependencies", "devDependencies"):
                for name, version in pkg_data.get(section, {}).items():
                    data["dependencies"]["items"].append({"name": name, "version": version})
        except (ValueError, KeyError, IOError):
            pass
        data["dependencies"]["total"] = len(data["dependencies"]["items"])

    elif os.path.exists(composer):
        data["dependencies"]["manager"] = "composer"
        content = _read_file(composer)
        deps = re.findall(r'"([^"]+/[^"]+)":\s*"([^"]+)"', content)
        for name, version in deps:
            data["dependencies"]["items"].append({"name": name, "version": version})
        data["dependencies"]["total"] = len(data["dependencies"]["items"])

    elif os.path.exists(req):
        data["dependencies"]["manager"] = "pip"
        content = _read_file(req)
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                parts = line.split("==")
                data["dependencies"]["items"].append({"name": parts[0].strip(), "version": parts[1].strip()})
            else:
                data["dependencies"]["items"].append({"name": line.strip(), "version": "latest"})
        data["dependencies"]["total"] = len(data["dependencies"]["items"])

    elif os.path.exists(gomod):
        data["dependencies"]["manager"] = "go mod"
    elif os.path.exists(cargo):
        data["dependencies"]["manager"] = "cargo"


def _scan_docs(data, cwd, excludes):
    md_files = []
    for rel, full in _walk_files(cwd, {".md"}, excludes):
        md_files.append("./" + rel.replace("\\", "/"))
        if len(md_files) >= 30:
            break
    data["existing_docs"] = sorted(md_files)


def _scan_migration(data, cwd, excludes):
    cs_exts = {".cs", ".csproj", ".sln", ".config"}
    all_exts = {".cs", ".ts", ".js", ".py", ".php", ".go", ".java"}

    # .NET target framework
    for rel, full in _walk_files(cwd, {".csproj"}, excludes):
        content = _read_file(full)
        match = re.search(r">(net\S+|v\d+\.\d+)<", content)
        if match:
            data["migration"]["target_framework"] = match.group(1)
            break

    # MVC controllers
    controller_pattern = re.compile(
        r"Controller|\[HttpGet\]|\[HttpPost\]|\[Route\]|\[ApiController\]"
    )
    controller_files = _search_files(cwd, controller_pattern.pattern, {".cs"}, excludes, max_results=30, names_only=True)
    controller_files = [f for f in controller_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if controller_files:
        data["migration"]["frameworks"].append({"name": "ASP.NET MVC/API", "files": controller_files})

    # Web Forms
    aspx_files = _find_files_by_name(cwd, r"\.(aspx|ascx|master)$", excludes)
    aspx_files = [f for f in aspx_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    aspx_count = len(aspx_files)
    if aspx_count > 0:
        data["migration"]["views"]["aspx"] = aspx_count
        data["migration"]["frameworks"].append({"name": "Web Forms", "files": aspx_files[:20]})
        data["migration"]["blockers"].append({
            "type": "WEB_FORMS", "severity": "HIGH",
            "description": f"{aspx_count} Web Forms pages — no direct .NET Core equivalent",
            "recommendation": "Strangler Fig pattern: YARP proxy + migrate page by page",
            "files_affected": aspx_count,
        })

    # Razor views (.cshtml)
    cshtml_files = _find_files_by_name(cwd, r"\.cshtml$", excludes)
    cshtml_files = [f for f in cshtml_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    data["migration"]["views"]["cshtml"] = len(cshtml_files)

    # Razor components (.razor)
    razor_files = _find_files_by_name(cwd, r"\.razor$", excludes)
    razor_files = [f for f in razor_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    data["migration"]["views"]["razor"] = len(razor_files)

    # WinForms
    winforms_files = _search_files(
        cwd, r"System\.Windows\.Forms|InitializeComponent|partial class.*Form",
        {".cs"}, excludes, max_results=20, names_only=True,
    )
    winforms_files = [f for f in winforms_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if winforms_files:
        data["migration"]["frameworks"].append({"name": "WinForms", "files": winforms_files})
        data["migration"]["blockers"].append({
            "type": "WINFORMS", "severity": "HIGH",
            "description": f"{len(winforms_files)} WinForms files — UI tightly coupled to business logic",
            "recommendation": "Extract business logic to shared library, rewrite UI in web framework",
            "files_affected": len(winforms_files),
        })

    # WPF (.xaml)
    xaml_files = _find_files_by_name(cwd, r"\.xaml$", excludes)
    xaml_files = [f for f in xaml_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if xaml_files:
        data["migration"]["frameworks"].append({"name": "WPF", "files": xaml_files[:20]})

    # Entity Framework
    ef_files = _search_files(
        cwd, r"DbContext|DbSet|ObjectContext|EntityFramework",
        {".cs", ".config", ".csproj"}, excludes, max_results=15, names_only=True,
    )
    ef_files = [f for f in ef_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if ef_files:
        edmx_files = _find_files_by_name(cwd, r"\.edmx$", excludes)
        edmx_files = [f for f in edmx_files if "bin" not in f.split(os.sep)]
        edmx_count = len(edmx_files)
        data["migration"]["has_edmx"] = edmx_count > 0
        if edmx_count > 0:
            data["migration"]["ef_version"] = "EF6 (EDMX)"
            data["migration"]["blockers"].append({
                "type": "EF6_EDMX", "severity": "MEDIUM",
                "description": f"{edmx_count} EDMX files — conceptual break migrating to EF Core",
                "recommendation": "Migrate to EF Core Code-First with DbContext",
                "files_affected": edmx_count,
            })
        else:
            efcore_files = _search_files(
                cwd, r"Microsoft\.EntityFrameworkCore",
                {".cs", ".csproj"}, excludes, max_results=5, names_only=True,
            )
            data["migration"]["ef_version"] = "EF Core" if efcore_files else "EF6 (Code-First)"

    # Stored procedures
    sp_matches = _search_files(
        cwd, r"StoredProcedure|EXEC\s|EXECUTE\s|sp_|usp_|CommandType\.StoredProcedure",
        {".cs", ".sql", ".php", ".py"}, excludes, max_results=200,
    )
    sp_matches = [m for m in sp_matches if "bin" not in m["file"].split(os.sep) and "obj" not in m["file"].split(os.sep)]
    sp_count = len(sp_matches)
    data["migration"]["stored_procedures"] = sp_count
    if sp_count > 5:
        data["migration"]["blockers"].append({
            "type": "STORED_PROCEDURES", "severity": "MEDIUM",
            "description": f"{sp_count} stored procedure references — business logic trapped in DB",
            "recommendation": "Extract SP logic to service layer before migration",
            "files_affected": sp_count,
        })

    # COM Interop
    com_matches = _search_files(
        cwd, r"DllImport|ComImport|TypeLib|Interop|Marshal\.",
        {".cs"}, excludes, max_results=20,
    )
    com_matches = [m for m in com_matches if "bin" not in m["file"].split(os.sep) and "obj" not in m["file"].split(os.sep)]
    for m in com_matches:
        data["migration"]["com_interop"].append({
            "file": m["file"].replace("\\", "/"),
            "line": str(m["line_number"]),
            "content": m["content"].strip()[:100],
        })
    if data["migration"]["com_interop"]:
        data["migration"]["blockers"].append({
            "type": "COM_INTEROP", "severity": "CRITICAL",
            "description": f"{len(data['migration']['com_interop'])} COM/Interop references — Windows-only, blocks containerization",
            "recommendation": "Create wrapper service or replace with managed alternatives",
            "files_affected": len(data["migration"]["com_interop"]),
        })

    # P/Invoke
    pinvoke_matches = _search_files(
        cwd, r"DllImport.*kernel32|DllImport.*user32|DllImport.*gdi32|DllImport.*advapi32|DllImport.*shell32",
        {".cs"}, excludes, max_results=20,
    )
    pinvoke_matches = [m for m in pinvoke_matches if "bin" not in m["file"].split(os.sep) and "obj" not in m["file"].split(os.sep)]
    for m in pinvoke_matches:
        data["migration"]["pinvoke"].append({
            "file": m["file"].replace("\\", "/"),
            "line": str(m["line_number"]),
            "content": m["content"].strip()[:100],
        })
    if data["migration"]["pinvoke"]:
        data["migration"]["blockers"].append({
            "type": "PINVOKE", "severity": "CRITICAL",
            "description": f"{len(data['migration']['pinvoke'])} P/Invoke calls — blocks Linux/container deployment",
            "recommendation": "Replace with cross-platform .NET APIs or isolate in Windows-only service",
            "files_affected": len(data["migration"]["pinvoke"]),
        })

    # System.Web
    sysweb_files = _search_files(
        cwd, r"System\.Web|HttpContext\.Current|HttpApplication",
        {".cs"}, excludes, max_results=30, names_only=True,
    )
    sysweb_files = [f for f in sysweb_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    data["migration"]["system_web"] = sysweb_files
    if sysweb_files:
        data["migration"]["blockers"].append({
            "type": "SYSTEM_WEB", "severity": "HIGH",
            "description": f"{len(sysweb_files)} files use System.Web — not available in .NET Core",
            "recommendation": "Use System.Web Adapters for incremental migration",
            "files_affected": len(sysweb_files),
        })

    # System.Drawing
    sysdraw_files = _search_files(
        cwd, r"System\.Drawing|System\.Drawing\.Common",
        {".cs", ".csproj"}, excludes, max_results=10, names_only=True,
    )
    sysdraw_files = [f for f in sysdraw_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    data["migration"]["system_drawing"] = sysdraw_files
    if sysdraw_files:
        data["migration"]["blockers"].append({
            "type": "SYSTEM_DRAWING", "severity": "MEDIUM",
            "description": f"{len(sysdraw_files)} files use System.Drawing — Windows-only in .NET 6+",
            "recommendation": "Replace with SixLabors.ImageSharp (cross-platform)",
            "files_affected": len(sysdraw_files),
        })

    # Config files
    configs = []
    for cfg in ["web.config", "app.config", "appsettings.json", "Startup.cs", "Program.cs", "Global.asax"]:
        found = _find_files_by_name(cwd, re.escape(cfg) + "$", excludes, max_results=5)
        found = [f for f in found if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
        for f in found:
            configs.append("./" + f.replace("\\", "/"))
    data["migration"]["configs"] = configs

    # NuGet packages from .csproj
    if data["dependencies"]["manager"] == "NOT DETECTED":
        csproj_files = _find_files_by_name(cwd, r"\.csproj$", excludes, max_results=5)
        csproj_files = [f for f in csproj_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
        for proj_rel in csproj_files:
            proj_full = os.path.join(cwd, proj_rel)
            content = _read_file(proj_full)
            pkgs = re.findall(r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"', content)
            for name, version in pkgs:
                data["dependencies"]["items"].append({"name": name, "version": version})
        if data["dependencies"]["items"]:
            data["dependencies"]["manager"] = "NuGet"
            data["dependencies"]["total"] = len(data["dependencies"]["items"])

    # packages.config (older .NET)
    if data["dependencies"]["manager"] == "NOT DETECTED":
        pkgcfg_files = _find_files_by_name(cwd, r"^packages\.config$", excludes, max_results=3)
        pkgcfg_files = [f for f in pkgcfg_files if "bin" not in f.split(os.sep)]
        for cfg_rel in pkgcfg_files:
            cfg_full = os.path.join(cwd, cfg_rel)
            content = _read_file(cfg_full)
            pkgs = re.findall(r'id="([^"]+)"\s+version="([^"]+)"', content)
            for name, version in pkgs:
                data["dependencies"]["items"].append({"name": name, "version": version})
        if data["dependencies"]["items"]:
            data["dependencies"]["manager"] = "NuGet (packages.config)"
            data["dependencies"]["total"] = len(data["dependencies"]["items"])

    # ERP-specific patterns (only source files, no bundled JS)
    erp_patterns = {
        "SAP": r"BAPI|SapNco|SAPConnector|sap\.client",
        "TOTVS": r"protheus|Protheus|advpl|ADVPL|totvs\.api",
        "Oracle ERP": r"OracleERP|fusion.*cloud|oracle.*erp",
    }
    erp_exts = {".cs", ".php", ".py", ".ts", ".java", ".config", ".xml"}
    for erp_name, pattern in erp_patterns.items():
        erp_found = _search_files(cwd, pattern, erp_exts, excludes, max_results=5, names_only=True)
        erp_found = [f for f in erp_found if not any(ign in f for ign in INTEGRATION_IGNORE_FILES)]
        if erp_found:
            if not any(i["service"] == erp_name for i in data["integrations"]):
                data["integrations"].append({
                    "service": erp_name,
                    "file": erp_found[0].replace("\\", "/"),
                    "line": "—",
                })

    # Java Spring detection
    spring_files = _search_files(
        cwd, r"@RestController|@RequestMapping|@SpringBootApplication|@Service|@Repository",
        {".java"}, excludes, max_results=20, names_only=True,
    )
    spring_files = [f for f in spring_files if "target" not in f.split(os.sep) and "build" not in f.split(os.sep)]
    if spring_files:
        data["migration"]["frameworks"].append({"name": "Spring MVC", "files": spring_files})

    jpa_files = _search_files(
        cwd, r"@Entity|@Table|JpaRepository|CrudRepository",
        {".java"}, excludes, max_results=10, names_only=True,
    )
    jpa_files = [f for f in jpa_files if "target" not in f.split(os.sep)]
    if jpa_files:
        data["migration"]["frameworks"].append({"name": "Spring Data JPA", "files": jpa_files})

    thymeleaf_files = _find_files_by_name(cwd, r"\.html$", excludes, max_results=50)
    thymeleaf_in_templates = [f for f in thymeleaf_files if "templates" in f.split(os.sep) and "target" not in f.split(os.sep)]
    jsp_files = _find_files_by_name(cwd, r"\.jsp$", excludes, max_results=10)
    jsp_files = [f for f in jsp_files if "target" not in f.split(os.sep)]
    if thymeleaf_in_templates or jsp_files:
        data["migration"]["frameworks"].append({"name": "Thymeleaf/JSP", "files": []})

    # PHP detection (all frameworks + procedural)
    laravel_files = _search_files(
        cwd, r"Illuminate\\|Route::get|Route::post|Eloquent|extends Model",
        {".php"}, excludes, max_results=20, names_only=True,
    )
    if laravel_files:
        data["migration"]["frameworks"].append({"name": "Laravel", "files": laravel_files})

    blade_files = _find_files_by_name(cwd, r"\.blade\.php$", excludes, max_results=10)
    if blade_files:
        data["migration"]["frameworks"].append({"name": "Blade Templates", "files": []})

    # Symfony
    symfony_files = _search_files(
        cwd, r"Symfony\\|AbstractController|@Route|#\[Route",
        {".php"}, excludes, max_results=20, names_only=True,
    )
    if symfony_files:
        data["migration"]["frameworks"].append({"name": "Symfony", "files": symfony_files})

    twig_files = _find_files_by_name(cwd, r"\.twig$", excludes, max_results=10)
    if twig_files:
        data["migration"]["frameworks"].append({"name": "Twig Templates", "files": []})

    # CodeIgniter
    codeigniter_files = _search_files(
        cwd, r"CI_Controller|CodeIgniter|\$this->load->|\$this->input->",
        {".php"}, excludes, max_results=20, names_only=True,
    )
    if codeigniter_files:
        data["migration"]["frameworks"].append({"name": "CodeIgniter", "files": codeigniter_files})

    # CakePHP
    cakephp_files = _search_files(
        cwd, r"CakePHP|AppController|TableRegistry|\$this->loadModel",
        {".php"}, excludes, max_results=20, names_only=True,
    )
    if cakephp_files:
        data["migration"]["frameworks"].append({"name": "CakePHP", "files": cakephp_files})

    # Procedural PHP (no framework)
    if not laravel_files and not symfony_files and not codeigniter_files and not cakephp_files:
        php_file_list = list(_walk_files(cwd, {".php"}, excludes))
        if php_file_list:
            raw_sql_files = _search_files(
                cwd, r"mysql_query|mysqli_query|pg_query|PDO|mysql_connect|mysqli_connect",
                {".php"}, excludes, max_results=20, names_only=True,
            )
            data["migration"]["frameworks"].append({
                "name": "PHP Procedural",
                "files": raw_sql_files if raw_sql_files else [],
            })
            if raw_sql_files:
                data["migration"]["blockers"].append({
                    "type": "PHP_RAW_SQL", "severity": "MEDIUM",
                    "description": f"{len(raw_sql_files)} files with raw SQL (mysql_query/mysqli/PDO) — no ORM, SQL injection risk",
                    "recommendation": "Migrate to ORM (Prisma/SQLAlchemy/EF Core) with parameterized queries",
                    "files_affected": len(raw_sql_files),
                })

    # PHP-specific blockers
    php_deprecated_files = _search_files(
        cwd, r"mysql_query|mysql_connect|ereg|split\(",
        {".php"}, excludes, max_results=10, names_only=True,
    )
    if php_deprecated_files:
        data["migration"]["blockers"].append({
            "type": "PHP_DEPRECATED", "severity": "HIGH",
            "description": f"{len(php_deprecated_files)} files use deprecated PHP functions (mysql_*, ereg, split)",
            "recommendation": "Update to mysqli/PDO, preg_match, explode before cross-platform migration",
            "files_affected": len(php_deprecated_files),
        })

    # PHP session/globals
    php_globals_files = _search_files(
        cwd, r"\$_SESSION|\$_GLOBALS|session_start|\$_REQUEST",
        {".php"}, excludes, max_results=20, names_only=True,
    )
    if php_globals_files and len(php_globals_files) > 5:
        data["migration"]["blockers"].append({
            "type": "PHP_SESSIONS", "severity": "MEDIUM",
            "description": f"{len(php_globals_files)} files use PHP sessions/globals — stateful, blocks horizontal scaling",
            "recommendation": "Migrate to JWT/token-based auth with stateless API architecture",
            "files_affected": len(php_globals_files),
        })

    # Delphi detection
    delphi_files = _find_files_by_name(cwd, r"\.(pas|dfm|dpr|dpk)$", excludes, max_results=30)
    if delphi_files:
        delphi_display = [f for f in delphi_files if f.endswith(".pas") or f.endswith(".dfm")][:20]
        data["migration"]["frameworks"].append({"name": "Delphi VCL/FMX", "files": delphi_display})
        vcl_files = _search_files(
            cwd, r"TForm|TButton|TEdit|TDataSet|TADOQuery",
            {".pas"}, excludes, max_results=20, names_only=True,
        )
        if vcl_files:
            data["migration"]["blockers"].append({
                "type": "DELPHI_VCL", "severity": "HIGH",
                "description": f"{len(vcl_files)} Delphi VCL files — UI tightly coupled to business logic",
                "recommendation": "Extract business logic to shared library, rewrite UI as web SPA",
                "files_affected": len(vcl_files),
            })
        bde_files = _search_files(
            cwd, r"BDE|TTable|TQuery|TDatabase",
            {".pas"}, excludes, max_results=10, names_only=True,
        )
        if bde_files:
            data["migration"]["blockers"].append({
                "type": "DELPHI_BDE", "severity": "CRITICAL",
                "description": f"{len(bde_files)} files use BDE (Borland Database Engine) — discontinued, no modern equivalent",
                "recommendation": "Replace with ADO/dbExpress first, then migrate to modern ORM",
                "files_affected": len(bde_files),
            })

    # VB6 detection
    vb6_files = _find_files_by_name(cwd, r"\.(frm|bas|cls|vbp)$", excludes, max_results=30)
    if vb6_files:
        vb6_display = [f for f in vb6_files if f.endswith((".frm", ".bas", ".cls"))][:20]
        data["migration"]["frameworks"].append({"name": "VB6", "files": vb6_display})
        vb6_count = len(vb6_files)
        data["migration"]["blockers"].append({
            "type": "VB6", "severity": "CRITICAL",
            "description": f"{vb6_count} VB6 files — language EOL, no runtime support on modern OS",
            "recommendation": "Use Mobilize.Net for automated VB6→C# conversion (60-70% automated), then migrate to web",
            "files_affected": vb6_count,
        })
        activex_files = _search_files(
            cwd, r"CreateObject|ActiveX|OLE|COM",
            {".frm", ".bas", ".cls"}, excludes, max_results=10, names_only=True,
        )
        if activex_files:
            data["migration"]["blockers"].append({
                "type": "ACTIVEX", "severity": "CRITICAL",
                "description": f"{len(activex_files)} files use ActiveX/COM — no web equivalent, requires wrapper service",
                "recommendation": "Create REST wrapper service for COM components, replace ActiveX with web components",
                "files_affected": len(activex_files),
            })

    # Database detection (SQL Server, Oracle)
    sqlserver_files = _search_files(
        cwd, r"SqlConnection|SqlCommand|SQLOLEDB|Data Source=.*\\\\",
        {".cs", ".config", ".json", ".pas", ".frm"}, excludes, max_results=10, names_only=True,
    )
    sqlserver_files = [f for f in sqlserver_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if sqlserver_files:
        data["migration"]["frameworks"].append({"name": "SQL Server", "files": sqlserver_files})

    oracle_files = _search_files(
        cwd, r"OracleConnection|Oracle\.ManagedDataAccess|OracleClient",
        {".cs", ".config", ".pas"}, excludes, max_results=10, names_only=True,
    )
    oracle_files = [f for f in oracle_files if "bin" not in f.split(os.sep)]
    if oracle_files:
        data["migration"]["frameworks"].append({"name": "Oracle DB", "files": oracle_files})

    # Infrastructure detection
    iis_files = _find_files_by_name(cwd, r"^(web\.config|applicationHost\.config)$", excludes, max_results=5)
    iis_files = [f for f in iis_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if iis_files:
        data["migration"]["frameworks"].append({"name": "IIS", "files": []})

    azdevops_files = _find_files_by_name(cwd, r"^azure-pipelines\.(yml|yaml)$", excludes, max_results=5)
    if azdevops_files:
        data["migration"]["frameworks"].append({"name": "Azure DevOps CI/CD", "files": []})

    # UI library detection
    devexpress_files = _search_files(
        cwd, r"DevExpress|DXGrid|XtraGrid|DxDataGrid",
        {".cs", ".cshtml", ".config", ".csproj"}, excludes, max_results=10, names_only=True,
    )
    devexpress_files = [f for f in devexpress_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if devexpress_files:
        data["migration"]["frameworks"].append({"name": "DevExpress Controls", "files": devexpress_files})

    telerik_files = _search_files(
        cwd, r"Telerik|Kendo|RadGrid|TelerikGrid",
        {".cs", ".cshtml", ".config", ".csproj"}, excludes, max_results=10, names_only=True,
    )
    telerik_files = [f for f in telerik_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if telerik_files:
        data["migration"]["frameworks"].append({"name": "Telerik Controls", "files": telerik_files})

    # SignalR detection
    signalr_files = _search_files(
        cwd, r"SignalR|HubConnection|IHubContext",
        {".cs", ".ts", ".js", ".csproj"}, excludes, max_results=10, names_only=True,
    )
    signalr_files = [f for f in signalr_files if "bin" not in f.split(os.sep) and "obj" not in f.split(os.sep)]
    if signalr_files:
        data["migration"]["frameworks"].append({"name": "SignalR", "files": signalr_files})


def _classify_endpoints(data, cwd, excludes):
    for ep in data["endpoints"]:
        path_lower = ep["path"].lower()
        file_lower = ep["file"].lower()
        combined = path_lower + " " + file_lower
        if any(kw in combined for kw in REVENUE_KEYWORDS):
            ep["criticality"] = "revenue-critical"
        elif any(kw in combined for kw in ADMIN_KEYWORDS):
            ep["criticality"] = "admin"
        elif ep["method"] == "GET" or any(kw in combined for kw in READONLY_KEYWORDS):
            ep["criticality"] = "read-only"
        else:
            ep["criticality"] = "operational"


def _scan_ghost_features(data, cwd, excludes):
    if not os.path.exists(os.path.join(cwd, ".git")):
        return
    unique_files = set(ep["file"] for ep in data["endpoints"])
    for filepath in list(unique_files)[:100]:
        last_commit = _run(f"git log -1 --format='%ci' -- '{filepath}' 2>/dev/null", cwd)
        if last_commit:
            try:
                commit_date = datetime.strptime(last_commit[:10], "%Y-%m-%d")
                days_ago = (datetime.now() - commit_date).days
                if days_ago > 90:
                    data["ghost_features"].append({
                        "file": filepath,
                        "last_commit": last_commit[:10],
                        "days_ago": days_ago,
                    })
            except ValueError:
                pass


def _scan_bus_factor_modules(data, cwd, excludes):
    if not os.path.exists(os.path.join(cwd, ".git")):
        return
    modules = {}
    for ep in data["endpoints"]:
        module = ep["file"].split("/")[0] if "/" in ep["file"] else "root"
        if module not in modules:
            modules[module] = {"files": set(), "endpoints": 0}
        modules[module]["files"].add(ep["file"])
        modules[module]["endpoints"] += 1
    for module, info in modules.items():
        path = f"{module}/" if module != "root" else "."
        contributors = _run(f"git log --format='%an' -- '{path}' 2>/dev/null | sort -u", cwd)
        contribs = _lines(contributors)
        data["git"]["bus_factor_modules"][module] = {
            "contributors": contribs,
            "count": len(contribs),
            "files": len(info["files"]),
            "endpoints": info["endpoints"],
        }


def _scan_deprecated_functions(data, cwd, excludes):
    if "php" not in data["languages"]:
        return
    for func_name, (replacement, severity, reason) in DEPRECATED_PHP_FUNCTIONS.items():
        pattern = re.escape(func_name) + r"\s*\("
        matches = _search_files(cwd, pattern, {".php"}, excludes, max_results=10)
        for m in matches:
            data["deprecated_functions"].append({
                "function": func_name,
                "replacement": replacement,
                "severity": severity,
                "reason": reason,
                "file": m["file"].replace("\\", "/"),
                "line": m["line_number"],
            })


def _classify_integrations(data, cwd, excludes):
    for integ in data["integrations"]:
        service_lower = integ["service"].lower()
        matched = False
        for pattern, (classification, residency) in SERVICE_INFO.items():
            if pattern in service_lower:
                integ["classification"] = classification
                integ["data_residency"] = residency
                matched = True
                break
        if not matched:
            integ["classification"] = "unknown"
            integ["data_residency"] = "Unknown"


def _detect_system_type(data, cwd, excludes):
    all_paths = " ".join(ep["path"].lower() for ep in data["endpoints"])
    all_files = " ".join(ep["file"].lower() for ep in data["endpoints"])
    combined = all_paths + " " + all_files + " " + data["project"]["name"].lower()
    for sys_type, keywords in SYSTEM_TYPE_PATTERNS.items():
        matches = sum(1 for kw in keywords if kw in combined)
        if matches >= 2:
            data["project"]["system_type"] = sys_type
            break
    else:
        data["project"]["system_type"] = "web-platform"
    if data["languages"]:
        primary = max(data["languages"].items(), key=lambda x: x[1]["files"])
        data["project"]["primary_stack"] = primary[0]
    else:
        data["project"]["primary_stack"] = "unknown"


def _scan_sap_ecosystem(data, cwd, excludes):
    from codedocs.sap_detection import detect_sap_stacks
    detected = detect_sap_stacks(cwd)
    data["sap_stacks"] = detected
    for stack in detected:
        if not any(f["name"] == stack["name"] for f in data["migration"]["frameworks"]):
            data["migration"]["frameworks"].append({
                "name": stack["name"],
                "files": stack["evidence"],
            })
