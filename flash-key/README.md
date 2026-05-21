# claude-ahk

**Claude Code 快捷键设置向导 / Claude Code Shortcut Wizard**

交互式设置向导，为 Claude Code 生成 Windows 键盘快捷键（AutoHotkey v2 脚本）。
An interactive setup wizard that generates Windows keyboard shortcuts (AutoHotkey v2) for Claude Code.

---

## 简介 / Overview

你在 Windows 上用 Claude Code 时，是否经常觉得切换窗口很麻烦？这个 skill 可以帮你：

- **一键启动** — 按快捷键在指定目录打开 Claude
- **窗口管理** — 单击收起/恢复 Claude 窗口，长按轮转切换
- **快速发送** — 选中任意文本，一键发送给 Claude

Ever felt annoyed switching windows while using Claude Code on Windows? This skill helps you:

- **One-key launch** — Open Claude Code in your project directory instantly
- **Window management** — Click to minimize/restore, hold to cycle through windows
- **Quick send** — Select any text, one key to send it to Claude

## 要求 / Requirements

- Windows 10 / 11 (AutoHotkey 仅支持 Windows)
- Claude Code CLI 已安装
- AutoHotkey v2（skill 会自动生成安装脚本）

## 安装 / Installation

### 方式一：通过 install-skill 安装（推荐）

```
/claude install-skill claude-ahk
```

### 方式二：手动安装

1. 下载 `SKILL.md` 文件
2. 放入 `~/.claude/skills/claude-ahk/` 目录
3. 重启 Claude Code

### 方式三：本地安装（开发模式）

将项目 `SKILL.md` 复制或软链接到 `~/.claude/skills/claude-ahk/SKILL.md`。

## 使用方法 / Usage

安装后，对 Claude Code 说以下任意一句话即可触发：

**中文：**
- "帮我配一套 Claude 快捷键"
- "设置快捷键启动 Claude"
- "我想给 Claude 加快捷键"
- "帮我写个 Alt+S 启动 Claude"

**English:**
- "Set up keyboard shortcuts for Claude Code"
- "Create AHK shortcuts for Claude"
- "I want to add hotkeys for Claude"

### 三种配置方式 / Three Setup Modes

| 模式 / Mode | 说明 / Description |
|------------|-------------------|
| **就用默认配置** / Use defaults | 直接生成 Prince 的日常配置方案，一键搞定 |
| **自定义设置** / Customize | 逐项设置项目目录、快捷键、窗口管理等功能 |
| **直接说需求** / Tell me directly | 跳过向导，直接描述你要的快捷键 |

### 默认配置 / Default Preset

| 快捷键 / Hotkey | 功能 / Function |
|----------------|-----------------|
| `Alt+S` | 在当前目录打开 Claude Code / Launch Claude Code |
| `Alt+C` (单击/click) | 最小化/恢复 Claude 窗口 / Minimize/restore window |
| `Alt+C` (长按/hold) | 轮转切换多个 Claude 窗口 / Cycle through windows |
| `Alt+V` | 截图秒发：存图并打出路径，手动回车发送 / Save screenshot and print path |

### 生成的配套文件 / Generated Files

skill 会生成两个文件放到你指定的目录：

- `claude_shortcuts.ahk` — 快捷键脚本，双击运行
- `install-ahk.ps1` — AHK v2 安装检测脚本（未安装时自动下载安装）

## 文件结构 / File Structure

```
claude-ahk/
├── SKILL.md           # Skill 本体 / Skill definition
├── README.md          # 本文件 / This file
├── LICENSE            # MIT 许可证
├── evals/
│   └── evals.json     # 测试用例 / Test cases
└── scripts/
    └── install-ahk.ps1  # 参考安装脚本 / Reference installer
```

## 跨平台说明 / Cross-Platform Notes

AutoHotkey 是 Windows 独占工具。如果你在 macOS 或 Linux 上使用，skill 会提示：

- **macOS**: 建议使用 [Hammerspoon](https://www.hammerspoon.org/) 实现类似功能
- **Linux**: 建议使用 xdotool / xbindkeys

## 许可 / License

MIT
