---
name: skill-downloader
description: |
  Skill 市场 — 从多个 Skill 仓库浏览、搜索、下载安装 Claude Code Skill。
  用户说以下话时触发：
  - "帮我找个skill"、"下载skill"、"skill市场"、"skill下载"
  - "有没有能翻译的skill"、"找能做xx的skill"、"搜索能做xx的skill"
  - "看看anthropic官方有什么skill"、"看看composio有什么"、"看看宝玉有什么skill"
  - "从baoyu装一个翻译"、"装一个做PPT的skill"
  - "安装xx skill"、"下载xx skill"、"装个xx"
  - "看看有什么新skill"、"最近有什么好skill"
  - "做pre"、"做演示"、"做幻灯片"、"presentation"、"slide"、"keynote" — 幻灯片制作
  - "家教"、"辅导"、"教学"、"教育"、"错题"、"复习"、"学习计划" — 教育辅导
  - "有没有教育相关的skill"、"有没有做演示的skill"

  支持的仓库（15 个）：
  - anthropics/skills — 官方（17 个）
  - ComposioHQ/awesome-claude-skills — 社区（140+ 个）
  - JimLiu/baoyu-skills — 中文（22 个）
  - stellarlinkco/myclaude — 框架（~10+ 个）
  - GarethManning/education-agent-skills — 131 个教学 skill
  - shawnzam/keynot — HTML 幻灯片
  - op7418/guizang-ppt-skill — 杂志风 HTML 幻灯片
  - zarazhangrui/frontend-slides — 动画 HTML 演示
  - Noi1r/beamer-skill — LaTeX 学术演示
  - Orange0618/teach-me-skill — AI 导师
  - SamuelSchlesinger/ai-tutor — 个性化辅导
  - obra/superpowers — 14 个实战 dev skill
  - Jeffallan/claude-skills — 66 个全栈 skill

  搜索/查找：support "search" command for cross-repo keyword search.

  不触发：用户只是想了解 skill 概念、讨论 skill 设计、不涉及下载安装。
---

# skill-downloader — Skill 市场

从 15 个仓库浏览、搜索、下载安装 Claude Code Skill。

## 本地索引

`SKILL-INDEX.md` 保存了已爬取的 skill 名称和分类，`search` 命令会自动查本地索引。

## 脚本

`C:\free\skills\skill-downloader\scripts\skill-manager.ps1`

## 命令速查

```powershell
# 查看所有可用仓库
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" list-repos

# 列出仓库中的 skill
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" list -Repo anthropics/skills

# 列出仓库子分类的 skill（教育/Composio）
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" list -Repo GarethManning/education-agent-skills -Subdir memory-learning-science

# 搜索 skill（跨仓库，查名称+本地索引）
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" search -Keyword slide

# 查看 skill 信息
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" info -Repo anthropics/skills -Skill docx

# 查看子分类中的 skill 信息（教育）
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" info -Repo GarethManning/education-agent-skills -Skill retrieval-practice-generator -Subdir memory-learning-science

# 安装 skill（到 ~/.claude/skills/）
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" install -Repo JimLiu/baoyu-skills -Skill baoyu-translate

# 单 skill 仓库不用写 -Skill
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" install -Repo shawnzam/keynot

# 从子目录安装
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" install -Repo GarethManning/education-agent-skills -Skill retrieval-practice-generator -Subdir memory-learning-science

# 安装到指定目录
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" install -Repo JimLiu/baoyu-skills -Skill baoyu-translate -Dest C:\free\.claude\skills\baoyu-translate

# 看仓库有哪些子分类
powershell -NoProfile -File "C:\free\skills\skill-downloader\scripts\skill-manager.ps1" categories -Repo GarethManning/education-agent-skills
```

## 工作流程

### 场景 A：用户说"看看有什么 skill"
1. `list-repos` 展示 15 个仓库
2. 用户选定仓库 → `list -Repo X` 获取 skill 列表
3. 用户选定 skill → `info -Repo X -Skill Y` 展示详情
4. 确认后 `install -Repo X -Skill Y`

### 场景 B：搜索 skill
1. `search -Keyword <关键词>` 跨仓库搜索 skill 名称
2. 搜索结果含仓库来源
3. 选定后用 `info` 确认，然后 `install`

### 场景 C：直接安装
- 多 skill 仓库：`install -Repo X -Skill Y`
- 单 skill 仓库：`install -Repo X`（自动填 skill 名）
- 子分类 skill：`install -Repo X -Skill Y -Subdir Z`

## 仓库总览（15 个）

### 原有 4 个
| 仓库 | 数量 | 特点 |
|------|------|------|
| anthropics/skills | 17 | 官方，docx/pdf/pptx/xlsx/frontend-design |
| ComposioHQ/awesome-claude-skills | 140+ | 社区精选，含 100+ 自动化 skill |
| JimLiu/baoyu-skills | 22 | 中文特色，翻译/配图/公众号/小红书 |
| stellarlinkco/myclaude | ~10 | 全栈开发框架 |

### 新增 — 教育
| 仓库 | 数量 | 特点 |
|------|------|------|
| GarethManning/education-agent-skills | 131 | 证据驱动教学，19 个分类 |
| Orange0618/teach-me-skill | 1 | AI 导师模式 |
| SamuelSchlesinger/ai-tutor | — | 个性化学习框架 |

### 新增 — 演示
| 仓库 | 特点 |
|------|------|
| shawnzam/keynot | Prompt → HTML 幻灯片 |
| op7418/guizang-ppt-skill | 杂志风滑屏 HTML 演示 |
| zarazhangrui/frontend-slides | 动画 HTML 演示，12 风格 |
| Noi1r/beamer-skill | LaTeX Beamer 学术演示 |

### 新增 — 开发
| 仓库 | 数量 | 特点 |
|------|------|------|
| obra/superpowers | 14 | TDD、debugging、code-review 等 |
| Jeffallan/claude-skills | 66 | 全栈开发技能覆盖 |

## 安装后处理
- 全局 `~/.claude/skills/<name>/` → 重启 Claude Code 生效
- 项目级 `.claude/skills/<name>/` → 仅当前项目可用

## 备注
- 使用 `ghproxy.net` 代理 GitHub（中国用户）
- API 限流可设 `GITHUB_TOKEN` 环境变量
- `search` 命令同时查 API 和本地 `SKILL-INDEX.md`
- 单 skill 仓库（keynot、guizang 等）自动填充 skill 名，安装更快捷
