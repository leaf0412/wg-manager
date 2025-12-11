"""WireGuard 密钥生成模块"""

import subprocess
from typing import Optional


class WireGuardKeyError(Exception):
    """密钥操作错误"""
    pass


def run_wg_command(args: list[str]) -> tuple[bool, str]:
    """执行 wg 命令"""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        return False, "未找到 wg 命令，请确保已安装 WireGuard"


def generate_private_key() -> str:
    """生成私钥"""
    success, result = run_wg_command(["wg", "genkey"])
    if not success:
        raise WireGuardKeyError(f"生成私钥失败: {result}")
    return result


def generate_public_key(private_key: str) -> str:
    """从私钥生成公钥"""
    try:
        result = subprocess.run(
            ["wg", "pubkey"],
            input=private_key,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        raise WireGuardKeyError(f"生成公钥失败: {e}")


def generate_keypair() -> tuple[str, str]:
    """生成密钥对 (私钥, 公钥)"""
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    return private_key, public_key


def generate_preshared_key() -> str:
    """生成预共享密钥"""
    success, result = run_wg_command(["wg", "genpsk"])
    if not success:
        raise WireGuardKeyError(f"生成预共享密钥失败: {result}")
    return result
