# glm-vision

**给 Claude 装上一双眼睛。**

发张图就能聊。截图、照片、图表、UI 设计图、手写笔记——扔过去，Claude 看得懂。还能画图、做视频。

> 智谱 AI 免费多模态模型的 Claude Code Skill，零依赖。

## 能力

| 能力 | 说人话 | 模型 |
|------|--------|------|
| 图片理解 | 发张图问"这是什么"、"里面写了什么"、"帮我分析这个图表" | `glm-4v-flash` |
| 图片分析 | 图表数据解读、逻辑推理、UI 评审 | `glm-4.1v-thinking-flash` |
| AI 绘图 | "画一只赛博朋克猫" | `cogview-3-flash` |
| AI 视频 | "让这只猫动起来" | `cogvideox-flash` |

## 安装

### 前置条件

1. 去 [bigmodel.cn](https://bigmodel.cn) 注册并实名认证（免费额度够用）
2. 控制台 → API Key → 创建新 Key
3. 把 Key 填到 `.env` 里：

```bash
GLM_API_KEY=你的key
```

### 安装 skill

```bash
/claude install https://github.com/afrog8411-bit/Prince-skills/tree/main/glm-vision
```

### 安装 Python 依赖

```bash
pip install zhipuai pillow
```

## 用法

安装后在 Claude Code 里说：

- "帮我看看这张图" + 图片路径
- "这张图表讲了什么"
- "画一张..."
- "把这张图做成视频"

## License

MIT
