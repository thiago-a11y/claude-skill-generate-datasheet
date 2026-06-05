"""SAP ecosystem detection — identifies SAP project types from codebase patterns.

Pure Python implementation — no shell commands (find/grep).
Uses helpers from codedocs.scanner for cross-platform compatibility.
"""

import os
import re
from codedocs.scanner import _walk_files, _search_files, _find_files_by_name, EXCLUDE_DIRS


SAP_STACKS = {
    "SAP Business One (DI/UI API)": {
        "pattern": r"SAPbouiCOM|SAPbobsCOM|SAPServiceLayerHelper|CompanyService|SAPConnect",
        "extensions": {".cs", ".vb", ".config", ".csproj"},
        "marker_files": [".sln"],
        "description": "SAP B1 addon using DI API (data) and/or UI API (interface)",
    },
    "SAP Business One (Service Layer)": {
        "pattern": r"ServiceLayer|/b1s/v1/|/b1s/v2/|CompanyDB|SessionId.*B1SESSION",
        "extensions": {".cs", ".js", ".ts", ".py", ".php"},
        "marker_files": [],
        "description": "SAP B1 Service Layer REST/OData integration",
    },
    "SAP Fiori / SAPUI5": {
        "pattern": r"sap\.ui\.define|sap\.m\.|sap\.ui\.core|UIComponent\.extend|sap\.ui\.table",
        "extensions": {".js", ".ts", ".xml", ".json"},
        "marker_files": ["webapp/manifest.json", "webapp/Component.js", "webapp/Component.ts"],
        "description": "SAP Fiori / SAPUI5 web application",
    },
    "SAP CAP (Cloud Application Programming)": {
        "pattern": r"cds\.serve|cds\.connect|@sap/cds|using.*from.*cds",
        "extensions": {".cds", ".js", ".ts", ".json", ".yaml"},
        "marker_files": ["mta.yaml", "xs-app.json", "xs-security.json"],
        "description": "SAP BTP Cloud Application Programming model",
    },
    "SAP HANA Native": {
        "pattern": "",
        "extensions": set(),
        "marker_files": [],
        "file_extensions": [".hdbtable", ".hdbview", ".hdbprocedure", ".hdbcalculationview", ".hdbflowgraph", ".xsjs"],
        "description": "SAP HANA native development (HDI artifacts)",
    },
}


def detect_sap_stacks(cwd):
    detected = []

    for stack_name, config in SAP_STACKS.items():
        found = False
        evidence_files = []

        # Check marker files at root
        for marker in config.get("marker_files", []):
            marker_path = os.path.join(cwd, marker)
            if os.path.exists(marker_path):
                found = True
                evidence_files.append(marker)

        # Check file extensions (for HANA native etc.)
        if not found and config.get("file_extensions"):
            for ext in config["file_extensions"]:
                ext_pattern = re.escape(ext) + "$"
                files = _find_files_by_name(cwd, ext_pattern, EXCLUDE_DIRS, max_results=5)
                if files:
                    found = True
                    evidence_files.extend(files[:3])

        # Search file contents for pattern
        if not found and config.get("pattern"):
            files = _search_files(
                cwd, config["pattern"], config.get("extensions"),
                EXCLUDE_DIRS, max_results=10, names_only=True,
            )
            if files:
                found = True
                evidence_files.extend(files[:5])

        # Search for marker files deeper in the tree
        if not found and config.get("marker_files"):
            for marker in config["marker_files"]:
                parts = marker.split("/")
                if len(parts) > 1:
                    fname = parts[-1]
                    pattern = re.escape(fname) + "$"
                    results = _find_files_by_name(cwd, pattern, EXCLUDE_DIRS, max_results=3)
                    # Filter to only those ending with the full marker path
                    marker_normalized = marker.replace("/", os.sep)
                    results = [r for r in results if r.endswith(marker_normalized) or r.endswith(marker)]
                    if results:
                        found = True
                        evidence_files.extend(results[:2])

        if found:
            detected.append({
                "name": stack_name,
                "description": config["description"],
                "evidence": evidence_files,
            })

    # CDS files
    cds_files = _find_files_by_name(cwd, r"\.cds$", EXCLUDE_DIRS, max_results=5)
    if cds_files and not any(s["name"] == "SAP CAP (Cloud Application Programming)" for s in detected):
        detected.append({
            "name": "SAP CDS Models",
            "description": "SAP Core Data Services model definitions",
            "evidence": cds_files[:3],
        })

    # ABAP detection
    abapgit = os.path.exists(os.path.join(cwd, ".abapgit.xml"))
    abap_files = _find_files_by_name(cwd, r"\.abap$", EXCLUDE_DIRS, max_results=5)
    if abapgit or abap_files:
        evidence = []
        if abapgit:
            evidence.append(".abapgit.xml")
        evidence.extend(abap_files[:3])
        detected.append({
            "name": "SAP ABAP (abapGit export)",
            "description": "ABAP repository objects exported via abapGit",
            "evidence": evidence,
        })

    return detected
