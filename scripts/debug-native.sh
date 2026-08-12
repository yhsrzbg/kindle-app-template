#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
binary_name=$(python3 "$project_dir/scripts/app_config.py" get binary_name)

command -v gdb >/dev/null 2>&1 || {
  echo "gdb is required for native debugging." >&2
  exit 1
}
"$project_dir/scripts/build.sh" native debug
exec gdb --args "$project_dir/dist/native/$binary_name" "$@"
