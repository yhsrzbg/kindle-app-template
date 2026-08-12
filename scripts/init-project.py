#!/usr/bin/env python3
"""Customize app.json for a new project without touching build scripts."""

from __future__ import annotations

import argparse
import json
import os
import tempfile

from app_config import CONFIG_PATH, ConfigError, load_config, validate_config


def parse_version(value: str) -> list[int]:
    try:
        parts = [int(part) for part in value.split(".")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use MAJOR.MINOR.PATCH") from exc
    if len(parts) != 3 or any(part < 0 for part in parts):
        raise argparse.ArgumentTypeError("use MAJOR.MINOR.PATCH")
    return parts


def main() -> int:
    current = load_config()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", default=current["id"])
    parser.add_argument("--name", default=current["name"])
    parser.add_argument("--binary-name", default=current["binary_name"])
    parser.add_argument("--window-id", default=current["window_id"])
    parser.add_argument("--version", type=parse_version, default=current["version"])
    parser.add_argument("--author", default=current["author"])
    parser.add_argument("--description", default=current["description"])
    parser.add_argument(
        "--targets", nargs="+", choices=("kindlehf", "kindlepw2"),
        default=current["targets"],
    )
    args = parser.parse_args()
    updated = {
        "id": args.id,
        "name": args.name,
        "binary_name": args.binary_name,
        "window_id": args.window_id,
        "version": args.version,
        "author": args.author,
        "description": args.description,
        "targets": args.targets,
    }
    validate_config(updated)

    payload = json.dumps(updated, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=CONFIG_PATH.parent, delete=False
    ) as temporary:
        temporary.write(payload)
        temp_name = temporary.name
    os.replace(temp_name, CONFIG_PATH)
    print(f"Updated {CONFIG_PATH}")
    print("Next: ./scripts/build.sh native debug")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigError as exc:
        raise SystemExit(f"error: {exc}") from exc
