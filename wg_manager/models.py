"""数据模型定义"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Peer:
    """客户端/Peer 配置"""
    id: Optional[int]
    server_id: int  # 所属服务端 ID
    name: str
    public_key: str
    private_key: str
    preshared_key: str
    address: str
    allowed_ips: str = "0.0.0.0/0, ::/0"
    dns: str = ""
    listen_port: int = 0  # 客户端监听端口，0 表示随机
    mtu: int = 1280
    created_at: str = ""
    enabled: bool = True


@dataclass
class ServerConfig:
    """服务端配置"""
    id: Optional[int] = None
    private_key: str = ""
    public_key: str = ""
    address: str = "10.0.0.1/24"
    listen_port: int = 51820
    interface: str = "wg0"
    endpoint: str = ""
    post_up: str = ""
    post_down: str = ""
