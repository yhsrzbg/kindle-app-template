#!/bin/sh
set -eu

project_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
binary_name=$(python3 "$project_dir/scripts/app_config.py" get binary_name)
profile_tool="$project_dir/scripts/device_profiles.py"
preview=${KINDLE_PREVIEW_DEVICE:-paperwhite-hd}
fullscreen=false
debug=false

usage() {
  cat <<'EOF'
Usage: run-native.sh [options] [-- application-arguments]

Options:
  --device NAME       Preview a built-in Kindle device profile
  --resolution WxH    Preview an arbitrary framebuffer resolution
  --fullscreen        Use the current PC display instead of a device size
  --debug             Start the preview inside GDB
  --list-devices      List built-in profiles
  -h, --help          Show this help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --device|--resolution)
      [ "$#" -ge 2 ] || { echo "$1 requires a value" >&2; exit 2; }
      preview=$2
      shift 2
      ;;
    --fullscreen) fullscreen=true; shift ;;
    --debug) debug=true; shift ;;
    --list-devices) python3 "$profile_tool" list; exit 0 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo "No graphical session detected (DISPLAY and WAYLAND_DISPLAY are empty)." >&2
  exit 1
fi

if [ "$fullscreen" = true ]; then
  unset KINDLE_PREVIEW_SIZE
  export KINDLE_PREVIEW_FULLSCREEN=1
else
  KINDLE_PREVIEW_SIZE=$(python3 "$profile_tool" resolve "$preview")
  export KINDLE_PREVIEW_SIZE
  unset KINDLE_PREVIEW_FULLSCREEN
  echo "Previewing $KINDLE_PREVIEW_SIZE ($preview)"
fi

"$project_dir/scripts/build.sh" native debug
export G_DEBUG="${G_DEBUG:-fatal-warnings}"
if [ "$debug" = true ]; then
  command -v gdb >/dev/null 2>&1 || { echo "gdb is required." >&2; exit 1; }
  exec gdb --args "$project_dir/dist/native/$binary_name" "$@"
fi
exec "$project_dir/dist/native/$binary_name" "$@"
