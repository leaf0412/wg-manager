"""配置常量"""

import random
from pathlib import Path

# 本地配置目录
CONFIG_DIR = Path.home() / ".wg_manager"
DB_FILE = CONFIG_DIR / "wg_manager.db"
EXPORT_DIR = CONFIG_DIR / "clients"

# WireGuard 默认配置
DEFAULT_ADDRESS = "10.0.0.1/24"
DEFAULT_PORT = 51820
DEFAULT_INTERFACE = "wg0"
DEFAULT_DNS = ""  # 默认不设置 DNS
DEFAULT_MTU = 1280

# 远程服务器 WireGuard 配置路径
REMOTE_WG_DIR = "/etc/wireguard"


def generate_random_port() -> int:
    """生成随机监听端口 (10000-60000)"""
    return random.randint(10000, 60000)
