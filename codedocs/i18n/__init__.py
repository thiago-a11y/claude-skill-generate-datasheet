"""Lightweight i18n — loads JSON dictionaries, supports dot notation and fallback."""

import json
import os

_translations = {}
DEFAULT_LANG = "pt-BR"
SUPPORTED_LANGS = ("pt-BR", "en-US")


def _load(lang):
    if lang not in _translations:
        filename = lang.replace("-", "_") + ".json"
        path = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                _translations[lang] = json.load(f)
        except FileNotFoundError:
            _translations[lang] = {}
    return _translations[lang]


def t(key, lang=None):
    lang = lang or DEFAULT_LANG
    parts = key.split(".", 1)

    for try_lang in (lang, "en-US"):
        data = _load(try_lang)
        if len(parts) == 2:
            val = data.get(parts[0], {}).get(parts[1])
        else:
            val = data.get(parts[0])
        if val is not None:
            return val

    return key
