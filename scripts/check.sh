#!/bin/sh
set -eu

project_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
target=${1:-native}
binary_name=$(python3 "$project_dir/scripts/app_config.py" get binary_name)

python3 "$project_dir/scripts/app_config.py" validate
python3 -m unittest discover -s "$project_dir/tests" -v

for script in "$project_dir"/scripts/*.sh "$project_dir"/package/kpm/templates/*.sh.in; do
  sh -n "$script"
done
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck "$project_dir"/scripts/*.sh "$project_dir"/package/kpm/templates/*.sh.in
else
  echo "Note: shellcheck is not installed; syntax checks still ran."
fi

if [ -d "$project_dir/build/$target-debug" ]; then
  meson test -C "$project_dir/build/$target-debug" --print-errorlogs
elif [ -d "$project_dir/build/$target-release" ]; then
  meson test -C "$project_dir/build/$target-release" --print-errorlogs
fi

if [ "$target" != native ]; then
  binary="$project_dir/dist/$target/$binary_name"
  python3 "$project_dir/scripts/app_config.py" verify-elf "$binary" "$target"
  "$project_dir/scripts/package.sh" "$target"
  package_name=$(python3 "$project_dir/scripts/app_config.py" get id)_$(python3 "$project_dir/scripts/app_config.py" get version_string)_$target.kpkg
  first_hash=$(sha256sum "$project_dir/dist/kpm/$package_name" | awk '{print $1}')
  "$project_dir/scripts/package.sh" "$target" >/dev/null
  second_hash=$(sha256sum "$project_dir/dist/kpm/$package_name" | awk '{print $1}')
  test "$first_hash" = "$second_hash"
  echo "Reproducible package: $first_hash"
fi

echo "All checks passed for $target."
