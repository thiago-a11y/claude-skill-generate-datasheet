"""SAP ecosystem detection — identifies SAP project types from codebase patterns."""

import os
from codedocs.scanner import _run, _lines, _count_lines, GREP_EXCLUDE, FIND_EXCLUDE


SAP_STACKS = {
    "SAP Business One (DI/UI API)": {
        "grep_pattern": "SAPbouiCOM\\|SAPbobsCOM\\|SAPServiceLayerHelper\\|CompanyService\\|SAPConnect",
        "include": "--include='*.cs' --include='*.vb' --include='*.config' --include='*.csproj'",
        "marker_files": [".sln"],
        "description": "SAP B1 addon using DI API (data) and/or UI API (interface)",
    },
    "SAP Business One (Service Layer)": {
        "grep_pattern": "ServiceLayer\\|/b1s/v1/\\|/b1s/v2/\\|CompanyDB\\|SessionId.*B1SESSION",
        "include": "--include='*.cs' --include='*.js' --include='*.ts' --include='*.py' --include='*.php'",
        "marker_files": [],
        "description": "SAP B1 Service Layer REST/OData integration",
    },
    "SAP Fiori / SAPUI5": {
        "grep_pattern": "sap\\.ui\\.define\\|sap\\.m\\.\\|sap\\.ui\\.core\\|UIComponent\\.extend\\|sap\\.ui\\.table",
        "include": "--include='*.js' --include='*.ts' --include='*.xml' --include='*.json'",
        "marker_files": ["webapp/manifest.json", "webapp/Component.js", "webapp/Component.ts"],
        "description": "SAP Fiori / SAPUI5 web application",
    },
    "SAP CAP (Cloud Application Programming)": {
        "grep_pattern": "cds\\.serve\\|cds\\.connect\\|@sap/cds\\|using.*from.*cds",
        "include": "--include='*.cds' --include='*.js' --include='*.ts' --include='*.json' --include='*.yaml'",
        "marker_files": ["mta.yaml", "xs-app.json", "xs-security.json"],
        "description": "SAP BTP Cloud Application Programming model",
    },
    "SAP HANA Native": {
        "grep_pattern": "",
        "include": "",
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

        for marker in config.get("marker_files", []):
            marker_path = os.path.join(cwd, marker)
            if os.path.exists(marker_path):
                found = True
                evidence_files.append(marker)

        if not found and config.get("file_extensions"):
            for ext in config["file_extensions"]:
                out = _run(f"find . -name '*{ext}' {FIND_EXCLUDE} | head -5", cwd)
                files = _lines(out)
                if files:
                    found = True
                    evidence_files.extend(f.lstrip("./") for f in files[:3])

        if not found and config.get("grep_pattern"):
            out = _run(
                f"grep -rln '{config['grep_pattern']}' {config['include']} {GREP_EXCLUDE} 2>/dev/null | head -10",
                cwd,
            )
            files = _lines(out)
            if files:
                found = True
                evidence_files.extend(f.lstrip("./") for f in files[:5])

        if not found and config.get("marker_files"):
            for marker in config["marker_files"]:
                parts = marker.split("/")
                if len(parts) > 1:
                    search = _run(f"find . -path '*/{marker}' {FIND_EXCLUDE} | head -3", cwd)
                    results = _lines(search)
                    if results:
                        found = True
                        evidence_files.extend(f.lstrip("./") for f in results[:2])

        if found:
            detected.append({
                "name": stack_name,
                "description": config["description"],
                "evidence": evidence_files,
            })

    cds_files = _run(f"find . -name '*.cds' {FIND_EXCLUDE} | head -5", cwd)
    if _lines(cds_files) and not any(s["name"] == "SAP CAP (Cloud Application Programming)" for s in detected):
        detected.append({
            "name": "SAP CDS Models",
            "description": "SAP Core Data Services model definitions",
            "evidence": [f.lstrip("./") for f in _lines(cds_files)[:3]],
        })

    abapgit = os.path.exists(os.path.join(cwd, ".abapgit.xml"))
    abap_files = _run(f"find . -name '*.abap' {FIND_EXCLUDE} | head -5", cwd)
    if abapgit or _lines(abap_files):
        evidence = []
        if abapgit:
            evidence.append(".abapgit.xml")
        evidence.extend(f.lstrip("./") for f in _lines(abap_files)[:3])
        detected.append({
            "name": "SAP ABAP (abapGit export)",
            "description": "ABAP repository objects exported via abapGit",
            "evidence": evidence,
        })

    return detected
