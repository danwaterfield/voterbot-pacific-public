from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.bsky_client import BlueskyClient
from src.state import load_state, save_state
from src.templates import TemplateContext, context_from_row, render_profile

MIN_FIELDS = 3


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if "respondent_id" in df.columns:
        df["respondent_id"] = df["respondent_id"].astype(str)
    return df


def build_queue(ids: pd.Series, seed: int) -> list[str]:
    rng = random.Random(seed)
    queue = [str(value) for value in ids.dropna().unique().tolist()]
    rng.shuffle(queue)
    return queue


def row_field_count(row: pd.Series) -> int:
    fields = [
        "age_bucket",
        "gender",
        "ethnicity",
        "education",
        "housing",
        "urban_rural",
        "party_vote",
        "ideology",
    ]
    count = 0
    for field in fields:
        value = row.get(field)
        if value is None or value == "":
            continue
        if pd.isna(value):
            continue
        count += 1
    return count


def select_candidate(df: pd.DataFrame, state: Dict[str, Any]) -> Dict[str, Any]:
    if not state.get("queue"):
        state["queue"] = build_queue(df["respondent_id"], state.get("rng_seed", 1337))
        state["queue_index"] = 0

    used_ids = set(str(value) for value in state.get("used_ids", []))
    df_indexed = df.set_index("respondent_id", drop=False)

    while state["queue_index"] < len(state["queue"]):
        respondent_id = str(state["queue"][state["queue_index"]])
        state["queue_index"] += 1
        if respondent_id in used_ids:
            continue
        if respondent_id not in df_indexed.index:
            continue
        row = df_indexed.loc[respondent_id]
        if row_field_count(row) < MIN_FIELDS:
            continue
        return row.to_dict()

    raise RuntimeError("No remaining candidates with sufficient fields.")


def post_once(
    dataset_path: Path,
    state_path: Path,
    handle: Optional[str] = None,
    app_password: Optional[str] = None,
    dry_run: bool = False,
) -> str:
    df = load_dataset(dataset_path)
    state = load_state(state_path)

    row = select_candidate(df, state)
    context = context_from_row(row)
    text = render_profile(context)

    if dry_run:
        print(text)
        return text

    if not handle or not app_password:
        raise RuntimeError("Missing Bluesky credentials.")

    client = BlueskyClient(handle, app_password)
    uri = client.post(text)

    state.setdefault("used_ids", []).append(str(row["respondent_id"]))
    state["last_post"] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uri": uri,
        "text": text,
    }
    save_state(state_path, state)

    return uri
