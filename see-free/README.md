# see-free

**Claude 缺视觉能力？GLM-5V-Turbo / 智谱免费模型补上。**

Claude Code 本身不支持多模态。让它看图、分析图表、识别 UI 截图、提取手写笔记——它做不到。see-free 通过调用智谱 AI 的视觉模型补这块能力。

支持两种方案：
- **免费方案**：智谱免费模型（glm-4v-flash），日常够用
- **付费方案**：GLM-5V-Turbo，识别精度大幅提升（Design2Code 94.8），适合需要准确识别文字和图表的场景

> 纯 Python 实现，零外部依赖。

## 能力

| 能力 | 模型 | 方案 | 说明 |
|------|------|------|------|
| 图片理解 | `glm-5v-turbo`（推荐）或 `glm-4v-flash` | 付费/免费 | 截图、图表、UI、手写笔记、试卷 |
| 交互式视觉对话 | 同上 | 付费/免费 | 丢一张图，来回追问 |
| 批量多图理解 | 同上 | 付费/免费 | 串行处理，进度显示，支持 --json |
| AI 绘图 | `cogview-3-flash` | 免费 | 文生图 |
| AI 视频 | `cogvideox-flash` | 免费 | 文生/图生视频 |

## 快速开始

### 1. 获取 API Key

**免费方案**：去 [bigmodel.cn](https://bigmodel.cn) 注册 → 实名认证 → 创建 API Key

**付费方案**：在智谱控制台开通 GLM-5V-Turbo 的按量付费

### 2. 配置

在 `~/.claude/skills/see-free/.env` 中写入：

```bash
# 免费 Key（绘图/视频用），至少配一个
ZHIPU_API_KEY=你的免费key

# 付费 Key（视觉识别用，可选），配了就用 GLM-5V-Turbo
ZHIPU_API_KEY_PAID=你的付费key
```

### 3. 安装

```bash
/claude install https://github.com/afrog8411-bit/Prince-skills/tree/main/see-free
```

## 用法

在 Claude Code 里直接说：

**图片理解**
- "帮我看看这张图 /path/to/image.png"
- "这个 UI 设计怎么样"
- "对比这两张截图"
- "分析这张图里的图表数据 ——json"

**批量处理**
- "把这个文件夹里的截图都分析一遍"
- "批量识别这些图片里的文字"

**绘图/视频**
- "帮我画一张赛博朋克猫"
- "把这张图做成视频"

## 输出格式

默认终端友好输出。支持 `--json` 参数输出结构化数据：

```json
{"success": true, "result": "描述内容...", "model": "glm-5v-turbo"}
```

## CLI 命令

```bash
# 单张图片理解
python glm.py vision <图片路径> -q "问题" [--json]

# 批量多图理解（串行，自动处理付费 key 限流）
python glm.py batch-vision img1.png img2.png -q "描述这张图" --json

# 视觉对话
python glm.py chat <图片路径>

# 绘图
python glm.py draw "描述" [--enhance]

# 视频
python glm.py video "描述"

# 查看 Key 状态
python glm.py keys
```

## License

MIT
