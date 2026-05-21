# claude-ahk 改进设计

## 现状摘要

claude-ahk 是一个交互式向导 Skill，为 Claude Code 生成 Windows AutoHotkey v2 快捷键脚本。当前功能完整但存在可优化空间。

## 改进方向

### 1. AHK 代码质量（高优先级）

- **ClipboardAll 恢复语法修正**：当前 `ClipboardAll() := savedClip` 在 AHK v2 中可能不是标准写法，改为 `A_Clipboard := savedClip` 或 `ClipboardAll(savedClip)` 
- **窗口管理健壮性**：增加多个 Claude 窗口同时打开时的兜底逻辑
- **系统托盘菜单**：添加右键菜单（Reload、Suspend、Edit、Exit）
- **启动目录校验**：检查目标目录是否存在，不存在时提示而非静默失败

### 2. 终端支持扩展（中优先级）

当前只支持 Windows Terminal、PowerShell、CMD。可扩展：
- Alacritty
- WezTerm
- mintty (Git Bash)
- ConEmu / Cmder
- 用户自定义终端

### 3. Skill 触发与向导优化（中优先级）

- 补全更多触发关键词，提升匹配准确率
- 增加对用户误触发的兜底处理
- 向导流程加入"上一步"回溯能力

### 4. 测试与验证（持续）

- 扩展 evals.json 到 5-7 个用例
- 添加 AHK v2 语法验证逻辑
- 验证 PowerShell 脚本语法

### 5. 文档

- 增加故障排查章节
- 清理 README 冗余内容

## 迭代计划

每轮迭代聚焦一个方向，改完验证 → git commit → 进入下一轮。
