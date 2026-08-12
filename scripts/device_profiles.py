#!/usr/bin/env python3
"""Resolve Kindle preview profiles to framebuffer-sized WIDTHxHEIGHT values."""

from __future__ import annotations

import argparse
import re

PROFILES = {
    "legacy": (600, 800, "Legacy 6-inch Kindle"),
    "paperwhite-early": (758, 1024, "Early Kindle Paperwhite"),
    "paperwhite-hd": (1072, 1448, "6-inch 300 PPI Kindle"),
    "paperwhite-large": (1264, 1680, "Large Paperwhite/Oasis class"),
    "scribe": (1860, 2480, "Kindle Scribe class"),
}


def resolve(value: str) -> tuple[int, int]:
    if value in PROFILES:
        return PROFILES[value][0:2]
    match = re.fullmatch(r"([1-9][0-9]{2,3})x([1-9][0-9]{2,3})", value)
    if match is None:
        raise ValueError(f"unknown device or invalid resolution: {value}")
    width, height = (int(part) for part in match.groups())
    if not (320 <= width <= 4096 and 320 <= height <= 4096):
        raise ValueError("preview dimensions must each be between 320 and 4096 pixels")
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("value")
    args = parser.parse_args()

    if args.command == "list":
        for name, (width, height, description) in PROFILES.items():
            print(f"{name:18} {width}x{height:<9} {description}")
        return 0
    try:
        width, height = resolve(args.value)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"{width}x{height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
