# WireGuard Manager

一个 Python 命令行工具，用于管理 WireGuard VPN 服务端和客户端配置。

## 功能特性

- **多服务端管理**: 支持管理多个 WireGuard 服务端，按 `endpoint:interface` 组合区分
- **多网段支持**: 同一服务器可配置多个接口（wg0、wg1、wg2...），每个接口独立管理
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

  当前: example.com:wg0
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

# 切换到指定服务端的特定接口
uv run wg-manager use example.com -i wg1

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

## 多网段场景

当一台服务器需要配置多个 WireGuard 网段时（如隔离不同团队或用途），可以使用多接口方式管理。

### 使用场景示例

假设有一台公网服务器 `vpn.example.com`，需要配置三个独立的 VPN 网段：

| 接口 | 网段 | 端口 | 用途 |
|------|------|------|------|
| wg0 | 10.0.0.0/24 | 51820 | 开发团队 |
| wg1 | 10.1.0.0/24 | 51821 | 运维团队 |
| wg2 | 10.2.0.0/24 | 51822 | 测试环境 |

### 配置步骤

```bash
# 1. 初始化三个服务端接口

# 开发团队 (wg0, 默认)
uv run wg-manager init -e vpn.example.com -a 10.0.0.1/24 -p 51820 -i wg0

# 运维团队 (wg1)
uv run wg-manager init -e vpn.example.com -a 10.1.0.1/24 -p 51821 -i wg1

# 测试环境 (wg2)
uv run wg-manager init -e vpn.example.com -a 10.2.0.1/24 -p 51822 -i wg2

# 2. 查看所有服务端
uv run wg-manager servers

# 输出:
# 服务端列表:
#   vpn.example.com:wg0    10.0.0.1/24    Port:51820    0 客户端 (当前)
#   vpn.example.com:wg1    10.1.0.1/24    Port:51821    0 客户端
#   vpn.example.com:wg2    10.2.0.1/24    Port:51822    0 客户端

# 3. 在 wg0 (开发团队) 添加客户端
uv run wg-manager add -n dev-alice
uv run wg-manager add -n dev-bob

# 4. 切换到 wg1 (运维团队) 并添加客户端
uv run wg-manager use vpn.example.com -i wg1
uv run wg-manager add -n ops-charlie
uv run wg-manager add -n ops-dave

# 5. 切换到 wg2 (测试环境) 并添加客户端
uv run wg-manager use vpn.example.com -i wg2
uv run wg-manager add -n test-server-1
uv run wg-manager add -n test-server-2

# 6. 导出各接口的服务端配置
uv run wg-manager use vpn.example.com -i wg0 && uv run wg-manager server
uv run wg-manager use vpn.example.com -i wg1 && uv run wg-manager server
uv run wg-manager use vpn.example.com -i wg2 && uv run wg-manager server
```

### 从现有配置导入

如果服务器上已有多个 WireGuard 配置文件：

```bash
# 导入 wg0.conf
uv run wg-manager import -f /etc/wireguard/wg0.conf -e vpn.example.com

# 导入 wg1.conf
uv run wg-manager import -f /etc/wireguard/wg1.conf -e vpn.example.com

# 导入 wg2.conf
uv run wg-manager import -f /etc/wireguard/wg2.conf -e vpn.example.com
```

导入时会自动识别配置文件名作为接口名。

### SSH 远程管理多接口

每个接口可以独立配置 SSH 连接：

```bash
# 为 wg0 配置 SSH
uv run wg-manager use vpn.example.com -i wg0
uv run wg-manager ssh --host vpn.example.com

# 切换到 wg1 后，SSH 配置需要重新设置
uv run wg-manager use vpn.example.com -i wg1
uv run wg-manager ssh --host vpn.example.com

# 添加客户端会自动同步到对应的远程接口
uv run wg-manager add -n new-client
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
