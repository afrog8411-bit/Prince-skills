# skill-downloader 本地索引
# 上次更新: 2026-05-23
# 来源: GitHub API + WebFetch
# 用途: 离线参考，避免每次触发都调 GitHub API（限流 60 次/小时）

---

## 一、Presentation / 幻灯片制作

### 1. shawnzam/keynot
- 地址: https://github.com/shawnzam/keynot
- 说明: 一句话 prompt 生成精美的 HTML 幻灯片，无需 Keynote/PPT。支持键盘导航、滑屏、全屏、动画展示、品牌主题，单文件输出。

### 2. op7418/guizang-ppt-skill
- 地址: https://github.com/op7418/guizang-ppt-skill
- 说明: 杂志风格的 HTML 幻灯片，左右滑屏，10 种布局，5 个主题，WebGL 背景。单文件输出，中文作者。

### 3. iuiaoin/agent-skills (deck)
- 地址: https://github.com/iuiaoin/agent-skills
- 说明: 含 deck skill，两步工作流（/deck --plan + /deck --generate），支持通过 headless Chromium 导出 PPTX。

### 4. zarazhangrui/frontend-slides
- 地址: https://github.com/zarazhangrui/frontend-slides
- 说明: 动画丰富的 HTML 演示，12 种风格，支持 PDF 导出和 Vercel 部署。

### 5. Noi1r/beamer-skill
- 地址: https://github.com/Noi1r/beamer-skill
- 说明: LaTeX Beamer 学术演示，全生命周期：创建→编译→评审→润色→验证，质量评分和教学审查。

### 6. doudou1337/deckset-claude-skill
- 地址: https://github.com/doudou1337/deckset-claude-skill
- 说明: Deckset (macOS) Markdown 幻灯片，29 份文档 + 3 个示例。

### 7. tfriedel/claude-office-skills
- 地址: https://github.com/tfriedel/claude-office-skills
- 说明: Office 文档 skills，含 PPTX/DOCX/XLSX/PDF，支持 HTML 转 PPTX。

### 8. saidwivedi/research-skills
- 地址: https://github.com/saidwivedi/research-skills
- 说明: 含 results-to-slides skill，从 git 历史发现实验结果并生成可编辑的 PPTX。

---

## 二、教育/家教辅导

### 1. GarethManning/education-agent-skills（131 个教学 skill！）
- 地址: https://github.com/GarethManning/education-agent-skills
- 说明: 基于教育研究的 131 个教学 skill，覆盖 19 个领域，每个 skill 标注研究证据强度。
- 目录:

| 领域 | 子 skill 数量 | 对家教的用处 |
|------|-------------|------------|
| memory-learning-science | 8 | **记忆与学习科学** — 含 retrieval-practice（提取练习）、spaced-practice（间隔重复）、feedback-quality（反馈质量分析）、worked-example（示范学习）等，直接可用于错题总结和复习安排 |
| self-regulated-learning | — | 自主学习策略，帮学生建立学习计划 |
| curriculum-assessment | — | 评估设计，可用于出测验题 |
| questioning-discussion | — | 提问与讨论技巧，家教交互 |
| explicit-instruction | — | 显性教学法（直接教学） |
| literacy-critical-thinking | — | 批判性思维与读写 |
| curriculum-alignment | — | 课程对齐，帮学生建立知识结构 |
| inclusive-design | — | 差异化教学，针对不同水平调整 |
| ai-literacy | — | AI 素养 |
| wellbeing-motivation-agency | — | 学生动机与能动性 |

### 2. Orange0618/teach-me-skill
- 地址: https://github.com/Orange0618/teach-me-skill
- 说明: 让 Claude 从「代码生成器」变成「边教边做的导师」。先解释概念再写代码，逐行注释，等你确认才继续。

### 3. SamuelSchlesinger/ai-tutor
- 地址: https://github.com/SamuelSchlesinger/ai-tutor
- 说明: 个性化 AI 导师框架，评估水平→创建课程→互动授课→追踪进度→调整节奏。自适应难度、反思练习。

### 4. zuzuleinen/algotutor
- 地址: https://github.com/zuzuleinen/algotutor
- 说明: 算法陪练，含 32 个概念（从数组到动态规划），基于 FSRS（Anki 算法）的间隔重复复习。

### 5. AnjanJ/BodhiKit（Codeberg）
- 地址: https://codeberg.org/AnjanJ/BodhiKit
- 说明: 17 个教学 skill、3 个 agent、15 个知识库。基于学习科学（Oakley, Feynman, Bloom, Vygotsky 等）。含 /learn、/teach、/quiz、/review、/reflect、/mentor 等命令。

### 6. bevibing/tutor-skills
- 来源: SourcePulse
- 说明: 两个 skill（tutor-setup + tutor），将文档和代码转化为 Obsidian 知识库，含概念级测验追踪。

---

## 三、Skill 仓库索引（meta）

### 1. hesreallyhim/awesome-claude-code
- 地址: https://github.com/hesreallyhim/awesome-claude-code
- 说明: 215+ 资源生态图，涵盖 Tooling(46)、Slash-Commands(44)、Workflows(32)、CLAUDE.md(23)、Agent Skills(18)、Hooks(12) 等。32.3k stars。

### 2. onmyway133/awesome-claude-code
- 地址: https://github.com/onmyway133/awesome-claude-code
- 说明: 精选高质量 Claude Code 工具、skills、插件，限 200+ stars 以上的资源。

### 3. karanb192/awesome-claude-skills
- 地址: https://github.com/karanb192/awesome-claude-skills
- 说明: 50+ 验证过的 Agent Skills，含 TDD、调试、git 工作流、PDF 处理等。

### 4. VoltAgent/awesome-agent-skills
- 地址: https://github.com/VoltAgent/awesome-agent-skills
- 说明: 14.1k stars，官方 Anthropic/Google/Vercel/Stripe skills，兼容 Claude Code、Codex、Gemini CLI、Cursor 等。14.1k stars。

---

## 四、开发类（附带）

### 1. Jeffallan/claude-skills（66 个）
- 地址: https://github.com/Jeffallan/claude-skills
- 说明: 66 个全栈开发 skill，覆盖 12 个类别，3.2k stars。

### 2. obra/superpowers（14 个）
- 地址: https://github.com/obra/superpowers
- 说明: 14 个实战 skill（含 brainstorming、TDD、debugging、code-review、writing-plans 等），多平台兼容（Claude/Cursor/Codex/Gemini），27.9k stars 生态。

---

## 五、原 4 个仓库（保留完整索引于下文）

---

## anthropics/skills — 官方仓库（17 个）

路径前缀: `skills/<name>/` | 分支: main

| # | 名称 | 说明 |
|---|------|------|
| 1 | algorithmic-art | 算法艺术生成 |
| 2 | brand-guidelines | 品牌规范指南 |
| 3 | canvas-design | Canvas 设计 |
| 4 | claude-api | Claude API 开发辅助 |
| 5 | doc-coauthoring | 文档协作写作 |
| 6 | docx | Word 文档创建/编辑/分析 |
| 7 | frontend-design | 前端界面设计 |
| 8 | internal-comms | 内部沟通 |
| 9 | mcp-builder | MCP 服务器构建 |
| 10 | pdf | PDF 处理 |
| 11 | pptx | PPT 幻灯片制作 |
| 12 | skill-creator | Skill 创建与管理 |
| 13 | slack-gif-creator | Slack GIF 创建 |
| 14 | theme-factory | 主题工厂 |
| 15 | web-artifacts-builder | Web Artifacts 构建 |
| 16 | webapp-testing | Web 应用测试 |
| 17 | xlsx | Excel 电子表格处理 |

---

## ComposioHQ/awesome-claude-skills — 社区精选

分支: master

### 根目录通用 skill（32 个）

路径前缀: `<name>/`

| # | 名称 | 说明 |
|---|------|------|
| 1 | artifacts-builder | Artifacts 构建 |
| 2 | brand-guidelines | 品牌规范 |
| 3 | canvas-design | Canvas 设计 |
| 4 | changelog-generator | 更新日志生成 |
| 5 | competitive-ads-extractor | 竞品广告提取 |
| 6 | composio-skills | (分类目录，内含 100+ 自动化 skill) |
| 7 | connect-apps-plugin | 500+ App 连接插件（OAuth） |
| 8 | connect-apps | App 连接器 |
| 9 | connect | 连接器本体 |
| 10 | content-research-writer | 内容调研写作 |
| 11 | developer-growth-analysis | 开发者成长分析 |
| 12 | document-skills | (分类目录，含 docx/pdf/pptx/xlsx) |
| 13 | domain-name-brainstormer | 域名脑暴 |
| 14 | file-organizer | 文件整理 |
| 15 | image-enhancer | 图片增强 |
| 16 | internal-comms | 内部沟通 |
| 17 | invoice-organizer | 发票整理 |
| 18 | langsmith-fetch | LangSmith 数据获取 |
| 19 | lead-research-assistant | 销售线索研究 |
| 20 | mcp-builder | MCP 构建 |
| 21 | meeting-insights-analyzer | 会议洞察分析 |
| 22 | raffle-winner-picker | 抽奖工具 |
| 23 | skill-creator | Skill 创建 |
| 24 | skill-share | Skill 分享 |
| 25 | slack-gif-creator | Slack GIF 创建 |
| 26 | tailored-resume-generator | 简历定制 |
| 27 | template-skill | Skill 模板 |
| 28 | theme-factory | 主题工厂 |
| 29 | twitter-algorithm-optimizer | Twitter 算法优化 |
| 30 | video-downloader | 视频下载 |
| 31 | webapp-testing | Web 测试 |

### composio-skills/ — 自动化连接器（100+，部分示例）

路径前缀: `composio-skills/<name>/`

涵盖各第三方服务的 Claude Code 自动化操作，如：
`atlassian-automation`、`github-automation`、`slack-automation`、`gmail-automation`、
`notion-automation`、`jira-automation`、`asana-automation`、`linear-automation`、
`discord-automation`、`google-sheets-automation`、`google-drive-automation`、
`google-calendar-automation`、`google-docs-automation`、`outlook-automation`、
`hubspot-automation`、`salesforce-automation`、`postgres-automation` ...
共 100+，完整列表通过 `categories` 命令动态获取。

### document-skills/（4 个）

| # | 名称 | 说明 |
|---|------|------|
| 1 | docx | Word 文档 |
| 2 | pdf | PDF 文档 |
| 3 | pptx | PPT 演示 |
| 4 | xlsx | Excel 表格 |

---

## JimLiu/baoyu-skills — 宝玉 skill 集（22 个）

路径前缀: `skills/<name>/` | 分支: main

| # | 名称 | 说明 |
|---|------|------|
| 1 | baoyu-article-illustrator | 文章配图 |
| 2 | baoyu-comic | 漫画生成 |
| 3 | baoyu-compress-image | 图片压缩 |
| 4 | baoyu-cover-image | 封面图生成 |
| 5 | baoyu-danger-gemini-web | Gemini Web 集成 |
| 6 | baoyu-danger-x-to-markdown | X/Twitter 转 Markdown |
| 7 | baoyu-diagram | 图表/图示生成 |
| 8 | baoyu-format-markdown | Markdown 格式化 |
| 9 | baoyu-image-cards | 图片卡片制作 |
| 10 | baoyu-image-gen | 图片生成 |
| 11 | baoyu-imagine | AI 想象绘图 |
| 12 | baoyu-infographic | 信息图制作 |
| 13 | baoyu-markdown-to-html | Markdown 转 HTML |
| 14 | baoyu-post-to-wechat | 发布到公众号 |
| 15 | baoyu-post-to-weibo | 发布到微博 |
| 16 | baoyu-post-to-x | 发布到 X/Twitter |
| 17 | baoyu-slide-deck | 幻灯片制作 |
| 18 | baoyu-translate | 翻译 |
| 19 | baoyu-url-to-markdown | URL 转 Markdown |
| 20 | baoyu-wechat-summary | 公众号文章摘要 |
| 21 | baoyu-xhs-images | 小红书图片处理 |
| 22 | baoyu-youtube-transcript | YouTube 转录 |

---

## stellarlinkco/myclaude — 全栈开发框架

分支: main

### skills/ 目录

| # | 名称 | 说明 |
|---|------|------|
| 1 | do | 5 阶段功能开发工作流 |
| 2 | omo | 多 agent 编排与智能路由 |
| 3 | sparv | SPARV 工作流（Specify→Plan→Act→Review→Vault） |

### 其他目录

| # | 名称 | 位置 | 说明 |
|---|------|------|------|
| 4 | bmad | agents/ | |
| 5 | requirements | agents/ | |
| 6 | development-essentials | agents/ | |
| 7 | browser | (README 提及) | 浏览器自动化 |
| 8 | codex | (README 提及) | |
| 9 | gemini | (README 提及) | |
| 10 | dev | (README 提及) | |
| 11 | product-requirements | (README 提及) | |
| 12 | prototype-prompt-generator | (README 提及) | |
| 13 | skill-install | (README 提及) | |
| 14 | test-cases | (README 提及) | |
