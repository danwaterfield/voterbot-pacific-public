from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import pyreadstat


def clean_label(label: str | None) -> str | None:
    if not label:
        return None
    # Remove leading numeric prefixes like "1. "
    cleaned = label.strip()
    parts = cleaned.split(".", 1)
    if len(parts) == 2 and parts[0].strip().isdigit():
        cleaned = parts[1].strip()
    return cleaned


def read_raw_dta(path: Path) -> Tuple[Any, Dict[str, Any]]:
    df, meta = pyreadstat.read_dta(path, apply_value_formats=False)
    labels = {
        "variables": {
            name: clean_label(label)
            for name, label in zip(meta.column_names, meta.column_labels)
        },
        "values": {},
    }
    for var, label_map in meta.variable_value_labels.items():
        if isinstance(label_map, dict):
            labels["values"][var] = {int(k) if isinstance(k, float) and k.is_integer() else k: clean_label(v) for k, v in label_map.items()}
    return df, labels


def write_labels(labels: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2, ensure_ascii=False)


def ingest(raw_path: Path, labels_path: Path) -> Tuple[Any, Dict[str, Any]]:
    df, labels = read_raw_dta(raw_path)
    write_labels(labels, labels_path)
    return df, labels
