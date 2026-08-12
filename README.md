# Kindle Native App Template

A reusable C++17/GTK+ 2.0 template for native applications on jailbroken
Kindles. It provides native Linux GUI debugging, Meson cross-compilation,
reproducible KPM packages, metadata validation, and CI.

[中文文档](README_zh.md) · [PC GUI debugging (中文)](docs/PC_DEBUG_ZH.md) ·
[KPM installation](package/README.md)

## Features

- One metadata file: `app.json`
- Native debug and Kindle release builds through the same Meson project
- `kindlehf` (hard-float) and `kindlepw2` (soft-float) targets
- Self-contained, deterministic KPM v3 packaging
- ARM/ABI validation before packaging
- Safe library Scriptlet install/uninstall and duplicate-launch protection
- Unit tests and a GitHub Actions native-build smoke test

## Quick start

Install native dependencies on Fedora:

```sh
sudo dnf install gcc-c++ gdb gtk2-devel meson ninja-build
```

Customize the template:

```sh
./scripts/init-project.py \
  --id my_reader_tool \
  --name "My Reader Tool" \
  --binary-name my-reader-tool \
  --window-id org.example.my-reader-tool \
  --author "Your Name"
```

Build and open the GUI using the default `paperwhite-hd` preview:

```sh
./scripts/run-native.sh
```

Select a device profile or an exact custom framebuffer size:

```sh
./scripts/run-native.sh --list-devices
./scripts/run-native.sh --device paperwhite-early
./scripts/run-native.sh --resolution 900x1200
```

For source-level debugging:

```sh
./scripts/debug-native.sh
```

Generate screenshots for every built-in Kindle resolution with Xvfb and
ImageMagick:

```sh
make previews
```

## Kindle build and package

Install the cross-toolchain/SDK once (this downloads firmware and asks for sudo
to mount its root filesystem):

```sh
./scripts/bootstrap-toolchain.sh kindlehf
```

Then build and package:

```sh
./scripts/build.sh kindlehf release
./scripts/package.sh kindlehf
./scripts/check.sh kindlehf
```

Outputs are written to `dist/kindlehf/` and `dist/kpm/`. Use `kindlepw2` in the
same commands for older, soft-float firmware after installing that SDK target.

You can also use Make:

```sh
make run
make package TARGET=kindlehf
make check TARGET=kindlehf
```

## Project layout

```text
app.json                 application identity, version, and targets
src/                     C++/GTK source
scripts/build.sh         native and cross-build entry point
scripts/package.sh       reproducible KPM package entry point
scripts/init-project.py  template customization
package/kpm/templates/   generated KPM hooks and library Scriptlet
tests/                   metadata and tooling tests
docs/                    development guides
```

The generated C++ header and KPM manifest both come from `app.json`; do not
duplicate metadata elsewhere. See the
[KindleModding GTK tutorial](https://kindlemodding.org/kindle-dev/gtk-tutorial/)
for platform background.

## License

[MIT](LICENSE)
