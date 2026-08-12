#!/bin/sh
set -eu

project_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
target=${1:-kindlehf}
build_type=${2:-release}

case "$build_type" in
  debug|release) ;;
  *) echo "Usage: $0 [native|kindlehf|kindlepw2] [debug|release]" >&2; exit 2 ;;
esac

binary_name=$(python3 "$project_dir/scripts/app_config.py" get binary_name)
build_dir="$project_dir/build/$target-$build_type"
dist_dir="$project_dir/dist/$target"
strip_tool=

case "$target" in
  native)
    ;;
  kindlehf)
    tuple=arm-kindlehf-linux-gnueabihf
    cross_file=${KINDLE_CROSS_FILE:-"$HOME/x-tools/$tuple/meson-crosscompile.txt"}
    strip_tool="$HOME/x-tools/$tuple/bin/$tuple-strip"
    ;;
  kindlepw2)
    tuple=arm-kindlepw2-linux-gnueabi
    cross_file=${KINDLE_CROSS_FILE:-"$HOME/x-tools/$tuple/meson-crosscompile.txt"}
    strip_tool="$HOME/x-tools/$tuple/bin/$tuple-strip"
    ;;
  *) echo "Usage: $0 [native|kindlehf|kindlepw2] [debug|release]" >&2; exit 2 ;;
esac

if [ "$target" != native ] && [ ! -f "$cross_file" ]; then
  echo "Cross file not found: $cross_file" >&2
  echo "Run ./scripts/bootstrap-toolchain.sh $target first." >&2
  exit 1
fi

if [ "$target" = native ]; then
  if [ -d "$build_dir" ]; then
    meson setup --reconfigure --buildtype="$build_type" "$build_dir" "$project_dir"
  else
    meson setup --buildtype="$build_type" "$build_dir" "$project_dir"
  fi
else
  if [ -d "$build_dir" ]; then
    meson setup --reconfigure --buildtype="$build_type" --cross-file "$cross_file" "$build_dir" "$project_dir"
  else
    meson setup --buildtype="$build_type" --cross-file "$cross_file" "$build_dir" "$project_dir"
  fi
fi
meson compile -C "$build_dir"

mkdir -p "$dist_dir"
install -m 755 "$build_dir/$binary_name" "$dist_dir/$binary_name"
if [ "$build_type" = release ] && [ -n "$strip_tool" ]; then
  "$strip_tool" "$dist_dir/$binary_name"
fi
if [ "$target" != native ]; then
  python3 "$project_dir/scripts/app_config.py" verify-elf "$dist_dir/$binary_name" "$target"
fi

file "$dist_dir/$binary_name"
echo "Built: $dist_dir/$binary_name"
