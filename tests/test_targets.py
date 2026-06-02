"""Tests for migration target support — react-node, net-blazor, sap-fiori-ui5."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from codedocs.migration import analyze_migration, _resolve_target, TARGET_PLATFORMS

MOCK_DATA = {
    "project": {"name": "TestApp", "scan_date": "2026-01-01", "company": "TestCo",
                "system_type": "web-platform", "primary_stack": "python"},
    "languages": {"python": {"files": 10, "lines": 1000}},
    "endpoints": [],
    "database": {"tables": [], "migrations": []},
    "auth": {"method": "JWT", "evidence": ["auth.py"], "mfa": False, "rbac": True},
    "security": {"cors": {"detected": True, "files": ["app.py"]}},
    "integrations": [],
    "tests": {"test_files": 0, "source_files": 10},
    "git": {"commits": 50, "contributors": ["dev1"], "recent_commits": 5,
            "last_10": [], "bus_factor_modules": {}},
    "health": {"todos": 2, "todo_items": [], "loc": 1000},
    "dependencies": {"manager": "pip", "total": 5, "items": []},
    "existing_docs": [],
    "ghost_features": [],
    "deprecated_functions": [],
    "migration": {"blockers": [], "frameworks": [], "target_framework": "NOT DETECTED",
                  "views": {}, "ef_version": "NOT DETECTED", "has_edmx": False,
                  "stored_procedures": 0, "com_interop": [], "pinvoke": [],
                  "system_web": [], "system_drawing": [], "configs": []},
    "structure": [],
}


def test_resolve_target_aliases():
    assert _resolve_target("react-node") == "react+express"
    assert _resolve_target("net-blazor") == "blazor"
    assert _resolve_target("sap-fiori-ui5") == "sap-fiori-ui5"
    assert _resolve_target("sap") == "sap-fiori-ui5"
    assert _resolve_target("fiori") == "sap-fiori-ui5"
    assert _resolve_target(None) == "all"
    assert _resolve_target("all") == "all"


def test_sap_fiori_in_target_platforms():
    assert "sap-fiori-ui5" in TARGET_PLATFORMS
    sap = TARGET_PLATFORMS["sap-fiori-ui5"]
    assert "SAPUI5" in sap["frontend"]
    assert "OData" in sap["backend"]
    assert len(sap["pros"]) >= 3
    assert len(sap["cons"]) >= 3


def test_analyze_react_node():
    plan = analyze_migration(MOCK_DATA, target_platform="react-node")
    s = plan["summary"]
    assert not s["is_neutral"]
    assert s["target_key"] == "react+express"
    assert s["target_info"]["frontend"] == "React (TypeScript)"
    assert "Express" in s["target_info"]["backend"]


def test_analyze_net_blazor():
    plan = analyze_migration(MOCK_DATA, target_platform="net-blazor")
    s = plan["summary"]
    assert not s["is_neutral"]
    assert s["target_key"] == "blazor"
    assert "Blazor" in s["target_info"]["frontend"]


def test_analyze_sap_fiori():
    plan = analyze_migration(MOCK_DATA, target_platform="sap-fiori-ui5")
    s = plan["summary"]
    assert not s["is_neutral"]
    assert s["target_key"] == "sap-fiori-ui5"
    assert "SAPUI5" in s["target_info"]["frontend"]
    assert "OData" in s["target_info"]["backend"]


def test_analyze_neutral():
    plan = analyze_migration(MOCK_DATA, target_platform="all")
    s = plan["summary"]
    assert s["is_neutral"]
    assert s["target_key"] == "all"


def test_render_targets():
    from codedocs.renderer import render_migration_plan

    for target, expected_badge, expected_text in [
        ("react-node", "selecionado", "NestJS"),
        ("net-blazor", "selecionado", "Blazor"),
        ("sap-fiori-ui5", "selecionado", "Fiori"),
    ]:
        plan = analyze_migration(MOCK_DATA, target_platform=target)
        html = render_migration_plan(MOCK_DATA, plan, lang="pt-BR")
        assert expected_badge in html, f"{target}: missing badge '{expected_badge}'"
        assert expected_text in html, f"{target}: missing text '{expected_text}'"

    plan_neutral = analyze_migration(MOCK_DATA, target_platform="all")
    html_neutral = render_migration_plan(MOCK_DATA, plan_neutral, lang="pt-BR")
    assert "selecionado" not in html_neutral
    assert "RECOMENDADO" in html_neutral


if __name__ == "__main__":
    test_resolve_target_aliases()
    print("✓ Target aliases OK")
    test_sap_fiori_in_target_platforms()
    print("✓ SAP Fiori platform OK")
    test_analyze_react_node()
    print("✓ react-node analysis OK")
    test_analyze_net_blazor()
    print("✓ net-blazor analysis OK")
    test_analyze_sap_fiori()
    print("✓ sap-fiori-ui5 analysis OK")
    test_analyze_neutral()
    print("✓ Neutral mode OK")
    test_render_targets()
    print("✓ Render targets OK")
    print("\nAll target tests passed!")
