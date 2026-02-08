# IP Guardian

基于外部 IP 地址控制 macOS 应用访问的菜单栏工具。

当你的外部 IP 不在允许列表中时，IP Guardian 会自动阻止指定的 GUI 应用启动，并拦截指定的 CLI 命令。适用于需要在特定网络环境下限制应用使用的场景。

## 功能

- **GUI 应用监控** — 实时监听应用启动事件，当 IP 不在白名单时自动终止指定应用
- **CLI 命令拦截** — 通过 PATH 注入 wrapper 脚本，在执行前检查 IP（支持放行特定子命令）
- **菜单栏状态** — 在 macOS 菜单栏显示当前 IP 和状态图标（allowed / blocked / error）
- **开机自启** — 通过 LaunchAgent 实现登录时自动启动
- **系统通知** — 应用被拦截或状态变化时推送 macOS 通知

## 安装

### 依赖

- macOS
- Python 3.12+
- [rumps](https://github.com/jaredks/rumps) — macOS 菜单栏框架
- [pyobjc](https://pyobjc.readthedocs.io/) — 用于监听应用启动事件

### 步骤

```bash
# 克隆仓库
git clone https://github.com/<your-username>/ip-guardian.git
cd ip-guardian

# 安装依赖
pip3 install -r requirements.txt

# 复制配置文件并填入你的 IP
cp config.example.json config.json
# 编辑 config.json，将 YOUR_IP_HERE 替换为你的外部 IP

# 运行
python3 -m ip_guardian
```

或者使用一键安装脚本（会自动配置 CLI 拦截）：

```bash
bash setup.sh
```

## 配置

编辑 `config.json`（首次运行会自动复制到 `~/.ip_guardian/config.json`）：

```json
{
  "allowed_ips": ["YOUR_IP_HERE"],
  "gui_apps": [
    {"name": "ChatGPT", "bundle_id": "com.openai.chat"},
    {"name": "Claude", "bundle_id": "com.anthropic.claudefordesktop"}
  ],
  "cli_commands": [
    {"cmd": "codex", "allowed_subcommands": ["update"]},
    {"cmd": "claude", "allowed_subcommands": ["update"]}
  ],
  "check_interval": 30
}
```

| 字段 | 说明 |
|------|------|
| `allowed_ips` | 允许的外部 IP 列表 |
| `gui_apps` | 需要监控的 GUI 应用列表（`name` 用于通知显示，`bundle_id` 用于识别应用） |
| `cli_commands` | 需要拦截的 CLI 命令（`allowed_subcommands` 中的子命令会跳过 IP 检查） |
| `check_interval` | IP 检查间隔（秒） |

获取你当前的外部 IP：

```bash
curl ifconfig.me
```

查找应用的 Bundle ID：

```bash
osascript -e 'id of app "AppName"'
```

## 构建 .app

使用 py2app 打包为独立的 macOS 应用：

```bash
pip3 install py2app
python3 setup_app.py py2app
```

构建产物在 `dist/IP Guardian.app`，可以拖入 `/Applications` 使用。

## 项目结构

```
ip-guardian/
├── ip_guardian/
│   ├── __init__.py
│   ├── __main__.py      # python3 -m ip_guardian 入口
│   ├── app.py            # 菜单栏应用主逻辑
│   ├── app_monitor.py    # GUI 应用启动监听
│   ├── autostart.py      # 开机自启管理（LaunchAgent）
│   ├── cli_guard.py      # CLI wrapper 生成
│   ├── config.py         # 配置文件管理
│   └── ip_checker.py     # 外部 IP 检查
├── icons/                # 菜单栏状态图标
├── config.example.json   # 配置模板
├── requirements.txt
├── setup.sh              # 一键安装脚本
├── setup_app.py          # py2app 构建脚本
└── gen_icons.py          # 图标生成工具
```

## License

MIT
