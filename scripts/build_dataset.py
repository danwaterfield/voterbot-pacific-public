#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.cli import cmd_build_dataset
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw")
    parser.add_argument("--processed")
    parser.add_argument("--labels")
    parser.add_argument("--min-cell", type=int, default=10)
    args = parser.parse_args()
    cmd_build_dataset(args)


if __name__ == "__main__":
    main()
