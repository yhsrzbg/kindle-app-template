# Kindle 原生应用开发模板

这是一个面向已越狱 Kindle 的 C++17/GTK+ 2.0 项目模板。它把 PC 本地 GUI
调试、Meson 交叉编译、KPM 可重复打包、配置校验和 CI 放在同一个项目中。

[PC 本地 GUI 调试](docs/PC_DEBUG_ZH.md) · [KPM 真机安装](package/README.md) ·
[KindleModding GTK 教程](https://kindlemodding.org/kindle-dev/gtk-tutorial/)

## 模板提供的能力

- `app.json` 是应用 ID、名称、版本和目标平台的唯一配置源；
- 同一份源码可编译 PC 调试版和 Kindle 发布版；
- 支持 `kindlehf`（hard-float）和 `kindlepw2`（soft-float）；
- 打包前自动校验 ARM ELF 架构和浮点 ABI；
- 不依赖外部 KPM 源码，使用 Python 标准库生成确定性 KPM v3 包；
- 书库 Scriptlet、重复启动保护、`/tmp/<app-id>.log` 日志和安全卸载；
- 单元测试、统一检查命令和 GitHub Actions。

## 1. 从模板创建自己的应用

克隆项目后运行：

```bash
./scripts/init-project.py \
  --id my_reader_tool \
  --name "My Reader Tool" \
  --binary-name my-reader-tool \
  --window-id org.example.my-reader-tool \
  --author "Your Name" \
  --description "My first Kindle application"
```

脚本只更新 `app.json`。Meson 生成的 C++ 头文件、可执行文件名、KPM manifest、
安装脚本和包文件名都会自动使用新配置，不需要全文替换项目。

注意：`window_id` 不能含下划线，因为 Kindle 的 awesome 窗口标题协议使用下划线
分隔字段；应用 `id` 建议使用小写字母、数字和下划线。

## 2. PC 本地构建并查看 GUI

Fedora：

```bash
sudo dnf install gcc-c++ gdb gtk2-devel meson ninja-build
./scripts/run-native.sh
```

Ubuntu/Debian：

```bash
sudo apt install g++ gdb libgtk2.0-dev meson ninja-build
./scripts/run-native.sh
```

`run-native.sh` 会构建 debug 版本并打开窗口。需要断点和调用栈时运行：

```bash
./scripts/debug-native.sh
```

详细说明见 [PC 本地 GUI 开发与调试](docs/PC_DEBUG_ZH.md)。PC 调试可以快速验证
界面和业务逻辑，但电子墨水刷新、触控、Kindle 窗口管理器及私有 API 仍需真机测试。

## 3. 安装交叉编译环境

项目提供引导脚本，默认使用固定版本的 KOReader 工具链和 Kindle SDK 提交：

```bash
./scripts/bootstrap-toolchain.sh kindlehf
```

该过程会下载 Kindle 固件，并使用 `sudo` 挂载固件 rootfs。成功后交叉配置位于：

```text
~/x-tools/arm-kindlehf-linux-gnueabihf/meson-crosscompile.txt
```

旧固件设备的平台若为 `kindlepw2`，则执行：

```bash
./scripts/bootstrap-toolchain.sh kindlepw2
```

工具链引导还需要 `curl`、`git`、`tar`、`zstd`、`make`、`pkg-config`，以及构建
KindleTool 所需的系统开发包。Fedora 可参考：

```bash
sudo dnf install gcc-c++ meson ninja-build gtk2-devel libstdc++-static \
  git curl zstd make pkgconf-pkg-config gperf help2man libarchive-devel nettle-devel ShellCheck
```

## 4. 编译 Kindle 发布版

```bash
./scripts/build.sh kindlehf release
```

结果位于：

```text
dist/kindlehf/kindle-hello-world
```

脚本会把 Meson 产物复制到统一的 `dist/<target>/` 目录、执行 strip，并检查它是
ARM32 hard-float ELF。调试交叉版本可使用：

```bash
./scripts/build.sh kindlehf debug
```

## 5. 生成并校验 KPM 包

```bash
./scripts/package.sh kindlehf
./scripts/check.sh kindlehf
```

默认示例会生成：

```text
dist/kpm/kindle_hello_world_1.0.0_kindlehf.kpkg
dist/kpm/kindle_hello_world_1.0.0_kindlehf.kpkg.sha256
```

`check.sh` 会执行配置测试、Shell 语法检查、Meson 测试、ELF/ABI 校验，并连续
打包两次确认 SHA-256 一致。需要让发布归档携带指定时间戳时，可设置标准变量：

```bash
SOURCE_DATE_EPOCH=1710000000 ./scripts/package.sh kindlehf
```

## 6. 安装到 Kindle

把 `.kpkg` 复制到 Kindle USB 存储根目录，然后在搜索框执行：

```text
;kpm -y install file:///mnt/us/kindle_hello_world_1.0.0_kindlehf.kpkg
```

可从书库点击应用，也可执行 `;kpm launch kindle_hello_world`。完整的平台确认、安装、
日志和卸载步骤见 [KPM 真机安装教程](package/README.md)。

## 常用命令

```bash
make run                         # PC GUI
make debug                       # PC GDB
make package TARGET=kindlehf     # 交叉编译并打包
make check TARGET=kindlehf       # 完整校验
```

## 目录结构

```text
.
├── app.json                 # 应用元数据的唯一配置源
├── meson.build              # PC/Kindle 共用构建定义
├── src/                     # C++/GTK 源码
├── scripts/                 # 初始化、构建、运行、调试、打包与检查
├── package/kpm/templates/   # KPM hooks 和书库 Scriptlet 模板
├── tests/                   # 工具测试
├── docs/                    # 开发文档
└── .github/workflows/       # PC 构建 CI
```

## 发布前检查清单

- 更新 `app.json` 中的版本；
- `./scripts/check.sh <target>` 全部通过；
- 在目标平台确认 `;kpm version`；
- 真机测试安装、首次启动、重复启动、退出、日志和卸载；
- 不把 `build/`、`dist/`、`tools/` 或 SDK/固件提交到 Git。

## 许可证

[MIT](LICENSE)
