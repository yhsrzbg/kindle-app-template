# 使用 KPM 安装到 Kindle

以下命令以模板默认配置为例。修改 `app.json` 后，包名和应用 ID 会随之改变。

## 1. 确认设备平台

Kindle 必须已越狱并安装 KPM。在首页搜索框输入：

```text
;kpm version
```

记录输出中的平台：

- `kindlehf`：通常是运行较新固件的支持机型，使用 hard-float 包；
- `kindlepw2`：较旧固件平台，必须单独构建 soft-float 包。

平台必须与 `.kpkg` 文件名末尾一致，不要跨平台强制安装。

## 2. 构建安装包

```bash
./scripts/build.sh kindlehf release
./scripts/package.sh kindlehf
./scripts/check.sh kindlehf
```

输出示例：

```text
dist/kpm/kindle_hello_world_1.0.0_kindlehf.kpkg
```

## 3. USB 复制并安装

把 `.kpkg` 复制到 Kindle USB 存储盘根目录，安全弹出并断开 USB。在 Kindle 搜索框
输入（`file:///` 后有三个斜杠）：

```text
;kpm -y install file:///mnt/us/kindle_hello_world_1.0.0_kindlehf.kpkg
```

安装脚本会在 `/mnt/us/documents/` 创建一个书库 Scriptlet。如果同名文件已经存在
且内容不同，安装会停止，避免覆盖用户文件。

## 4. 启动

从书库点击 `Kindle Hello World`，或在搜索框输入：

```text
;kpm launch kindle_hello_world
```

启动脚本会阻止重复实例。运行日志位于：

```text
/tmp/kindle_hello_world.log
```

可通过 SSH、KTerm 或其他终端查看：

```sh
tail -n 100 /tmp/kindle_hello_world.log
```

## 5. 卸载

```text
;kpm -y uninstall kindle_hello_world
```

只有内容仍与本包一致时，卸载脚本才会删除书库 Scriptlet。USB 根目录中的 `.kpkg`
可在卸载后手动删除。

## 常见问题

- `Package does not support platform ...`：包目标与 `;kpm version` 不一致。
- 找不到包：确认它位于 `/mnt/us/`，没有额外的 `.zip` 后缀，也没有被自动重命名。
- 书库项目未出现：刷新首页或重启 Kindle 一次。
- 无法启动：先检查 `/tmp/<app-id>.log`，再确认二进制 ABI 与设备平台一致。
