from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_STATE = {
    "used_ids": [],
    "queue": [],
    "queue_index": 0,
    "rng_seed": 1337,
    "last_post": None,
}


def load_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return DEFAULT_STATE.copy()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    merged = DEFAULT_STATE.copy()
    merged.update(data)
    return merged


def save_state(path: Path, state: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
