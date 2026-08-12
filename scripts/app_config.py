#!/usr/bin/env python3
"""Read and validate app.json, the single source of project metadata."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "app.json"
SUPPORTED_TARGETS = {"kindlehf", "kindlepw2"}


class ConfigError(ValueError):
    pass


def load_config(path: Path = CONFIG_PATH) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    validate_config(data)
    return data


def _plain_string(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string")
    if any(ord(char) < 32 for char in value):
        raise ConfigError(f"{key} must not contain control characters")
    return value


def validate_config(data: dict) -> None:
    expected = {
        "id", "name", "binary_name", "window_id", "version", "author",
        "description", "targets",
    }
    missing = expected - data.keys()
    unknown = data.keys() - expected
    if missing:
        raise ConfigError(f"missing keys: {', '.join(sorted(missing))}")
    if unknown:
        raise ConfigError(f"unknown keys: {', '.join(sorted(unknown))}")

    app_id = _plain_string(data, "id")
    binary_name = _plain_string(data, "binary_name")
    window_id = _plain_string(data, "window_id")
    for key in ("name", "author", "description"):
        _plain_string(data, key)

    if not re.fullmatch(r"[a-z][a-z0-9_-]*", app_id):
        raise ConfigError("id must start with a lowercase letter and use a-z, 0-9, _ or -")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", binary_name):
        raise ConfigError("binary_name must be safe as a Unix filename")
    if not re.fullmatch(r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)+", window_id):
        raise ConfigError("window_id must be a dotted identifier without underscores")

    version = data.get("version")
    if (not isinstance(version, list) or len(version) != 3 or
            any(type(part) is not int or part < 0 for part in version)):
        raise ConfigError("version must contain exactly three non-negative integers")

    targets = data.get("targets")
    if (not isinstance(targets, list) or not targets or
            any(not isinstance(target, str) for target in targets)):
        raise ConfigError("targets must be a non-empty list of strings")
    if len(set(targets)) != len(targets):
        raise ConfigError("targets must be a non-empty list without duplicates")
    unsupported = set(targets) - SUPPORTED_TARGETS
    if unsupported:
        raise ConfigError(f"unsupported targets: {', '.join(sorted(unsupported))}")


def get_value(data: dict, key: str) -> str:
    if key == "version_string":
        return ".".join(str(part) for part in data["version"])
    if key not in data:
        raise ConfigError(f"unknown key: {key}")
    value = data[key]
    return json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)


def verify_elf(path: Path, target: str) -> None:
    if target not in SUPPORTED_TARGETS:
        raise ConfigError(f"unsupported target: {target}")
    try:
        header = path.read_bytes()[:52]
    except OSError as exc:
        raise ConfigError(f"cannot read binary {path}: {exc}") from exc
    if len(header) < 52 or header[:4] != b"\x7fELF":
        raise ConfigError(f"{path} is not an ELF binary")
    if header[4] != 1 or header[5] != 1:
        raise ConfigError(f"{path} must be a 32-bit little-endian ELF binary")
    if struct.unpack_from("<H", header, 18)[0] != 40:
        raise ConfigError(f"{path} is not an ARM binary")
    flags = struct.unpack_from("<I", header, 36)[0]
    hard_float = bool(flags & 0x400)
    if target == "kindlehf" and not hard_float:
        raise ConfigError(f"{path} is not built for the hard-float ABI")
    if target == "kindlepw2" and hard_float:
        raise ConfigError(f"{path} is not built for the soft-float ABI")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("key")
    verify_parser = subparsers.add_parser("verify-elf")
    verify_parser.add_argument("path", type=Path)
    verify_parser.add_argument("target", choices=sorted(SUPPORTED_TARGETS))
    args = parser.parse_args(argv)

    try:
        data = load_config()
        if args.command == "get":
            print(get_value(data, args.key))
        elif args.command == "verify-elf":
            verify_elf(args.path, args.target)
        else:
            print(f"OK: {CONFIG_PATH}")
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
