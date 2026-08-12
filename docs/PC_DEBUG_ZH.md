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

在 GNOME、KDE 等图形桌面的终端中执行：

```bash
./scripts/run-native.sh
```

脚本会生成调试版本并启动 `dist/native/` 中的程序。也可以分开执行：

```bash
./scripts/build.sh native debug
./dist/native/kindle-hello-world
```

如果修改了 `app.json` 中的 `binary_name`，第一种方式无需同步修改命令。

## 使用 GDB

```bash
./scripts/debug-native.sh
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

没有 `DISPLAY`/`WAYLAND_DISPLAY` 时不能直接查看窗口。自动化测试可使用 Xvfb：

```bash
sudo dnf install xorg-x11-server-Xvfb   # Fedora
Xvfb :99 -screen 0 800x1200x24 &
DISPLAY=:99 ./dist/native/kindle-hello-world
```

Xvfb 只能验证程序能够创建窗口，无法代替人工查看 GUI。

## PC 与 Kindle 的差异

- PC 的窗口尺寸、DPI、字体和主题与 Kindle 不同；避免依赖像素级布局。
- Kindle 是灰阶电子墨水屏，优先使用高对比度、大点击区域和少动画界面。
- PC 上没有 LIPC、Pillow/awesome 窗口管理器等 Kindle 服务，相关逻辑应封装并
  提供 PC fallback。
- 发布前至少在目标平台执行一次安装、启动、重复启动和卸载测试。
