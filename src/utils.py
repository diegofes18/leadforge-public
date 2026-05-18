"""Helpers comunes (parsing, normalización de strings, slugify)."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

import pandas as pd


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "x"


def slugify_business(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "lead"


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def normalize_phone(value: object) -> str:
    """Quita espacios, guiones, paréntesis y prefijo +34/0034 para comparar."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = re.sub(r"[\s\-\(\)\.]+", "", str(value))
    if s.startswith("+34"):
        s = s[3:]
    elif s.startswith("0034"):
        s = s[4:]
    elif s.startswith("34") and len(s) == 11:
        s = s[2:]
    return s


def first_address_line(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).split(",")[0].strip().lower()


def extract_city(formatted_address: str) -> str:
    parts = [p.strip() for p in str(formatted_address or "").split(",") if p.strip()]
    if not parts:
        return ""
    last = parts[-1]
    return re.sub(r"^\d{4,6}\s*", "", last).strip() or last


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def to_pipe_str(value: Any) -> str:
    if isinstance(value, list):
        return " | ".join(str(v) for v in value if str(v).strip())
    return str(value) if value is not None else ""
