# see-free

**DeepSeek 没有眼睛，智谱免费借你一双。**

DeepSeek V4 再强也只是纯文本。要「看图」？"帮我分析这张图表"？"给这段文案配张图"？"把这个做成视频"？——DeepSeek 做不到。

智谱 AI 的免费多模态 API 刚好补上这块。而且不用额外付费。

> Claude Code Skill，零依赖。

## 白嫖什么

| 能力 | 说明 | 免费 |
|------|------|------|
| 图片理解 | 发截图、图表、UI、手写笔记，让 AI 看 | 免费额度够用 |
| 图片分析 | 图表数据解读、逻辑推理、UI 评审（思维链） | 免费 |
| AI 绘图 | "赛博朋克猫""极简风海报"，文生图 | 免费 |
| AI 视频 | 图生视频、文生视频 | 免费 |

## 和 DeepSeek 什么关系

没有任何关系。纯互补。

你用 DeepSeek 写代码、推理、长文——它擅长的事交给它。遇到图片、视觉生成类的需求，这个 skill 帮你一键调智谱的免费 API。同一个 Claude 会话里无缝切换。

## 安装

### 1. 注册智谱

去 [bigmodel.cn](https://bigmodel.cn) → 注册 → 实名认证 → 控制台创建 API Key（免费额度日常够用）

### 2. 配置 Key

```bash
GLM_API_KEY=你的key
```

### 3. 安装 skill

```bash
/claude install https://github.com/afrog8411-bit/Prince-skills/tree/main/see-free
```

### 4. 装 Python 依赖

```bash
pip install zhipuai pillow
```

## 用法

在 Claude Code 里直接说：

- "帮我看看这张图 /path/to/image.png"
- "这个 UI 设计怎么样"
- "这张图表的数据趋势是什么"
- "帮我画一张..."
- "把这张图做成视频"

## License

MIT
