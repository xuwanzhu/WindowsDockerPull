# DockerPullAuto

DockerPullAuto.exe 一个是用于在Windows环境下没安装Docker也能拉取Docker镜像的软件。

DockerPullAuto 是对原始 `DockerPull.exe` 的轻量增强版。

它只新增一个能力：可以先输入 `docker login` 命令记录镜像仓库账号密码。除此之外，镜像拉取、架构选择、debug、quiet 等命令参数都保持和原始 `DockerPull.exe` 一样。

本项目采用的原始 `DockerPull.exe` 为官方版本 `v1.2.0`。

## 文件说明

- `DockerPull.exe`: 原始镜像下载工具，必须保留。
- `DockerPullAuto.exe`: 已打包好的增强版程序，日常直接运行这个文件。
- `docker_pull_auto.py`: DockerPullAuto 的 Python 源码，后续修改功能时编辑这个文件。
- `docker_pull_auto.spec`: PyInstaller 打包配置，负责把 `docker_pull_auto.py` 和 `DockerPull.exe` 打包成新的 `DockerPullAuto.exe`。
- `README.md`: 本说明文档。

## 使用方法

双击或在控制台运行：

```powershell
.\DockerPullAuto.exe
```

先输入登录命令：

```powershell
docker login registry.example.com -u username -p password
```

登录后，按原始 `DockerPull.exe` 的参数方式拉取镜像：

```powershell
-i registry.example.com/namespace/image:tag
```

指定架构：

```powershell
-i registry.example.com/namespace/image:tag -a arm64v8
```

开启 debug：

```powershell
-i registry.example.com/namespace/image:tag --debug
```

也可以把程序名一起输入，DockerPullAuto 会自动去掉程序名再调用原始工具：

```powershell
DockerPull.exe -i registry.example.com/namespace/image:tag -a amd64
```

如果你在拉取命令里手动指定了 `-r`、`-u` 或 `-p`，DockerPullAuto 不会覆盖它们：

```powershell
-i nginx:latest -r registry.example.com -u other_user -p other_password
```

更多示例：

```powershell
# 下载 Docker Hub 镜像
-i nginx:latest

# 下载指定架构镜像
-i alpine:latest -a arm64

# 下载私有仓库镜像
-i harbor.example.com/library/nginx:1.26.0 -u admin -p password

# 指定输出目录
-i nginx:latest -o ./downloads

# 静默模式下载
-i nginx:latest -q

# 下载 Quay.io 多架构镜像
-i quay.io/ascend/vllm-ascend:v0.11.0-a3-openeuler -a arm64
```

输入下面任意一个命令退出：

```powershell
q
quit
exit
```

## 原始 DockerPull.exe 参数

当前 `DockerPull.exe --help` 显示支持：

```text
-i, --image             Docker 镜像名称
-q, --quiet             静默模式，减少交互
-r, --custom_registry   自定义仓库地址
-a, --arch              架构，默认 amd64，常见 amd64、arm64v8
-u, --username          Docker 仓库用户名
-p, --password          Docker 仓库密码
-v, --version           显示版本信息
--debug                 启用调试模式
```

DockerPullAuto 除了额外支持 `docker login`，其他命令都应按上面的原始参数使用。

## 输出文件

镜像拉取成功后会生成一个 `.tar` 文件，可用于后续离线导入或分发。

默认情况下，输出文件会生成在运行 `DockerPullAuto.exe` 的当前目录下。例如你在项目目录里运行程序，生成的 `.tar` 文件就会出现在该项目目录中。

输出文件名通常由镜像仓库路径、镜像名和 tag 转换而来，例如：

```text
library_nginx_latest_amd64.tar
namespace_image_tag_arm64.tar
```

如果使用的原始 `DockerPull.exe` 版本支持 `-o` 参数，也可以指定输出目录：

```powershell
-i nginx:latest -o ./downloads
```

这种情况下，生成的 `.tar` 文件会放在 `./downloads` 目录下。

## 重新打包成 exe

请确保当前目录下有这些文件：

```text
DockerPull.exe
docker_pull_auto.py
docker_pull_auto.spec
```

安装 PyInstaller：

```powershell
python -m pip install pyinstaller
```

打包：

```powershell
python -m PyInstaller --clean .\docker_pull_auto.spec
```

打包完成后，新 exe 会生成在：

```text
dist\DockerPullAuto.exe
```

如果要覆盖根目录里的旧版本：

```powershell
Copy-Item .\dist\DockerPullAuto.exe .\DockerPullAuto.exe -Force
```

## 常见问题

如果提示找不到 `DockerPull.exe`，请确认原始 `DockerPull.exe` 和源码/打包配置在同一目录。

如果重新打包时报 `PermissionError` 或“拒绝访问”，通常是旧的 `DockerPullAuto.exe` 还在运行。关闭它后重新执行打包命令即可。

打包生成的 `build` 和 `dist` 是中间/输出目录。确认新的 `DockerPullAuto.exe` 可用后，可以删除 `build`；`dist` 中的 exe 可以复制到根目录保存。
