"""Tests for i18n — key parity and language switching."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from codedocs.i18n import t, _load


def _load_json(lang):
    filename = lang.replace("-", "_") + ".json"
    path = os.path.join(os.path.dirname(__file__), "..", "codedocs", "i18n", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _all_keys(d, prefix=""):
    keys = set()
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(_all_keys(v, full))
        else:
            keys.add(full)
    return keys


def test_key_parity():
    pt = _load_json("pt-BR")
    en = _load_json("en-US")
    pt_keys = _all_keys(pt)
    en_keys = _all_keys(en)

    missing_in_pt = en_keys - pt_keys
    missing_in_en = pt_keys - en_keys

    assert not missing_in_pt, f"Keys missing in pt-BR: {missing_in_pt}"
    assert not missing_in_en, f"Keys missing in en-US: {missing_in_en}"


def test_critical_keys_exist():
    critical = [
        "common.risk_score",
        "verdict.title",
        "verdict.diagnosis_0_30",
        "audit.title",
        "scan_report.title",
        "sales.title",
        "tech_spec.title",
        "migration.title",
        "decision.title",
        "decision.what_works",
        "decision.next_3_actions",
        "footer.trust_line",
    ]
    for key in critical:
        for lang in ("pt-BR", "en-US"):
            val = t(key, lang)
            assert val != key, f"Key '{key}' not found for {lang}"


def test_language_switching():
    assert t("decision.what_works", "pt-BR") == "O que funciona bem"
    assert t("decision.what_works", "en-US") == "What works well"

    assert "Próximas 3 Ações" in t("decision.next_3_actions", "pt-BR")
    assert "Next 3 Actions" in t("decision.next_3_actions", "en-US")

    assert "scanner offline" in t("footer.trust_line", "pt-BR").lower()
    assert "offline scanner" in t("footer.trust_line", "en-US").lower()


def test_fallback_to_english():
    val = t("nonexistent.key", "pt-BR")
    assert val == "nonexistent.key"


def test_format_strings():
    result = t("verdict.action_add_tests", "en-US").format(sf=42)
    assert "42" in result

    result = t("product.description", "pt-BR").format(
        name="TestApp", type="aplicação", langs="Python",
        endpoints=10, integrations=3, tables=5, score=50, summary="teste"
    )
    assert "TestApp" in result
    assert "10" in result


def test_decision_brief_generation():
    from codedocs.renderer import render_decision_brief

    data = {
        "project": {"name": "TestApp", "scan_date": "2026-01-01", "company": "TestCo", "system_type": "web-platform", "primary_stack": "python"},
        "languages": {"python": {"files": 10, "lines": 1000}},
        "endpoints": [],
        "database": {"tables": [], "migrations": []},
        "auth": {"method": "JWT", "evidence": ["auth.py"], "mfa": False, "rbac": True},
        "security": {"cors": {"detected": True, "files": ["app.py"]}, "csrf": {"detected": False, "files": []}},
        "integrations": [],
        "tests": {"test_files": 0, "source_files": 10},
        "git": {"commits": 50, "contributors": ["dev1"], "recent_commits": 5, "last_10": [], "bus_factor_modules": {}},
        "health": {"todos": 2, "todo_items": [], "loc": 1000},
        "dependencies": {"manager": "pip", "total": 5, "items": []},
        "existing_docs": [],
        "ghost_features": [],
        "deprecated_functions": [],
    }

    html_pt = render_decision_brief(data, lang="pt-BR")
    assert "O que funciona bem" in html_pt
    assert "What works well" not in html_pt

    html_en = render_decision_brief(data, lang="en-US")
    assert "What works well" in html_en
    assert "O que funciona bem" not in html_en


if __name__ == "__main__":
    test_key_parity()
    print("✓ Key parity OK")
    test_critical_keys_exist()
    print("✓ Critical keys OK")
    test_language_switching()
    print("✓ Language switching OK")
    test_fallback_to_english()
    print("✓ Fallback OK")
    test_format_strings()
    print("✓ Format strings OK")
    test_decision_brief_generation()
    print("✓ Decision Brief generation OK")
    print("\nAll tests passed!")
