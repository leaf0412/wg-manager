# WireGuard Manager

一个 Python 命令行工具，用于管理 WireGuard VPN 服务端和客户端配置。

## 功能特性

- **多服务端管理**: 支持管理多个 WireGuard 服务端，按 endpoint (IP/域名) 区分
- **客户端管理**: 添加、删除、启用/禁用客户端
- **配置导出**: 导出客户端配置内容和二维码
- **SSH 远程管理**: 通过 SSH 连接远程服务器，自动同步配置并热重载
- **交互式菜单**: 美观的命令行交互界面
- **命令行模式**: 支持脚本化操作

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd wireguard

# 使用 uv 安装依赖
uv sync
```

### 依赖

- Python 3.10+
- qrcode (用于生成二维码，可选)
- 系统 `ssh` 和 `scp` 命令 (用于远程管理)

## 使用方法

### 交互式菜单

```bash
uv run wg-manager
```

菜单界面:

```
┌────────────────────────────────────────────────┐
│              WireGuard 管理工具                │
└────────────────────────────────────────────────┘

  当前: example.com
  3 个客户端 | 共 2 个服务端
  ● SSH 已连接

┌─ 服务端 ───────────────────────────────────────┐
│  1. 初始化新服务端      2. 从文件导入          │
│  3. 手动输入私钥导入    4. 查看配置            │
│  5. 切换服务端          6. 删除服务端          │
├─ 客户端 ───────────────────────────────────────┤
│  7. 添加客户端          8. 删除客户端          │
│  9. 启用/禁用          10. 列出所有            │
│ 11. 导出配置           12. 显示二维码          │
├─ 远程管理 ─────────────────────────────────────┤
│ 13. 配置 SSH           14. 从远程导入          │
│ 15. 同步到远程         16. 查看远程状态        │
├─ 其他 ─────────────────────────────────────────┤
│ 17. 导出服务端配置      0. 退出                │
└────────────────────────────────────────────────┘
```

**提示**: 在任何输入环节，按 `Ctrl+C` 可返回主菜单。

### 命令行模式

```bash
# 查看帮助
uv run wg-manager --help

# 列出所有服务端
uv run wg-manager servers

# 切换服务端
uv run wg-manager use example.com

# 初始化新服务端
uv run wg-manager init -e example.com

# 从配置文件导入服务端
uv run wg-manager import -f /etc/wireguard/wg0.conf -e example.com

# 手动导入服务端 (输入私钥)
uv run wg-manager import -k <私钥> -e example.com

# 添加客户端
uv run wg-manager add -n phone
uv run wg-manager add -n laptop --dns 1.1.1.1 --mtu 1420

# 列出客户端
uv run wg-manager list

# 显示客户端配置
uv run wg-manager export -n phone

# 显示并保存到文件
uv run wg-manager export -n phone --save

# 显示二维码
uv run wg-manager export -n phone --qr

# 导出服务端配置
uv run wg-manager server

# 配置 SSH 连接
uv run wg-manager ssh --host 1.2.3.4

# 同步配置到远程服务器
uv run wg-manager sync

# 查看远程 WireGuard 状态
uv run wg-manager remote-status

# 删除客户端
uv run wg-manager remove -n phone

# 删除服务端
uv run wg-manager delete-server example.com
```

### 指定服务端操作

使用 `-s` 参数指定要操作的服务端:

```bash
# 在指定服务端上添加客户端
uv run wg-manager -s example.com add -n phone

# 列出指定服务端的客户端
uv run wg-manager -s vpn.example.org list
```

## 远程管理

配置 SSH 后，添加/删除客户端会自动同步到远程服务器:

1. **配置 SSH**: 交互式菜单选择 `13` 或执行 `wg-manager ssh --host <IP>`
2. **添加客户端**: 自动上传配置并动态添加 peer (不中断现有连接)
3. **删除客户端**: 自动更新配置并动态移除 peer
4. **手动同步**: 执行 `wg-manager sync` 全量同步

远程操作使用 `wg syncconf` 实现热重载，不会中断现有 VPN 连接。

## 数据存储

配置数据保存在 `~/.wg_manager/` 目录:

```
~/.wg_manager/
├── wg_manager.db      # SQLite 数据库
└── clients/           # 导出的客户端配置文件 (可选)
```

## 项目结构

```
wireguard/
├── pyproject.toml      # 项目配置
├── uv.lock             # 依赖锁定
├── README.md           # 说明文档
└── wg_manager/         # 源码目录
    ├── __init__.py     # 包初始化
    ├── cli.py          # 命令行接口
    ├── manager.py      # 核心管理逻辑
    ├── database.py     # SQLite 数据库操作
    ├── models.py       # 数据模型
    ├── config.py       # 配置常量
    ├── crypto.py       # WireGuard 密钥生成
    └── ssh.py          # SSH 远程管理
```

## 许可证

MIT
