# flash-key

**快捷键办事，不靠鼠标。**

在 Windows 上用 Claude Code 不用再切窗口、输路径、复制粘贴。装了这个 skill，一键启动、一键发送、一键收回。

> 交互式设置向导，为 Claude Code 生成 Windows 键盘快捷键（AutoHotkey v2 脚本）。

## 效果

| 快捷键 | 干的事 |
|--------|--------|
| `Alt+S` | 在项目目录一键打开 Claude |
| `Alt+C` (单击) | 最小化/恢复 Claude 窗口，像按遥控器 |
| `Alt+C` (长按) | 在多个 Claude 窗口之间轮转切换 |
| `Ctrl+Alt+C` | 选中任何文本 → 一键发给 Claude |

## 三种配置方式

- **就用默认** — 我的日常方案，直接用
- **自定义设置** — 项目目录、快捷键、终端类型，逐项配
- **直接说需求** — "帮我写个 Alt+S 启动 D:\projects\blog 的 Claude"

## 要求

- Windows 10 / 11
- Claude Code CLI
- AutoHotkey v2（skill 会自动生成安装脚本）

## 文件

```
claude-ahk/
├── SKILL.md
├── scripts/
│   ├── install-ahk.ps1    ← AHK v2 安装检测
│   └── validate-ahk.ps1   ← AHK 语法验证
└── evals/
    └── evals.json
```

## License

MIT
