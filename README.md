# DockerPullAuto

DockerPullAuto 是一个命令适配器，用来把常见的 `docker login` / `docker pull` 输入方式转换成原始 `DockerPull.exe` 的交互输入流程。

原始 `DockerPull.exe` 不依赖本机 Docker Engine，也不要求 Docker Desktop 正在运行。DockerPullAuto 只是让你可以用更熟悉的 Docker 命令格式操作它。

## 文件说明

- `DockerPull.exe`: 原始镜像下载工具，必须保留。
- `DockerPullAuto.exe`: 已打包好的可执行程序，日常直接运行这个文件。
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
docker login swr.cn-south-1.myhuaweicloud.com -u username -p password
```

然后输入拉取命令：

```powershell
docker pull swr.cn-south-1.myhuaweicloud.com/hw36423330/editor-2d:wip-jinlu-c41be194
```

也可以直接输入镜像名：

```powershell
swr.cn-south-1.myhuaweicloud.com/hw36423330/editor-2d:wip-jinlu-c41be194
```

输入下面任意一个命令退出：

```powershell
q
quit
exit
```

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
