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

- **Windows** → 正常走 AutoHotkey 生成流程。先简单说明：AutoHotkey（AHK）是一个 Windows 下的快捷键工具，这个 skill 会为你生成一套 AHK 脚本，安装后按快捷键就能操控 Claude Code。脚本安全、开源、不联网。
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
| `Alt+V` | 截图秒发 | 剪贴板有图时自动存图并打出路径，你手动回车发送给 Claude |

可选附加：
- 「发送选中文本」功能（默认不开启）：选中文本后按快捷键自动发送到 Claude 窗口。如需要可在自定义设置中开启并分配快捷键，建议用 `Ctrl+Shift+C` 等不易误触的组合。

配套文件：
- `install-ahk.ps1` — AHK v2 安装检测脚本，未安装时自动下载安装
- `save-clipimg.ps1` — 剪贴板图片保存助手

---

## 向导流程

入口是一个三选一的选择器：

```
选项 A：就用默认配置  — 一键生成，即装即用
选项 B：自定义设置     — 逐步引导，每步都问
选项 C：直接说需求     — 跳过向导，用户自由描述
```

三种路径如下。

### 路径 A：就用默认配置

用户选这个 → 检测 `C:\free` 是否存在：
- **存在** → 直接跳到最终确认。不再问任何多余问题。
- **不存在** → 问一句："Alt+S 要在哪个目录打开 Claude？" 用户给一个路径即可，不问其他选项。

然后展示汇总 → 确认 → 生成。

### 路径 B：自定义设置

用户选这个 → 按以下步骤逐一询问。

#### Step 1：项目目录

用 AskUserQuestion 询问（单选）：

```json
{
  "question": "设置快捷键一键在指定目录打开 Claude Code。比如 Alt+S 在 C:\free 启动，Alt+1 在 D:\projects\blog 启动。",
  "header": "项目目录",
  "options": [
    {"label": "默认单目录", "description": "Alt+S 在 C:\free 启动 Claude Code（推荐）"},
    {"label": "自定义目录", "description": "自己指定路径和快捷键"},
    {"label": "多目录", "description": "添加多个目录，分配 Alt+1、Alt+2…"},
    {"label": "跳过", "description": "不需要启动快捷键"}
  ],
  "multiSelect": false
}
```

各选项后续处理：
- 选"默认单目录"→ 检测 `C:\free` 是否存在。不存在时让用户输入路径。
- 选"自定义目录"→ 让用户输入路径，可选指定快捷键（未指定则用 Alt+S）。
- 选"多目录"→ 让用户逐一输入目录列表。如果只给了目录没指定快捷键，自动分配 Alt+1、Alt+2…。
- 选"跳过"→ 不留启动快捷键。

#### Step 2：窗口管理

用 AskUserQuestion 询问（单选）：

```json
{
  "question": "是否需要窗口管理功能？单击 Alt+C 最小化/恢复 Claude 窗口，长按超过 300ms 轮转切换多个 Claude 窗口。",
  "header": "窗口管理",
  "options": [
    {"label": "开启，默认 Alt+C", "description": "单击收起/恢复，长按轮转切换（推荐）"},
    {"label": "开启，自定义快捷键", "description": "自己指定快捷键"},
    {"label": "跳过", "description": "不需要此功能"}
  ],
  "multiSelect": false
}
```

- 选"自定义快捷键"→ 再用 AskUserQuestion 问用户要什么组合键，建议避开 Alt+S 和 Alt+V
- 选"跳过"→ 不留窗口管理快捷键

#### Step 3：发送选中文本（可选，默认不开启）

用 AskUserQuestion 询问（单选）：

```json
{
  "question": "是否需要「发送选中文本给 Claude」功能？选中文字后按快捷键自动复制并发送到 Claude 窗口。",
  "header": "发送文本",
  "options": [
    {"label": "开启，默认快捷键", "description": "用 Ctrl+Shift+C（推荐，不易与其他软件冲突）"},
    {"label": "开启，自定义快捷键", "description": "自己指定快捷键"},
    {"label": "不需要", "description": "跳过此功能（默认）"}
  ],
  "multiSelect": false
}
```

- 选"不需要"→ 跳过
- 选"自定义快捷键"→ 再用 AskUserQuestion 问用户要什么组合键

#### Step 4：终端选择

用 AskUserQuestion 询问（单选）：

```json
{
  "question": "你使用哪个终端运行 Claude？",
  "header": "终端选择",
  "options": [
    {"label": "Windows Terminal", "description": "默认"},
    {"label": "PowerShell 7", "description": "pwsh.exe"},
    {"label": "命令提示符", "description": "cmd.exe"},
    {"label": "Alacritty", "description": "alacritty.exe"},
    {"label": "WezTerm", "description": "wezterm-gui.exe"},
    {"label": "Git Bash", "description": "mintty.exe / Git for Windows"},
    {"label": "ConEmu / Cmder", "description": "ConEmu64.exe"},
    {"label": "其他", "description": "用户自行说明"}
  ],
  "multiSelect": false
}
```

按终端映射表（见下文）填写对应的 `ahk_exe` 和启动命令。选"其他"时让用户补充终端 exe 名称。

#### Step 5：截图秒发

这个功能解决一个很常见但各家截图工具不一样的痛点。

**问题**：终端不接受图片粘贴。不管你用微信 Alt+A、Win+Shift+S、Snipaste、还是 PrintScreen——截完图图片在剪贴板，但切到 Claude 终端按 Ctrl+V，没有反应。

**解决**：Alt+V 把剪贴板图片自动存成文件并打出路径，你手动回车发给 Claude。不管你用什么截图工具，最后都是按同一个快捷键。

```
像这样：截图（任意工具）→ 切到 Claude → Alt+V → C:\free\screenshots\xxx.png → 回车

注意：路径打出来后你可以加描述再回车，也可以直接回车。
```

用 AskUserQuestion 询问（单选）：

```json
{
  "question": "是否需要「截图秒发」功能？开启后按 Alt+V 自动存图并打出路径，手动回车发送给 Claude。\n\n说明：终端不接受图片粘贴。不管什么截图工具——截完图图片在剪贴板，切到 Claude 终端按 Ctrl+V 没反应。Alt+V 自动存图→打出路径→你回车发送。\n\n搭配推荐：如果你也安装了 see-free（视觉识别 skill），截图发给 Claude 后可调用视觉模型看图。一套快捷键打通「截图→发给 AI→AI 看懂」。",
  "header": "截图秒发",
  "options": [
    {"label": "开启，默认 Alt+V", "description": "不与任何常用快捷键冲突（推荐）"},
    {"label": "开启，自定义快捷键", "description": "自己指定快捷键"},
    {"label": "跳过", "description": "不需要此功能"}
  ],
  "multiSelect": false
}
```

- 选"自定义快捷键"→ 再用 AskUserQuestion 问用户要什么组合键
- 选"跳过"→ 不留截图秒发功能

### 路径 C：直接说需求

跳过向导，直接根据用户描述生成。

---

## 最终确认（所有路径共用）

无论走哪条路，生成前都要做两项预检：

1. **claude 命令检查**：运行 `claude --version`（通过 PowerShell），如果失败，提示用户先安装 Claude Code CLI 或将其加入 PATH
2. **生成目录检查**：确认目标目录是否存在，不存在则自动创建

预检通过后，展示汇总让用户确认：

```
## 即将生成以下配置

快捷键方案：
  Alt+S  → C:\free 启动 Claude Code
  Alt+C  → 窗口管理（单击收起 / 长按轮转）
  Alt+V  → 截图秒发（存图 + 打出路径，手动回车发送）

终端：Windows Terminal
配套：install-ahk.ps1（AHK v2 安装检测）+ save-clipimg.ps1（截图秒发助手）

确认生成？(Y/n)
```

用户确认后生成文件。文件默认保存到主快捷键对应的目录下：
- 单目录场景（默认 Alt+S）：文件生成到该目录（如 `C:\free\claude_shortcuts.ahk`）
- 多目录场景（Alt+1、Alt+2…）：文件生成到**第一个**目录下
- 配套 `install-ahk.ps1`（AHK 安装检测）和 `save-clipimg.ps1`（截图粘贴助手）与 AHK 文件放在同目录

---

## AHK 脚本组装说明

生成时按以下顺序拼装各个代码片段：

```
1. 脚本头部（#Requires、#SingleInstance、托盘菜单）
2. 全局变量定义（_targetExe、_screenshotsDir 等）
3. 快捷键定义（Alt+S 启动、Alt+C 窗口管理、Ctrl+Alt+C 发送文本、Alt+V 截图秒发）
4. 函数定义（_ClickAction、_CycleAction、_HoldCheck 等）
```

每个片段以 `; ── 功能名 ──` 注释分隔。生成的 `.ahk` 文件是完整可运行的，用户不需要手动拼接。

## AHK 代码模式

以下是用到的代码模式，生成时按需组合。

### 启动快捷键

单目录：

```autohotkey
!s::{
  target := "C:\path"
  if !DirExist(target) {
    MsgBox("[flash-key] 目录不存在: " target "`n请检查路径或重新配置。")
    return
  }
  try {
    Run("wt.exe -d """ target """ claude")
  } catch as err {
    MsgBox("[flash-key] 启动失败: " err.Message "`n`n常见原因：claude 命令未在 PATH 中`n请先确认 'claude --version' 能在终端正常运行。")
  }
}
```

多目录（Alt+1、Alt+2…）：

```autohotkey
!1::{
  target := "C:\project-alpha"
  if !DirExist(target) {
    MsgBox("[flash-key] 目录不存在: " target)
    return
  }
  try Run("wt.exe -d """ target """ claude")
  catch as err {
    MsgBox("[flash-key] 启动失败: " err.Message "`n请确认 claude 命令可用。")
  }
}

!2::{
  target := "D:\work"
  if !DirExist(target) {
    MsgBox("[flash-key] 目录不存在: " target)
    return
  }
  try Run("wt.exe -d """ target """ claude")
  catch as err {
    MsgBox("[flash-key] 启动失败: " err.Message "`n请确认 claude 命令可用。")
  }
}
```

### 窗口管理（单击/长按）

根据终端映射表（见下）设置 `_targetExe`。例：Windows Terminal 用 `WindowsTerminal.exe`，WezTerm 用 `wezterm-gui.exe`。

```autohotkey
_targetExe      := "WindowsTerminal.exe"  ; 按终端映射表修改
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

### 截图秒发（Alt+V）

专用快捷键，不与正常粘贴冲突。按 Alt+V 时检测剪贴板有图则存图并打出路径，你手动回车发送。

生成时把脚本路径写死为绝对路径（`A_ScriptDir`），避免用户移动 `.ahk` 文件后找不到脚本。

对应脚本：`save-clipimg.ps1`（生成在同目录）

```autohotkey
_screenshotsDir := "C:\free\screenshots"
_scriptDir := A_ScriptDir  ; 生成时替换为实际绝对路径

!v::{
  if !DllCall("IsClipboardFormatAvailable", "uint", 2)  ; CF_BITMAP
    return

  if !DirExist(_screenshotsDir)
    DirCreate(_screenshotsDir)
  ts := FormatTime(, "yyyy-MM-dd_HHmmss")
  filePath := _screenshotsDir "\" ts ".png"

  activeHwnd := WinExist("A")

  RunWait('powershell -NoProfile -File "' _scriptDir '\save-clipimg.ps1" "' _screenshotsDir '"', , "Hide")

  if FileExist(filePath) {
    WinActivate(activeHwnd)
    Sleep 100
    Send(filePath)
  }
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

生成文件后按以下步骤操作，并逐项验证：

**第一步：安装 AHK v2**
- 如果未安装 AutoHotkey v2，右键 `install-ahk.ps1` → **使用 PowerShell 运行**
- ⚠ 如果提示"无法加载文件...因为在此系统上禁止运行脚本"，以管理员身份运行 PowerShell 执行：
  ```
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
  然后再次右键运行 `install-ahk.ps1`
- 脚本会自动下载安装，看到绿色 `[OK]` 提示即成功
- 如果下载失败（中国用户），手动下载：`https://mirrors.tuna.tsinghua.edu.cn/archlinux/community/x86_64/autohotkey/`（Arch Linux 镜像，或直接在浏览器打开 autohotkey.com 下载）

**第二步：启动快捷键**
- 双击生成的 `.ahk` 文件
- ✅ **验证方法**：系统托盘出现绿色 `H` 图标（AutoHotkey），说明运行成功
- 如果没看到图标，检查是否已安装 AHK v2（回到第一步）

**第三步：测试每个快捷键**
- `Alt+S` → 应打开 Claude Code 终端
- `Alt+C` → 单击收起窗口，长按轮转切换
- `Ctrl+Alt+C` → 选中文本后发送到 Claude
- `Alt+V` → 截图后打出图片路径
- 某个快捷键没反应？检查托盘图标是否在 → 双击 `.ahk` 重新加载

⚠ **快捷键冲突**：如果某个快捷键在你其他软件中已占用（例如 Snipaste 用 Alt+S），右键托盘绿色 `H` 图标 → Suspend Hotkeys 暂停全部快捷键，或者 Edit This Script 自行修改键位。

**临时暂停：** 右键托盘绿色 `H` 图标 → Suspend Hotkeys（暂停全部快捷键）。再次点击恢复。不需要退出。

**第四步（可选）：开机自启**
- Win+R → 输入 `shell:startup` → 回车
- 把 `.ahk` 文件复制到打开的文件夹
- 下次开机自动运行

**停止 / 卸载**
- 停止：右键托盘绿色 `H` 图标 → Exit
- 卸载：删除 `.ahk` 文件和配套的 `install-ahk.ps1`、`save-clipimg.ps1`
