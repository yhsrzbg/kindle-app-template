#!/bin/sh
set -eu

project_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
output_dir=${1:-"$project_dir/dist/previews"}
shift_if_output=$#
if [ "$shift_if_output" -gt 0 ]; then
  shift
fi

command -v xvfb-run >/dev/null 2>&1 || { echo "xvfb-run is required." >&2; exit 1; }
command -v import >/dev/null 2>&1 || { echo "ImageMagick import is required." >&2; exit 1; }

binary_name=$(python3 "$project_dir/scripts/app_config.py" get binary_name)
profile_tool="$project_dir/scripts/device_profiles.py"
"$project_dir/scripts/build.sh" native debug
mkdir -p "$output_dir"

if [ "$#" -eq 0 ]; then
  set -- legacy paperwhite-early paperwhite-hd paperwhite-large scribe
fi

for profile in "$@"; do
  resolution=$(python3 "$profile_tool" resolve "$profile")
  output="$output_dir/$profile.png"
  echo "Capturing $profile at $resolution"
  # Variables inside this script fragment intentionally expand in the child shell.
  # shellcheck disable=SC2016
  KINDLE_PREVIEW_SIZE="$resolution" xvfb-run -a -s "-screen 0 ${resolution}x24" \
    sh -c '
      "$1" >"$3" 2>&1 &
      app_pid=$!
      trap '\''kill "$app_pid" 2>/dev/null || true'\'' EXIT HUP INT TERM
      sleep 1
      import -window root "$2"
      kill "$app_pid" 2>/dev/null || true
      wait "$app_pid" 2>/dev/null || true
      trap - EXIT HUP INT TERM
    ' sh "$project_dir/dist/native/$binary_name" "$output" "$output.log"
done

echo "Preview screenshots: $output_dir"
