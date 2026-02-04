from __future__ import annotations

import argparse
from pathlib import Path

from src.features import FeatureConfig, build_features
from src.ingest import ingest
from src.post import post_once


DEFAULT_RAW = Path("data/raw/2_NZES23Release_100227.dta")
FALLBACK_RAW = Path("doi-10.26193-hhmeuz/2_NZES23Release_100227.dta")
DEFAULT_PROCESSED = Path("data/processed/nzes2023.parquet")
DEFAULT_LABELS = Path("data/processed/labels.json")
DEFAULT_STATE = Path("state/state.json")


def resolve_raw_path(path: Path | None) -> Path:
    if path and path.exists():
        return path
    if DEFAULT_RAW.exists():
        return DEFAULT_RAW
    if FALLBACK_RAW.exists():
        return FALLBACK_RAW
    raise FileNotFoundError("Could not find NZES .dta file. Place it in data/raw.")


def cmd_build_dataset(args: argparse.Namespace) -> None:
    raw_path = resolve_raw_path(Path(args.raw) if args.raw else None)
    labels_path = Path(args.labels) if args.labels else DEFAULT_LABELS
    processed_path = Path(args.processed) if args.processed else DEFAULT_PROCESSED

    df, labels = ingest(raw_path, labels_path)
    features = build_features(df, labels, FeatureConfig(min_cell=args.min_cell))

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(processed_path, index=False)

    print(f"Wrote {processed_path}")


def cmd_post_once(args: argparse.Namespace) -> None:
    dataset_path = Path(args.dataset) if args.dataset else DEFAULT_PROCESSED
    state_path = Path(args.state) if args.state else DEFAULT_STATE

    handle = args.handle
    app_password = args.app_password

    post_once(
        dataset_path=dataset_path,
        state_path=state_path,
        handle=handle,
        app_password=app_password,
        dry_run=args.dry_run,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NZES Bluesky voter bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-dataset", help="Build processed dataset")
    build_parser.add_argument("--raw", help="Path to .dta file")
    build_parser.add_argument("--processed", help="Output parquet path")
    build_parser.add_argument("--labels", help="Output labels JSON path")
    build_parser.add_argument("--min-cell", type=int, default=10, help="Minimum cell size")
    build_parser.set_defaults(func=cmd_build_dataset)

    post_parser = subparsers.add_parser("post-once", help="Post one profile to Bluesky")
    post_parser.add_argument("--dataset", help="Processed parquet path")
    post_parser.add_argument("--state", help="State JSON path")
    post_parser.add_argument("--handle", help="Bluesky handle")
    post_parser.add_argument("--app-password", help="Bluesky app password")
    post_parser.add_argument("--dry-run", action="store_true", help="Print without posting")
    post_parser.set_defaults(func=cmd_post_once)

    dry_parser = subparsers.add_parser("dry-run", help="Generate a post without posting")
    dry_parser.add_argument("--dataset", help="Processed parquet path")
    dry_parser.add_argument("--state", help="State JSON path")
    dry_parser.set_defaults(func=lambda args: cmd_post_once(argparse.Namespace(**{
        "dataset": args.dataset,
        "state": args.state,
        "handle": None,
        "app_password": None,
        "dry_run": True,
    })))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
