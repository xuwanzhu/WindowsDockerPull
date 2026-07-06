import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoginInfo:
    registry: str
    username: str
    password: str


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def bundled_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return app_dir()


def docker_pull_exe() -> Path:
    bundled = bundled_dir() / "DockerPull.exe"
    if bundled.exists():
        return bundled

    sibling = app_dir() / "DockerPull.exe"
    if sibling.exists():
        return sibling

    raise FileNotFoundError("找不到原始 DockerPull.exe")


def split_command(command: str) -> list[str]:
    return shlex.split(command)


def registry_from_image(image: str) -> str:
    first = image.split("/", 1)[0]
    if "." in first or ":" in first or first == "localhost":
        return first
    return ""


def normalize_registry(registry: str) -> str:
    registry = registry.strip()
    for prefix in ("https://", "http://"):
        if registry.startswith(prefix):
            registry = registry[len(prefix):]
    return registry.rstrip("/")


def parse_login(command: str) -> LoginInfo:
    args = split_command(command)
    if len(args) < 2 or [part.lower() for part in args[:2]] != ["docker", "login"]:
        raise ValueError("请输入 docker login 命令")

    registry = ""
    username = ""
    password = ""
    index = 2
    while index < len(args):
        item = args[index]
        if item in {"-u", "--username"} and index + 1 < len(args):
            username = args[index + 1]
            index += 2
            continue
        if item.startswith("--username="):
            username = item.split("=", 1)[1]
            index += 1
            continue
        if item in {"-p", "--password"} and index + 1 < len(args):
            password = args[index + 1]
            index += 2
            continue
        if item.startswith("--password="):
            password = item.split("=", 1)[1]
            index += 1
            continue
        if not item.startswith("-") and not registry:
            registry = item
        index += 1

    if not username:
        username = input("镜像仓库用户名: ").strip()
    if not password:
        password = input("镜像仓库密码: ").strip()

    if not username or not password:
        raise ValueError("用户名和密码不能为空")

    return LoginInfo(normalize_registry(registry), username, password)


def parse_pull(command: str) -> str:
    args = split_command(command)
    if len(args) >= 3 and [part.lower() for part in args[:2]] == ["docker", "pull"]:
        return args[2]
    if len(args) == 1 and not args[0].startswith("docker"):
        return args[0]
    raise ValueError("请输入镜像名或 docker pull 命令")


def pull_with_original_tool(image: str, login: LoginInfo | None) -> bool:
    image_registry = registry_from_image(image)
    registry = image_registry or (login.registry if login else "")

    if login is None:
        print("还没有登录信息，请先输入 docker login 命令。")
        return False

    if login.registry and image_registry and normalize_registry(login.registry) != normalize_registry(image_registry):
        print(f"当前登录仓库是 {login.registry}，拉取镜像仓库是 {image_registry}。")
        print("如果需要切换账号，请先重新输入 docker login 命令。")
        return False

    input_text = "\n".join([image, registry, login.username, login.password, ""]) + "\n"
    print(f"\n调用原始 DockerPull.exe 拉取: {image}")
    process = subprocess.Popen(
        [str(docker_pull_exe())],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output, _ = process.communicate(input_text)
    if output:
        print(output, end="" if output.endswith("\n") else "\n")
    return process.returncode == 0


def main() -> int:
    os.system("")
    login: LoginInfo | None = None

    print("=" * 60)
    print("DockerPullAuto - docker login / docker pull 命令适配器")
    print("=" * 60)
    print("先输入 docker login 命令，再输入 docker pull 命令。输入 q 退出。")
    print("示例: docker login swr.cn-south-1.myhuaweicloud.com -u username -p password")

    while True:
        try:
            command = input("\n请输入命令: ").strip()
            lowered = command.lower()
            if not command:
                continue
            if lowered in {"q", "quit", "exit"}:
                print("已退出。")
                return 0
            if lowered.startswith("docker login"):
                login = parse_login(command)
                shown_registry = login.registry or "dockerhub"
                print(f"已记录登录信息: {shown_registry} / {login.username}")
                continue
            if lowered.startswith("docker pull") or not lowered.startswith("docker "):
                image = parse_pull(command)
                ok = pull_with_original_tool(image, login)
                print("完成。" if ok else "命令执行失败。")
                continue

            print("只支持 docker login 和 docker pull。")
        except KeyboardInterrupt:
            print("\n已退出。")
            return 0
        except Exception as exc:
            print(f"执行失败: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
