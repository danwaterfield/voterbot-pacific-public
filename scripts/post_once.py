#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.post import post_once


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset")
    parser.add_argument("--state")
    parser.add_argument("--handle", default=os.getenv("BSKY_HANDLE"))
    parser.add_argument("--app-password", default=os.getenv("BSKY_APP_PASSWORD"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    dataset_path = Path(args.dataset) if args.dataset else Path("data/processed/nzes2023.parquet")
    state_path = Path(args.state) if args.state else Path("state/state.json")

    post_once(
        dataset_path=dataset_path,
        state_path=state_path,
        handle=args.handle,
        app_password=args.app_password,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
