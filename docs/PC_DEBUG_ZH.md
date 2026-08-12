# PC 本地 GUI 开发与调试

Kindle 端仍使用 GTK+ 2.0，因此模板在 Linux PC 上使用同一套源码和 GTK API
进行快速调试。PC 构建用于验证界面与业务逻辑；最终仍要交叉编译并在真机上验证
电子墨水刷新、触控、窗口管理器和 Kindle 私有 API。

## 安装依赖

Fedora：

```bash
sudo dnf install gcc-c++ gdb gtk2-devel meson ninja-build
```

Ubuntu/Debian：

```bash
sudo apt install g++ gdb libgtk2.0-dev meson ninja-build
```

## 构建并查看 GUI

在 GNOME、KDE 等图形桌面的终端中执行。默认预览 `paperwhite-hd` 的
`1072×1448` 客户区：

```bash
./scripts/run-native.sh
```

查看内置设备预设：

```bash
./scripts/run-native.sh --list-devices
```

当前预设包括：

| 名称 | 分辨率 | 用途 |
|---|---:|---|
| `legacy` | 600×800 | 老款 6 英寸 Kindle |
| `paperwhite-early` | 758×1024 | 早期 Paperwhite |
| `paperwhite-hd` | 1072×1448 | 6 英寸 300 PPI 级设备 |
| `paperwhite-large` | 1264×1680 | 大屏 Paperwhite/Oasis 级设备 |
| `scribe` | 1860×2480 | Scribe 级设备 |

指定预设或任意 `320～4096` 像素范围内的尺寸：

```bash
./scripts/run-native.sh --device paperwhite-early
./scripts/run-native.sh --resolution 900x1200
./scripts/run-native.sh --fullscreen
```

分辨率预设只用于 PC 调试，不会编译进 Kindle 发布程序。没有预览变量时，程序仍由
Kindle 窗口管理器最大化到设备的实际可用区域。KPM 的 `kindlehf`/`kindlepw2`
平台代表 ABI，不代表某个固定分辨率。

脚本会生成调试版本并启动 `dist/native/` 中的程序。也可以分开执行：

```bash
./scripts/build.sh native debug
./dist/native/kindle-hello-world
```

如果修改了 `app.json` 中的 `binary_name`，第一种方式无需同步修改命令。

## 使用 GDB

```bash
./scripts/debug-native.sh --device paperwhite-hd
```

常用命令：

```text
break main
run
bt
continue
```

程序崩溃时执行 `bt` 查看调用栈。编译目录位于 `build/native-debug/`，其中保留
调试符号。

## 手动配置与测试

```bash
meson setup --buildtype=debug build/native-debug
meson compile -C build/native-debug
meson test -C build/native-debug --print-errorlogs
```

已经存在的构建目录可使用：

```bash
meson setup --reconfigure --buildtype=debug build/native-debug
```

## 无桌面或远程环境

没有 `DISPLAY`/`WAYLAND_DISPLAY` 时不能直接查看窗口。安装 Xvfb 和 ImageMagick 后，
可以批量生成所有预设分辨率的截图：

```bash
sudo dnf install xorg-x11-server-Xvfb ImageMagick   # Fedora
./scripts/capture-previews.sh
```

结果位于 `dist/previews/`。也可以只生成部分预设：

```bash
./scripts/capture-previews.sh dist/previews legacy paperwhite-hd
```

GitHub Actions 会自动生成 `legacy` 和 `paperwhite-hd` 截图并上传为
`kindle-gui-previews` artifact。Xvfb 截图可以发现裁切和溢出，但无法代替人工查看
GUI 和真机测试。

## PC 与 Kindle 的差异

- 分辨率相同也不代表 DPI、字体和物理触控尺寸相同；避免依赖像素级布局。
- Kindle 是灰阶电子墨水屏，优先使用高对比度、大点击区域和少动画界面。
- PC 上没有 LIPC、Pillow/awesome 窗口管理器等 Kindle 服务，相关逻辑应封装并
  提供 PC fallback。
- 发布前至少在目标平台执行一次安装、启动、重复启动和卸载测试。
