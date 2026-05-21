# flash-key — Claude Code 快捷键 Skill

## 项目说明
- 为 Claude Code 生成 Windows 快捷键的交互式 Skill
- 核心产物：`SKILL.md`（skill 本体）、`scripts/install-ahk.ps1`、`evals/evals.json`
- 语言：SKILL.md 中文，AHK v2 脚本，PowerShell

## 验证
- AHK v2 语法：检查 `{` `}` 配对、`::` 热键定义格式、函数调用正确
- PowerShell 语法：`pwsh -NoProfile -Command "& { .\scripts\install-ahk.ps1; exit $LASTEXITCODE }"`
- 评估：每次修改后检查 evals.json 中的 3 个用例是否能被 SKILL.md 的 description 覆盖

## 迭代原则
- 每次迭代锁定一个方面：AHK 脚本质量 / PowerShell 脚本 / SKILL.md 完整性 / 文档
- 改完必须验证语法再提交
- 每轮迭代前先读当前状态，不做重复改动

## 目录约定
- `SKILL.md` — skill 定义（核心文件）
- `scripts/` — 配套脚本
- `evals/` — 测试用例
- 根目录不积内容文件
