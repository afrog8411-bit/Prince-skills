---
name: flash-key
description: |
  交互式设置向导，为 Claude Code 生成 Windows 键盘快捷键（AutoHotkey v2 脚本）。
  用户可以说"帮我配一套 Claude 快捷键"、"设置快捷键启动 Claude"、"AHK 配置向导"、
  "我想给 Claude 加快捷键"、"窗口管理快捷键"等。也支持直接指令如"帮我写个 Alt+S 启动 Claude"。
  Windows 专用（macOS/Linux 用户会被告知不支持并推荐替代工具）。
  涉及 AutoHotkey、快捷键绑定、终端自动化、Windows 窗口管理。
  触发词包括：快捷键、热键、hotkey、shortcut、启动 Claude、窗口切换、发送文本、ahk、AutoHotkey。
  不要用于非 Windows 快捷键配置或非 Claude Code 相关场景。
---

# flash-key — Claude Code 快捷键设置向导

为 Claude Code 生成 Windows 键盘快捷键（AutoHotkey v2 脚本）。

## 操作系统检测

首次触发时通过 `uname -s` 或 `(Get-CimInstance Win32_OperatingSystem).Caption` 检测用户操作系统：

- **Windows** → 正常走 AutoHotkey 生成流程
- **macOS** → 提示不支持 AHK，推荐 [Hammerspoon](https://www.hammerspoon.org/)
- **Linux** → 提示不支持 AHK，推荐 xdotool / xbindkeys

## 工作模式

两种模式：

### 模式一：交互式向导（默认）

用户说"帮我配一套快捷键"这类模糊需求时，走完整向导流程：

1. 先展示**默认配置预览**，让用户快速选择"就用这套"还是自定义
2. 如果自定义，逐一询问各选项
3. 生成完整 AHK 脚本 + 配套安装脚本

### 模式二：直接生成

用户直接说"我要 Alt+S 打开 C:\projects 目录的 Claude"，跳过向导，直接输出对应脚本。

---

## 默认配置（内置预设）

当用户选择"就用默认"时，使用以下配置。这套配置也是你（作者 Prince）日常使用的快捷键方案。

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Alt+S` | 打开 Claude Code | 在当前目录启动 Claude（默认 `C:\free`） |
| `Alt+C` | 单击：最小化/恢复当前 Claude 窗口 | 有窗口时收回，无窗口时恢复 |
| | 长按：轮转切换多个 Claude 窗口 | 按住超过 300ms 进入轮转模式 |
| `Ctrl+Alt+C` | 将选中文本发送到 Claude 窗口 | 复制 → 激活 Claude → 粘贴发送 |

配套文件：
- `install-ahk.ps1` — AHK v2 安装检测脚本，未安装时自动下载安装

---

## 向导流程

入口是一个三选一的选择器：

```
选项 A：就用默认配置  — 直接生成 Prince 的配置方案
选项 B：自定义设置     — 逐步引导，每步都问
选项 C：直接说需求     — 跳过向导，用户自由描述
```

三种路径如下。

### 路径 A：就用默认配置

用户选这个 → 直接跳到最终确认（展示汇总 → 确认 → 生成）。不再问任何多余问题。

### 路径 B：自定义设置

用户选这个 → 按以下步骤逐一询问。

#### Step 1：项目目录

```
你可以设置快捷键，一键在指定目录打开 Claude Code。
比如 Alt+1 在 D:\projects\blog 打开，Alt+2 在另一个目录打开。

你有要添加的目录吗？直接告诉我路径和想要的快捷键。
如果没有，默认只有一个 Alt+S 启动。
```

用户在对话中给出目录列表。如果只给了目录没指定快捷键，由 skill 自动分配 Alt+1、Alt+2… 依此类推。

#### Step 2：窗口管理

```
是否需要窗口管理功能？
（单击最小化/恢复，长按轮转切换多个 Claude 窗口）

  默认快捷键：Alt+C
  也可以改成其他键，或跳过

  你的选择是？
```

#### Step 3：发送选中文本

```
是否需要"发送选中文本给 Claude"功能？
（选中任意文本，按快捷键自动发送到 Claude 窗口）

  默认快捷键：Ctrl+Alt+C
  也可以改成其他键，或跳过

  你的选择是？
```

#### Step 4：终端选择

```
你使用哪个终端运行 Claude？

  1) Windows Terminal（默认）
  2) PowerShell 7
  3) 命令提示符 (cmd)
  4) Alacritty
  5) WezTerm
  6) Git Bash
  7) ConEmu / Cmder
  8) 其他（请说明）

  你的选择是？
```

### 路径 C：直接说需求

跳过向导，直接根据用户描述生成。

---

## 最终确认（所有路径共用）

无论走哪条路，生成前都要展示汇总让用户确认：

```
## 即将生成以下配置

快捷键方案：
  Alt+S  → C:\free 启动 Claude Code
  Alt+C  → 窗口管理（单击收起 / 长按轮转）
  Ctrl+Alt+C → 选中文本发送给 Claude

终端：Windows Terminal
配套：install-ahk.ps1（AHK v2 安装检测）

确认生成？(Y/n)
```

用户确认后生成文件。文件默认保存到主快捷键对应的目录下：
- 单目录场景（默认 Alt+S）：文件生成到该目录（如 `C:\free\claude_shortcuts.ahk`）
- 多目录场景（Alt+1、Alt+2…）：文件生成到**第一个**目录下
- 配套 `install-ahk.ps1` 与 AHK 文件放在同目录

---

## AHK 代码模式

以下是用到的代码模式，生成时按需组合。

### 启动快捷键

单目录：

```autohotkey
!s::{
  if !DirExist("C:\path") {
    MsgBox("目录不存在: C:\path")
    return
  }
  try Run("wt.exe -d C:\path claude")
}
```

多目录（Alt+1、Alt+2…）：

```autohotkey
!1::{
  target := "C:\project-alpha"
  if !DirExist(target) {
    MsgBox("目录不存在: " target)
    return
  }
  try Run("wt.exe -d """ target """ claude")
}

!2::{
  target := "D:\work"
  if !DirExist(target) {
    MsgBox("目录不存在: " target)
    return
  }
  try Run("wt.exe -d """ target """ claude")
}
```

### 窗口管理（单击/长按）

```autohotkey
_targetExe      := "WindowsTerminal.exe"
_clickThreshold := 300
_cycleInterval  := 400
_pressTick      := 0

!c::{
  global _pressTick
  _pressTick := A_TickCount
  SetTimer(_HoldCheck, -_clickThreshold)
}

!c up::{
  global _pressTick
  SetTimer(_CycleTick, 0)
  if (A_TickCount - _pressTick < _clickThreshold)
    _ClickAction()
}

_HoldCheck() {
  if GetKeyState("c", "P") {
    SetTimer(_CycleTick, _cycleInterval)
    _CycleTick()
  }
}

_CycleTick() { _CycleAction() }

_CycleAction() {
  static idx := 1
  windows := WinGetList("ahk_exe " _targetExe)
  if windows.Length = 0 { idx := 1; return }
  if windows.Length = 1 { WinActivate(windows[1]); return }
  if idx > windows.Length { idx := 1 }
  try WinActivate(windows[idx])
  idx := idx >= windows.Length ? 1 : idx + 1
}

_ClickAction() {
  windows := WinGetList("ahk_exe " _targetExe)
  if windows.Length = 0 { return }
  allMin := true
  for hwnd in windows {
    if WinGetMinMax(hwnd) != -1 { allMin := false; break }
  }
  if allMin { WinActivate(windows[1]); return }
  activeHwnd := WinExist("A")
  for hwnd in windows {
    if hwnd = activeHwnd { WinMinimize(hwnd); return }
  }
  WinActivate(windows[1])
}
```

### 发送选中文本

```autohotkey
^!c::{
  savedClip := ClipboardAll()
  A_Clipboard := ""
  Send("^c")
  if !ClipWait(1) {
    A_Clipboard := savedClip
    return
  }
  text := A_Clipboard
  A_Clipboard := savedClip
  if Trim(text) = "" { return }

  targetClass := "WindowsTerminal.exe"
  if WinExist("ahk_exe " targetClass) {
    WinActivate
    Sleep 200
  } else { return }

  Send("{Enter}")
  Sleep 80
  Send("^v")
  Sleep 80
  Send("{Enter}")
}
```

### AHK v2 脚本头部

每个 `.ahk` 文件必须以固定头部开头：

```autohotkey
#Requires AutoHotkey >=2.0
#SingleInstance Force
; https://www.autohotkey.com/download/ — AHK v2 下载地址（如未安装）
; 安装后双击本文件即可运行。

; 系统托盘菜单
A_IconTip := "Claude Code 快捷键"
TraySetIcon("shell32.dll", 264)
```

---

## 配套安装脚本

每次生成 `.ahk` 时，同时生成 `install-ahk.ps1`：

```powershell
$ahkPaths = @(
    "$env:ProgramFiles\AutoHotkey\v2\AutoHotkey64.exe",
    "$env:ProgramFiles\AutoHotkey\v2\AutoHotkey32.exe",
    "$env:LOCALAPPDATA\Programs\AutoHotkey\v2\AutoHotkey64.exe",
    "$env:LOCALAPPDATA\Programs\AutoHotkey\v2\AutoHotkey32.exe"
)

foreach ($path in $ahkPaths) {
    if (Test-Path $path) {
        Write-Host "[OK] AutoHotkey v2 already installed" -ForegroundColor Green
        exit 0
    }
}

Write-Host "[WARN] AutoHotkey v2 not found, downloading..." -ForegroundColor Yellow

$url = "https://www.autohotkey.com/download/ahk-v2.exe"
$installer = "$env:TEMP\ahk-v2-install.exe"

try {
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
    Start-Process -Wait -FilePath $installer -ArgumentList "/S"
    Remove-Item $installer -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Installation complete!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Installation failed: $_" -ForegroundColor Red
    Write-Host "Manual download: https://www.autohotkey.com/download/" -ForegroundColor Cyan
}
```

---

## 终端映射表

| 终端 | ahk_exe | 启动命令 |
|------|---------|---------|
| Windows Terminal | `WindowsTerminal.exe` | `wt.exe -d [dir] claude` |
| PowerShell 7 | `pwsh.exe` | `pwsh.exe -NoExit -Command claude` |
| 命令提示符 | `cmd.exe` | `cmd.exe /k claude` |
| Alacritty | `alacritty.exe` | `alacritty.exe --working-directory [dir] -e claude` |
| WezTerm | `wezterm-gui.exe` | `wezterm-gui.exe start --cwd [dir] claude` |
| Git Bash | `mintty.exe` | `mintty.exe -d [dir] claude`（需要 Git for Windows） |
| ConEmu / Cmder | `ConEmu64.exe` | `ConEmu64.exe /Dir [dir] claude` |

---

## 生成后说明

生成文件后告诉用户：

1. **安装 AHK v2**：如果未安装，右键 `install-ahk.ps1` → 使用 PowerShell 运行
2. **启动快捷键**：双击 `.ahk` 文件（托盘出现图标）
3. **开机自启**：Win+R → `shell:startup`，把 `.ahk` 放进去
4. **停止/卸载**：右键托盘图标 → Exit；删除文件即可
