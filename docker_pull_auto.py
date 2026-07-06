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
    sibling = app_dir() / "DockerPull.exe"
    if sibling.exists():
        return sibling

    bundled = bundled_dir() / "DockerPull.exe"
    if bundled.exists():
        return bundled

    raise FileNotFoundError("找不到原始 DockerPull.exe")


def split_command(command: str) -> list[str]:
    return shlex.split(command)


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


def strip_program_name(args: list[str]) -> list[str]:
    if args and args[0].lower() in {"dockerpull.exe", "dockerpull", ".\\dockerpull.exe"}:
        return args[1:]
    return args


def has_option(args: list[str], short_name: str, long_name: str) -> bool:
    for item in args:
        if item == short_name or item == long_name or item.startswith(f"{long_name}="):
            return True
    return False


def add_missing_login_args(args: list[str], login: LoginInfo | None) -> list[str]:
    if login is None:
        return args
    if not has_option(args, "-i", "--image"):
        return args

    result = list(args)
    if login.registry and not has_option(result, "-r", "--custom_registry"):
        result.extend(["-r", login.registry])
    if not has_option(result, "-u", "--username"):
        result.extend(["-u", login.username])
    if not has_option(result, "-p", "--password"):
        result.extend(["-p", login.password])
    return result


def hide_password(args: list[str]) -> list[str]:
    safe_args = list(args)
    index = 0
    while index < len(safe_args):
        item = safe_args[index]
        if item in {"-p", "--password"} and index + 1 < len(safe_args):
            safe_args[index + 1] = "******"
            index += 2
            continue
        if item.startswith("--password="):
            safe_args[index] = "--password=******"
        index += 1
    return safe_args


def run_original_tool(args: list[str], login: LoginInfo | None) -> bool:
    args = add_missing_login_args(strip_program_name(args), login)
    shown = " ".join(shlex.quote(item) for item in hide_password(args))
    print(f"\n调用原始 DockerPull.exe: {shown}", flush=True)

    stdin_text = "\n" if args else None
    result = subprocess.run([str(docker_pull_exe()), *args], input=stdin_text, text=True)
    return result.returncode == 0


def print_usage_examples() -> None:
    print("\n使用示例:")
    print("# 下载 Docker Hub 镜像")
    print(" -i nginx:latest")
    print()
    print("# 下载指定架构镜像")
    print(" -i alpine:latest -a arm64")
    print()
    print("# 下载私有仓库镜像")
    print(" -i harbor.example.com/library/nginx:1.26.0 -u admin -p password")
    print()
    print("# 指定输出目录")
    print(" -i nginx:latest -o ./downloads")
    print()
    print("# 静默模式下载")
    print(" -i nginx:latest -q")
    print()
    print("# 下载 Quay.io 多架构镜像")
    print(" -i quay.io/ascend/vllm-ascend:v0.11.0-a3-openeuler -a arm64")


def main() -> int:
    os.system("")
    login: LoginInfo | None = None

    if len(sys.argv) > 1:
        ok = run_original_tool(sys.argv[1:], login)
        input("\n按回车退出...")
        return 0 if ok else 1

    print("=" * 60)
    print("DockerPullAuto - DockerPull.exe + docker login")
    print("=" * 60)
    print("先输入 docker login 命令记录账号密码。")
    print("之后按 DockerPull.exe 原始参数使用，例如: -i nginx:latest -a amd64")
    print("输入 q 退出。")
    print_usage_examples()

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

            ok = run_original_tool(split_command(command), login)
            print("完成。" if ok else "命令执行失败。")
        except KeyboardInterrupt:
            print("\n已退出。")
            return 0
        except Exception as exc:
            print(f"执行失败: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
