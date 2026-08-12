#!/usr/bin/env python3
"""Build a reproducible KPM v3 package using only the Python standard library."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import tarfile
import tempfile
from pathlib import Path

from app_config import CONFIG_PATH, ROOT, ConfigError, load_config, verify_elf

TEMPLATE_DIR = ROOT / "package" / "kpm" / "templates"


def render(template: str, config: dict) -> bytes:
    replacements = {
        "@APP_ID@": config["id"],
        "@APP_NAME@": config["name"],
        "@APP_AUTHOR@": config["author"],
        "@BINARY_NAME@": config["binary_name"],
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    if re.search(r"@[A-Z_]+@", template):
        raise ConfigError("an unresolved template marker remains")
    return template.encode("utf-8")


def package_entries(config: dict, target: str, binary: Path) -> dict[str, tuple[bytes, int]]:
    manifest = {
        "manifest_version": 3,
        "id": config["id"],
        "name": config["name"],
        "author": config["author"],
        "description": config["description"],
        "version": config["version"],
        "dependencies": [],
        "supported_platforms": [target],
    }
    binary_name = config["binary_name"]
    entries: dict[str, tuple[bytes, int]] = {
        "manifest.json": ((json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode(), 0o644),
        f"bin/{binary_name}": (binary.read_bytes(), 0o755),
    }
    for output_name, template_name in (
        ("install.sh", "install.sh.in"),
        ("launch.sh", "launch.sh.in"),
        ("uninstall.sh", "uninstall.sh.in"),
        (f"scriptlets/{binary_name}.sh", "scriptlet.sh.in"),
    ):
        source = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        entries[output_name] = (render(source, config), 0o755)
    return entries


def write_package(output: Path, entries: dict[str, tuple[bytes, int]], epoch: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
        with gzip.GzipFile(fileobj=temporary, mode="wb", filename="", mtime=epoch) as gz_file:
            with tarfile.open(fileobj=gz_file, mode="w", format=tarfile.GNU_FORMAT) as archive:
                directories = sorted({name.rsplit("/", 1)[0] for name in entries if "/" in name})
                for directory in directories:
                    info = tarfile.TarInfo(directory + "/")
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    info.mtime = epoch
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    archive.addfile(info)
                for name in sorted(entries):
                    data, mode = entries[name]
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mode = mode
                    info.mtime = epoch
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    archive.addfile(info, io.BytesIO(data))
    temporary_path.replace(output)


def verify_package(output: Path, expected_names: set[str]) -> None:
    with tarfile.open(output, "r:gz") as archive:
        names = {member.name.rstrip("/") for member in archive if member.isfile()}
        if names != expected_names:
            raise ConfigError(f"archive contents differ: {sorted(names ^ expected_names)}")
        manifest_file = archive.extractfile("manifest.json")
        if manifest_file is None or json.load(manifest_file)["manifest_version"] != 3:
            raise ConfigError("archive manifest is missing or invalid")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("kindlehf", "kindlepw2"))
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)
    if args.target not in config["targets"]:
        raise ConfigError(f"target {args.target} is not enabled in app.json")
    binary = ROOT / "dist" / args.target / config["binary_name"]
    verify_elf(binary, args.target)

    epoch_text = os.environ.get("SOURCE_DATE_EPOCH", "0")
    try:
        epoch = int(epoch_text)
        if epoch < 0:
            raise ValueError
    except ValueError as exc:
        raise ConfigError("SOURCE_DATE_EPOCH must be a non-negative integer") from exc

    version = ".".join(str(part) for part in config["version"])
    output = ROOT / "dist" / "kpm" / f"{config['id']}_{version}_{args.target}.kpkg"
    entries = package_entries(config, args.target, binary)
    write_package(output, entries, epoch)
    verify_package(output, set(entries))

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="ascii")
    print(f"Package: {output}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ConfigError, OSError, tarfile.TarError) as exc:
        raise SystemExit(f"error: {exc}") from exc
