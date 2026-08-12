#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=${1:-kindlehf}
toolchain_release=2026.08
sdk_commit=b4a6c99d718a7cf74935f36105c62491b4336a61

case "$target" in
  kindlehf) tuple=arm-kindlehf-linux-gnueabihf ;;
  kindlepw2) tuple=arm-kindlepw2-linux-gnueabi ;;
  *) echo "Usage: $0 [kindlehf|kindlepw2]" >&2; exit 2 ;;
esac

for command in curl git tar zstd make meson pkg-config; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Missing command: $command" >&2
    exit 1
  }
done

toolchain_dir="$HOME/x-tools/$tuple"
if [ ! -x "$toolchain_dir/bin/$tuple-g++" ]; then
  archive=$(mktemp --suffix=.tar.zst)
  trap 'rm -f "$archive"' EXIT HUP INT TERM
  url="https://github.com/koreader/koxtoolchain/releases/download/$toolchain_release/$target.tar.zst"
  echo "Downloading $url"
  curl --fail --location --retry 3 --output "$archive" "$url"
  tar --zstd -xf "$archive" -C "$HOME"
fi

sdk_dir="$project_dir/tools/kindle-sdk"
if [ ! -d "$sdk_dir/.git" ]; then
  mkdir -p "$project_dir/tools"
  git clone https://github.com/KindleModding/Kindle-SDK.git "$sdk_dir"
fi
git -C "$sdk_dir" fetch --depth=1 origin "$sdk_commit"
git -C "$sdk_dir" checkout --detach "$sdk_commit"

echo "The SDK step downloads Kindle firmware and uses sudo for loop mounting."
"$sdk_dir/gen-sdk.sh" "$target" "$toolchain_dir"
test -f "$toolchain_dir/meson-crosscompile.txt"
echo "Ready: $toolchain_dir/meson-crosscompile.txt"
