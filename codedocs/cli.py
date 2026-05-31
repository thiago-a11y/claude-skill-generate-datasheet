"""CLI interface — zero dependencies, pure argparse."""

import argparse
import os
import sys
import webbrowser
from pathlib import Path

from codedocs import __version__
from codedocs.scanner import scan
from codedocs.renderer import render_sales_datasheet, render_technical_spec, render_scan_report, render_migration_plan
from codedocs.migration import analyze_migration


RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
DIM = "\033[2m"


def _progress(step, total, label):
    bar_len = 20
    filled = int(bar_len * step / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    pct = int(100 * step / total)
    print(f"\r  {bar} {pct:3d}% {label:<40}", end="", flush=True)
    if step == total:
        print()


def _print_summary(data):
    langs = data["languages"]
    total_files = sum(v["files"] for v in langs.values())
    total_loc = sum(v["lines"] for v in langs.values())

    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  SCAN RESULTS — {data['project']['name']}{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}\n")

    print(f"  {CYAN}Languages{RESET}")
    for lang, info in sorted(langs.items(), key=lambda x: -x[1]["files"]):
        print(f"    {lang:<15} {info['files']:>5} files  {info['lines']:>8} lines")
    print(f"    {'TOTAL':<15} {total_files:>5} files  {total_loc:>8} lines")

    print(f"\n  {CYAN}Endpoints{RESET}        {len(data['endpoints'])} detected")
    print(f"  {CYAN}Database{RESET}         {len(data['database']['tables'])} tables, {len(data['database']['migrations'])} migrations")
    print(f"  {CYAN}Auth{RESET}             {data['auth']['method']}", end="")
    if data["auth"]["mfa"]:
        print(f" + MFA", end="")
    if data["auth"]["rbac"]:
        print(f" + RBAC", end="")
    print()

    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = len(data["security"])
    sec_color = GREEN if sec_count >= 7 else YELLOW if sec_count >= 4 else RED
    print(f"  {CYAN}Security{RESET}         {sec_color}{sec_count}/{sec_total} controls detected{RESET}")

    print(f"  {CYAN}Integrations{RESET}     {len(data['integrations'])} external services")
    print(f"  {CYAN}Tests{RESET}            {data['tests']['test_files']} test files / {data['tests']['source_files']} source files")

    if data["git"]["commits"] > 0:
        print(f"  {CYAN}Git{RESET}              {data['git']['commits']} commits, {len(data['git']['contributors'])} contributors, {data['git']['recent_commits']} last 30d")

    todo_color = GREEN if data["health"]["todos"] < 10 else YELLOW if data["health"]["todos"] < 50 else RED
    print(f"  {CYAN}Code Health{RESET}      {todo_color}{data['health']['todos']} TODOs/FIXMEs{RESET}")
    print(f"  {CYAN}Dependencies{RESET}     {data['dependencies']['total']} ({data['dependencies']['manager']})")
    print(f"  {CYAN}Existing Docs{RESET}    {len(data['existing_docs'])} markdown files")

    # Health score
    score = _calc_health_score(data)
    score_color = GREEN if score >= 70 else YELLOW if score >= 40 else RED
    print(f"\n  {BOLD}Health Score:     {score_color}{score}/100{RESET}")
    print()


def _calc_health_score(data):
    scores = []

    # Test coverage (20%)
    if data["tests"]["source_files"] > 0:
        ratio = data["tests"]["test_files"] / data["tests"]["source_files"]
        scores.append(min(100, int(ratio * 200)) * 0.20)
    else:
        scores.append(0)

    # Security (20%)
    sec_count = sum(1 for v in data["security"].values() if v["detected"])
    sec_total = max(1, len(data["security"]))
    scores.append(int(sec_count / sec_total * 100) * 0.20)

    # Tech debt (15%)
    loc = max(1, data["health"]["loc"])
    debt_per_kloc = data["health"]["todos"] / (loc / 1000)
    debt_score = max(0, 100 - int(debt_per_kloc * 15))
    scores.append(debt_score * 0.15)

    # Documentation (15%)
    doc_count = len(data["existing_docs"])
    doc_score = min(100, doc_count * 12)
    scores.append(doc_score * 0.15)

    # Git health (15%)
    contributors = len(data["git"]["contributors"])
    git_score = min(100, contributors * 20) if contributors > 0 else 0
    scores.append(git_score * 0.15)

    # Dependency management (15%)
    dep_score = 80 if data["dependencies"]["manager"] != "NOT DETECTED" else 20
    scores.append(dep_score * 0.15)

    return min(100, int(sum(scores)))


def main():
    parser = argparse.ArgumentParser(
        prog="codedocs",
        description="CodeDocs — Offline codebase documentation generator. Zero AI, zero internet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m codedocs /path/to/project
  python -m codedocs . --output ./docs
  python -m codedocs /project --no-browser
  python -m codedocs /project --name "My Product" --company "My Company"
        """,
    )
    parser.add_argument("path", help="Path to the project to scan")
    parser.add_argument("--output", "-o", default=None, help="Output directory (default: <path>/codedocs-output)")
    parser.add_argument("--name", default=None, help="Product name (default: directory name)")
    parser.add_argument("--company", default=None, help="Company name")
    parser.add_argument("--no-browser", action="store_true", help="Don't open report in browser after scan")
    parser.add_argument("--no-migration", action="store_true", help="Skip migration plan generation")
    parser.add_argument("--target", default=None, help="Focus on specific target (react, angular, blazor, go, vue). Default: show all options")
    parser.add_argument("--erp", nargs="*", default=[], help="ERP integrations to plan (SAP, TOTVS, Sankhya, Senior, Oracle)")
    parser.add_argument("--version", action="version", version=f"codedocs {__version__}")
    parser.add_argument("--json", action="store_true", help="Output raw scan data as JSON")
    args = parser.parse_args()

    project_path = os.path.abspath(args.path)
    if not os.path.isdir(project_path):
        print(f"{RED}Error: {project_path} is not a directory{RESET}")
        sys.exit(1)

    output_dir = args.output or os.path.join(project_path, "codedocs-output")

    print(f"\n{BOLD}  CodeDocs v{__version__}{RESET}")
    print(f"  {DIM}Offline codebase documentation generator{RESET}")
    print(f"  {DIM}Zero AI · Zero internet · Zero data egress{RESET}\n")
    print(f"  Scanning: {project_path}\n")

    data = scan(project_path, progress_callback=_progress)

    if args.name:
        data["project"]["name"] = args.name
    if args.company:
        data["project"]["company"] = args.company

    if args.json:
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    _print_summary(data)

    os.makedirs(output_dir, exist_ok=True)

    print(f"  {BOLD}Generating documentation...{RESET}\n")

    outputs = []

    scan_html = render_scan_report(data)
    sales_html = render_sales_datasheet(data)
    tech_html = render_technical_spec(data)

    outputs.append(("scan-report.html", scan_html, "Scan Report"))
    outputs.append(("sales-datasheet.html", sales_html, "Sales Datasheet"))
    outputs.append(("technical-spec.html", tech_html, "Technical Spec"))

    if not args.no_migration:
        erp_list = [e.upper() if e.lower() == "sap" else e.title() for e in args.erp]
        target = args.target or "all"
        plan = analyze_migration(data, target_platform=target, target_erps=erp_list)
        migration_html = render_migration_plan(data, plan)
        outputs.append(("migration-plan.html", migration_html, "Migration Plan"))

        print(f"\n  {CYAN}Migration Analysis{RESET}")
        print(f"    Modules: {plan['summary']['total_modules']}")
        print(f"    Estimated effort: {plan['summary']['total_hours']:,}h (~{plan['summary']['total_weeks']} weeks)")
        print(f"    Critical blockers: {plan['summary']['critical_blockers']}")
        if plan['summary']['erp_integrations']:
            print(f"    ERP integrations: {', '.join(plan['summary']['erp_integrations'])}")

    for filename, content, label in outputs:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  {GREEN}✓{RESET} {label:<20} → {os.path.relpath(filepath)}")

    file_count = len(outputs)
    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"  {GREEN}Done!{RESET} {file_count} files generated in {os.path.relpath(output_dir)}/")
    print(f"  {DIM}Open scan-report.html for the full inventory{RESET}")
    print(f"  {DIM}Open sales-datasheet.html for the sales document{RESET}")
    print(f"  {DIM}Open technical-spec.html for the technical spec{RESET}")
    if args.migration:
        print(f"  {DIM}Open migration-plan.html for the migration roadmap{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}\n")

    open_file = "migration-plan.html" if args.migration else "scan-report.html"
    if not args.no_browser:
        webbrowser.open(f"file://{os.path.abspath(os.path.join(output_dir, open_file))}")
