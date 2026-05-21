# glm-vision

智谱 AI 免费多模态模型的 Claude Code Skill — **看图理解、AI 绘图、AI 视频**，零依赖。

## 能力

| 能力 | 模型 | 说明 |
|------|------|------|
| 图片理解 | `glm-4v-flash` | 快速看图，128K 上下文 |
| 图片分析 | `glm-4.1v-thinking-flash` | 思维链推理，适合图表/逻辑分析 |
| AI 绘图 | `cogview-3-flash` | 文生图 |
| AI 视频 | `cogvideox-flash` | 文生视频 / 图生视频 |

## 安装

### 前置条件

1. 访问 [bigmodel.cn](https://bigmodel.cn) 注册并实名认证
2. 进入控制台 → API Key → 创建新 Key
3. 将 Key 写入环境变量或配置文件：

```bash
# 方式一：环境变量
export ZHIPU_API_KEY=你的key

# 方式二：配置文件
cp .env.example .env
# 编辑 .env 填入你的 Key
```

### 作为 Claude Code Skill 安装

```bash
cp -r glm-vision ~/.claude/skills/glm-vision
```

安装后 Claude 会自动识别视觉相关请求并调用本工具。

### 作为独立 CLI 使用

```bash
python scripts/glm.py --help
```

## 使用

### 图片理解

```bash
python scripts/glm.py vision 截图.png
python scripts/glm.py vision 截图.png -q "分析这个 UI 设计"
python scripts/glm.py vision a.png b.png -q "对比这两张图" --thinking
python scripts/glm.py vision https://example.com/pic.jpg
```

### 交互式视觉对话

```bash
python scripts/glm.py chat 截图.png
# 进入对话模式后可以来回追问
```

### AI 绘图

```bash
python scripts/glm.py draw "一只橘猫坐在窗台上" --enhance
python scripts/glm.py draw "竖版海报" --size 720x1280
```

### AI 视频

```bash
# 一站式（推荐）
python scripts/glm.py video "猫在草地上追蝴蝶"
python scripts/glm.py video "猫追蝴蝶" --image 参考图.png

# 分步
python scripts/glm.py video-submit "描述"
python scripts/glm.py video-poll <task_id>
python scripts/glm.py video-download <url>
```

## 行为特性

- **图片生成** — 完成后自动用默认查看器打开
- **视频生成** — 一站式命令：自动重试提交 → 进度条 → 轮询 → 完成后定位到文件夹
- **零外部依赖** — 纯 Python 标准库，无需 pip install
- **自动重试** — API 限流时指数退避重试

## 技术栈

- Python 3.9+（标准库 only）
- 智谱 AI OpenAPI（v4）
- Claude Code Skill 框架

## 开源协议

MIT
