"""WireGuard 管理工具"""

__version__ = "0.1.0"

from .manager import WireGuardManager
from .models import Peer, ServerConfig

__all__ = ["WireGuardManager", "Peer", "ServerConfig"]
