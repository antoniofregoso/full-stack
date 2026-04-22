from __future__ import annotations

import re
from typing import Any

LANG_CODE_PATTERN = re.compile(r"^[a-z]{2}(?:-[a-z]{2})?$", re.IGNORECASE)


def is_i18n_dict(data: Any) -> bool:
    if not isinstance(data, dict) or not data:
        return False

    if not all(isinstance(key, str) and LANG_CODE_PATTERN.match(key.strip()) for key in data):
        return False

    return all(not isinstance(value, (dict, list)) for value in data.values())


def filter_i18n_with_fallback(
    data: Any,
    allowed_langs: set[str],
    fallback: str = "en",
) -> Any:
    normalized_allowed_langs = {
        lang.strip().lower()
        for lang in allowed_langs
        if isinstance(lang, str) and lang.strip()
    }
    normalized_fallback = (fallback or "").strip().lower()

    if isinstance(data, dict):
        if is_i18n_dict(data):
            normalized_data = {
                key.strip().lower(): value
                for key, value in data.items()
                if isinstance(key, str) and key.strip()
            }
            filtered = {
                lang: normalized_data[lang]
                for lang in normalized_allowed_langs
                if lang in normalized_data
            }

            if normalized_fallback in normalized_data:
                fallback_value = normalized_data[normalized_fallback]
                for lang in normalized_allowed_langs:
                    if lang not in filtered:
                        filtered[lang] = fallback_value

            return filtered

        return {
            key: filter_i18n_with_fallback(value, normalized_allowed_langs, normalized_fallback)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [
            filter_i18n_with_fallback(item, normalized_allowed_langs, normalized_fallback)
            for item in data
        ]

    return data
