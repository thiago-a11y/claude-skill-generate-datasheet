"""JSON stdin/stdout bridge for CodeDocs — lets Electron talk to the Python engine.

Protocol:
  IN  (one JSON line on stdin):
    {"command": "scan", "path": "/some/path", "options": {"lang": "pt-BR", "target": "react-node"}}

  OUT (JSON lines on stdout):
    {"type": "progress", "step": 5, "total": 19, "label": "Analyzing endpoints"}
    ...
    {"type": "result", "files": {"scan-report": "<html>...", ...}}

  ERROR:
    {"type": "error", "message": "Path not found: /bad/path"}
"""

import json
import os
import sys
import traceback
import io

# Force UTF-8 on Windows (default cp1252 can't handle unicode chars like ★)
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# When bundled: codedocs/ is in the same directory as this script
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = _THIS_DIR
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from codedocs.scanner import scan
from codedocs.renderer import (
    render_scan_report,
    render_sales_datasheet,
    render_technical_spec,
    render_migration_plan,
    render_decision_brief,
)
from codedocs.migration import analyze_migration
from codedocs.md_renderer import render_all_md


def _emit(obj):
    """Write one JSON line to stdout and flush immediately."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _progress_callback(step, total, label):
    """Forward scanner progress to the Electron side as JSON events."""
    _emit({"type": "progress", "step": step, "total": total, "label": label})


def handle_scan(path, options=None):
    """Run the full CodeDocs pipeline and emit progress + result."""
    options = options or {}
    lang = options.get("lang", "pt-BR")
    target = options.get("target", None)

    # --- scan ---
    data = scan(path, progress_callback=_progress_callback)

    # --- render ---
    files = {}
    files["scan-report"] = render_scan_report(data, lang=lang)
    files["sales-datasheet"] = render_sales_datasheet(data, lang=lang, target=target)
    files["technical-spec"] = render_technical_spec(data, lang=lang, target=target)

    plan = analyze_migration(data, target_platform=target or "all")
    files["migration-plan"] = render_migration_plan(data, plan, lang=lang)
    files["decision-brief"] = render_decision_brief(data, plan, lang=lang)

    # --- markdown docs (full documentation pack) ---
    if options.get("full_docs"):
        md_files = render_all_md(data)
        files["md_docs"] = json.dumps(md_files, ensure_ascii=False)

    _emit({"type": "result", "files": files})


def main():
    """Read one JSON command from stdin, execute it, emit JSON to stdout."""
    try:
        raw = sys.stdin.readline()
        if not raw.strip():
            _emit({"type": "error", "message": "Empty input — expected a JSON command on stdin."})
            sys.exit(1)

        msg = json.loads(raw)
        command = msg.get("command")

        if command != "scan":
            _emit({"type": "error", "message": f"Unknown command: {command}"})
            sys.exit(1)

        path = msg.get("path")
        if not path:
            _emit({"type": "error", "message": "Missing required field: path"})
            sys.exit(1)

        path = os.path.abspath(path)
        if not os.path.isdir(path):
            _emit({"type": "error", "message": f"Path not found or not a directory: {path}"})
            sys.exit(1)

        options = msg.get("options", {})
        handle_scan(path, options)

    except json.JSONDecodeError as exc:
        _emit({"type": "error", "message": f"Invalid JSON: {exc}"})
        sys.exit(1)
    except FileNotFoundError as exc:
        _emit({"type": "error", "message": str(exc)})
        sys.exit(1)
    except Exception:
        _emit({"type": "error", "message": traceback.format_exc()})
        sys.exit(1)


if __name__ == "__main__":
    main()
