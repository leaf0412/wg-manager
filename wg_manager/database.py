"""SQLite 数据库管理"""

import sqlite3
from pathlib import Path
from typing import Optional

from .models import Peer, ServerConfig


class Database:
    """SQLite 数据库管理"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._migrate_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS server (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    private_key TEXT NOT NULL,
                    public_key TEXT NOT NULL,
                    address TEXT NOT NULL DEFAULT '10.0.0.1/24',
                    listen_port INTEGER NOT NULL DEFAULT 51820,
                    interface TEXT NOT NULL DEFAULT 'wg0',
                    endpoint TEXT NOT NULL,
                    post_up TEXT DEFAULT '',
                    post_down TEXT DEFAULT '',
                    ssh_host TEXT DEFAULT '',
                    ssh_port INTEGER DEFAULT 22,
                    ssh_user TEXT DEFAULT 'root'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS peers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL DEFAULT 1,
                    name TEXT NOT NULL,
                    public_key TEXT NOT NULL,
                    private_key TEXT DEFAULT '',
                    preshared_key TEXT DEFAULT '',
                    address TEXT NOT NULL,
                    allowed_ips TEXT DEFAULT '',
                    dns TEXT DEFAULT '',
                    listen_port INTEGER DEFAULT 0,
                    mtu INTEGER DEFAULT 1280,
                    created_at TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    UNIQUE(server_id, name),
                    FOREIGN KEY (server_id) REFERENCES server(id)
                )
            """)
            conn.commit()

    def _migrate_db(self):
        """数据库迁移 - 添加新字段"""
        with self._get_conn() as conn:
            # 检查 peers 表字段
            cursor = conn.execute("PRAGMA table_info(peers)")
            columns = [row[1] for row in cursor.fetchall()]

            if "listen_port" not in columns:
                conn.execute("ALTER TABLE peers ADD COLUMN listen_port INTEGER DEFAULT 0")

            if "mtu" not in columns:
                conn.execute("ALTER TABLE peers ADD COLUMN mtu INTEGER DEFAULT 1280")

            if "server_id" not in columns:
                conn.execute("ALTER TABLE peers ADD COLUMN server_id INTEGER DEFAULT 1")

            conn.commit()

    # ========== 服务端管理 ==========

    def get_servers(self) -> list[ServerConfig]:
        """获取所有服务端"""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM server ORDER BY id").fetchall()
            return [self._row_to_server(row) for row in rows]

    def get_server(self, server_id: int = 1) -> Optional[ServerConfig]:
        """获取指定服务端配置"""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM server WHERE id = ?", (server_id,)).fetchone()
            if row:
                return self._row_to_server(row)
        return None

    def get_server_by_endpoint(self, endpoint: str) -> Optional[ServerConfig]:
        """根据 endpoint 获取服务端"""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM server WHERE endpoint = ?", (endpoint,)).fetchone()
            if row:
                return self._row_to_server(row)
        return None

    def _row_to_server(self, row: sqlite3.Row) -> ServerConfig:
        """将数据库行转换为 ServerConfig 对象"""
        return ServerConfig(
            id=row["id"],
            private_key=row["private_key"],
            public_key=row["public_key"],
            address=row["address"],
            listen_port=row["listen_port"],
            interface=row["interface"],
            endpoint=row["endpoint"],
            post_up=row["post_up"],
            post_down=row["post_down"]
        )

    def save_server(self, server: ServerConfig) -> ServerConfig:
        """保存服务端配置（新增或更新）"""
        with self._get_conn() as conn:
            if server.id:
                # 更新现有服务端
                conn.execute("""
                    UPDATE server SET private_key = ?, public_key = ?, address = ?,
                        listen_port = ?, interface = ?, endpoint = ?, post_up = ?, post_down = ?
                    WHERE id = ?
                """, (server.private_key, server.public_key, server.address,
                      server.listen_port, server.interface, server.endpoint,
                      server.post_up, server.post_down, server.id))
            else:
                # 新增服务端
                cursor = conn.execute("""
                    INSERT INTO server (private_key, public_key, address, listen_port,
                                        interface, endpoint, post_up, post_down)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (server.private_key, server.public_key, server.address,
                      server.listen_port, server.interface, server.endpoint,
                      server.post_up, server.post_down))
                server.id = cursor.lastrowid
            conn.commit()
        return server

    def delete_server(self, server_id: int) -> bool:
        """删除服务端及其所有客户端"""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM peers WHERE server_id = ?", (server_id,))
            cursor = conn.execute("DELETE FROM server WHERE id = ?", (server_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_ssh_config(self, server_id: int = 1) -> Optional[dict]:
        """获取 SSH 配置"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT ssh_host, ssh_port, ssh_user FROM server WHERE id = ?",
                (server_id,)
            ).fetchone()
            if row and row["ssh_host"]:
                return {
                    "host": row["ssh_host"],
                    "port": row["ssh_port"] or 22,
                    "user": row["ssh_user"] or "root"
                }
        return None

    def save_ssh_config(self, server_id: int, host: str, port: int = 22, user: str = "root"):
        """保存 SSH 配置"""
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE server SET ssh_host = ?, ssh_port = ?, ssh_user = ?
                WHERE id = ?
            """, (host, port, user, server_id))
            conn.commit()

    # ========== 客户端管理 ==========

    def get_peers(self, server_id: int = 1) -> list[Peer]:
        """获取指定服务端的所有客户端"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM peers WHERE server_id = ? ORDER BY created_at",
                (server_id,)
            ).fetchall()
            return [self._row_to_peer(row) for row in rows]

    def get_peer_by_name(self, name: str, server_id: int = 1) -> Optional[Peer]:
        """根据名称获取客户端"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM peers WHERE name = ? AND server_id = ?",
                (name, server_id)
            ).fetchone()
            if row:
                return self._row_to_peer(row)
        return None

    def _row_to_peer(self, row: sqlite3.Row) -> Peer:
        """将数据库行转换为 Peer 对象"""
        # 兼容旧数据库
        listen_port = row["listen_port"] if "listen_port" in row.keys() else 0
        mtu = row["mtu"] if "mtu" in row.keys() else 1280
        server_id = row["server_id"] if "server_id" in row.keys() else 1

        return Peer(
            id=row["id"],
            server_id=server_id,
            name=row["name"],
            public_key=row["public_key"],
            private_key=row["private_key"],
            preshared_key=row["preshared_key"],
            address=row["address"],
            allowed_ips=row["allowed_ips"],
            dns=row["dns"],
            listen_port=listen_port,
            mtu=mtu,
            created_at=row["created_at"],
            enabled=bool(row["enabled"])
        )

    def add_peer(self, peer: Peer) -> Peer:
        """添加客户端"""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO peers (server_id, name, public_key, private_key, preshared_key,
                                   address, allowed_ips, dns, listen_port, mtu,
                                   created_at, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (peer.server_id, peer.name, peer.public_key, peer.private_key,
                  peer.preshared_key, peer.address, peer.allowed_ips, peer.dns,
                  peer.listen_port, peer.mtu, peer.created_at, 1 if peer.enabled else 0))
            conn.commit()
            peer.id = cursor.lastrowid
        return peer

    def remove_peer(self, name: str, server_id: int = 1) -> bool:
        """删除客户端"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM peers WHERE name = ? AND server_id = ?",
                (name, server_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def toggle_peer(self, name: str, server_id: int = 1) -> Optional[bool]:
        """切换客户端启用状态"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT enabled FROM peers WHERE name = ? AND server_id = ?",
                (name, server_id)
            ).fetchone()
            if row:
                new_status = 0 if row["enabled"] else 1
                conn.execute(
                    "UPDATE peers SET enabled = ? WHERE name = ? AND server_id = ?",
                    (new_status, name, server_id)
                )
                conn.commit()
                return bool(new_status)
        return None

    def get_used_ips(self, server_id: int = 1) -> set[int]:
        """获取已使用的 IP 地址最后一段"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT address FROM peers WHERE server_id = ?",
                (server_id,)
            ).fetchall()
            used = {1}  # 服务器使用 .1
            for row in rows:
                ip = row["address"].split("/")[0]
                parts = ip.split(".")
                if len(parts) == 4:
                    used.add(int(parts[-1]))
            return used
