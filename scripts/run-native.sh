#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
binary_name=$(python3 "$project_dir/scripts/app_config.py" get binary_name)

if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo "No graphical session detected (DISPLAY and WAYLAND_DISPLAY are empty)." >&2
  exit 1
fi

"$project_dir/scripts/build.sh" native debug
export G_DEBUG=${G_DEBUG:-fatal-warnings}
exec "$project_dir/dist/native/$binary_name" "$@"
