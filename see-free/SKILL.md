---
name: see-free
description: >
  智谱AI 多模态 — 看图理解(GLM-5V付费)、AI 绘图、AI 视频、多 Key 并行批处理。
  以下场景触发：

  图片理解：用户发来图片路径/截图/screenshot、问"看看这张图"、"帮我看看"、"图片里有什么"、
  "这是什么图"、"截图里有什么"、"读一下这张图"、"分析这张图"、"识别图片"、"提取图中文字"、
  "这张图讲了什么"、"这个UI/设计怎么样"、"图表数据是什么"、"对比这两张图"。

  AI 绘图："画一张"、"帮我画"、"生成图片"、"设计一个"、"做个图"、"生成海报/logo/封面"、
  "帮我做张图"、描述画面后要求画出来。

  AI 视频："生成视频"、"做个视频"、"帮我做个动画/视频"、"文生视频"、"图生视频"。

  批量/队列："批量生成"、"多张图"、"一次生成多张"、"队列"、"读这个文件每行生成一张"、
  "批量分析这些图"、"一次性看这些图"、"全部理解一遍"。

  不触发：纯文字对话、抽象讨论、不涉及任何视觉内容的请求（如"你觉得呢"）。
---

# 智谱AI 视觉 Skill v5.1 — 稳健执行引擎

用智谱 AI 平台补 deepseek 缺失的视觉能力。**视觉识别走付费 GLM-5V-Turbo，绘图/视频走免费模型**。

## 模型

| 能力 | 模型 | 费用 | 说明 |
|------|------|------|------|
| 图片理解 | `glm-5v-turbo` | **付费** | 智谱旗舰多模态，Design2Code 94.8，输入 $1.20/M |
| AI 绘图 | `cogview-3-flash` | 免费 | 文生图 |
| AI 视频 | `cogvideox-flash` | 免费 | 文生视频，异步提交 |

## 前置条件：配置 API Key

需要两类 Key：

### 1. 付费 Key（视觉识别用）

从智谱开放平台获取付费 API Key，写入 `.env`：

```
ZHIPU_API_KEY_PAID=你的付费key
```

### 2. 免费 Key（绘图/视频用）

注册智谱 → 创建 API Key：

```
ZHIPU_API_KEY=免费key
ZHIPU_API_KEY_2=第二个       # 可选，用于并行加速
ZHIPU_API_KEY_3=第三个       # 可选
```

两个池子互不干扰。**付费 Key 没配好时 vision/chat 会报错，draw/video 不受影响。**

## 脚本命令

```bash
# ========== 视觉对话（推荐）==========
python ~/.claude/skills/see-free/scripts/glm.py chat <图片路径或URL>

# 例：丢一张图，然后像聊天一样追问
python ~/.claude/skills/see-free/scripts/glm.py chat 截图.png
python ~/.claude/skills/see-free/scripts/glm.py chat https://example.com/pic.jpg

# 输入 exit 退出

# ========== 单次图片理解（GLM-5V-Turbo 付费）==========
python ~/.claude/skills/see-free/scripts/glm.py vision <路径或URL>
python ~/.claude/skills/see-free/scripts/glm.py vision <路径或URL> -q 帮我分析一下这个UI设计
python ~/.claude/skills/see-free/scripts/glm.py vision a.png b.png -q 对比这两张截图 --json

# ========== AI 绘图（免费）==========
python ~/.claude/skills/see-free/scripts/glm.py draw "描述文本"
python ~/.claude/skills/see-free/scripts/glm.py draw "描述" [输出路径] --size 720x1280 --enhance

# ========== AI 视频（免费，一站式：自动提交 → 轮询 → 下载打开）==========
python ~/.claude/skills/see-free/scripts/glm.py video "描述"
python ~/.claude/skills/see-free/scripts/glm.py video "描述" --image 参考图.png

# ========== AI 视频（手动分步）==========
python ~/.claude/skills/see-free/scripts/glm.py video-submit "描述"
python ~/.claude/skills/see-free/scripts/glm.py video-poll <task_id>
python ~/.claude/skills/see-free/scripts/glm.py video-download <url> [输出路径]

# ========== 并行批量处理 ==========

# 查看所有 API Key 的健康状态（含付费 Key）
python ~/.claude/skills/see-free/scripts/glm.py keys

# 串行多图理解（GLM-5V-Turbo 付费，逐张处理）
python ~/.claude/skills/see-free/scripts/glm.py batch-vision img1.png img2.png img3.png -q "描述这张图" --json

# 并行生成多张图片（免费）
python ~/.claude/skills/see-free/scripts/glm.py batch-draw "prompt1" "prompt2" "prompt3" [--workers 3] [--enhance] [--size 1024x1024]

# 从文件读取提示词，逐行生成图片
python ~/.claude/skills/see-free/scripts/glm.py queue prompts.txt [--workers 3] [--enhance]
```

### 选项说明

* `--enhance`: 自动追加质量关键词，适合 prompt 较短时
* `--size`: 1024x1024（方图）| 1280x720（横版）| 720x1280（竖版）
* `--thinking`: （兼容旧调用，v5 中统一用 GLM-5V-Turbo，此参数忽略）
* `--json`: 输出 JSON 格式 `{"success": true, "result": "...", "model": "glm-5v-turbo"}`，适合程序消费
* `--workers`: （保留兼容，付费 key 实际串行）
* URL 支持: vision 和 chat 接受 HTTP/HTTPS 图片链接
* 图片已默认去除 AI 水印

## Key 管理

**免费 Key 池**（`ZHIPU_API_KEY` / `_2` / `_3` …）：
- 用于 draw/video/batch-draw/queue 命令
- round-robin 多 Key 调度，遇 429 自动冷却切换
- 健康状态持久化（`.key_state.json`）

**付费 Key**（`ZHIPU_API_KEY_PAID`）：
- 用于 vision/chat/batch-vision 命令
- 单 key 直连，5 次指数退避重试 + 1302 限流等待 30s
- 并发限制为 1（账户级），batch 自动串行处理

## 输出格式

```
[智谱视觉] 这是一张电商后台的订单详情页截图。页面顶部显示订单号...
```

绘图/视频：
```
已生成图片，保存到 `C:\free\glm-output\image_xxx.png`
提示词：xxx
尺寸：1024×1024
```

批量（终端输出）：
```
[1/3] img1.png ...
[2/3] img2.png ...
[3/3] img3.png ...
[OK] img1.png: 这是一张...（前200字）
[FAIL] img2.png: 错误信息
```

批量（`--json`）：
```json
{"success": true, "total": 3, "ok": 2, "fail": 1, "results": [...]}
```

## 错误处理

- 付费 Key 未设置 → 提示设置 ZHIPU_API_KEY_PAID
- 免费 Key 未设置 → 引导注册智谱
- 图片路径不存在或 URL 无效 → 请用户确认
- API 429/5xx → 自动重试（免费 key 切换 key，付费 key 指数退避）
- 1302 账户限流 → 等待 30s 后重试，最多 3 次
- 内容审核拦截 → 提示用户调整提示词
- 视频失败（VIDEO_FAILED）→ 告知用户重新提交

## 搭配推荐

本 skill 解决的是"AI 能不能看懂图"的问题，但截图发给 AI 本身是个痛点——
终端不能直接粘贴图片，而且微信 Alt+A、Win+Shift+S、Snipaste 等截图工具行为各不相同。

推荐安装 [flash-key](https://github.com/afrog8411-bit/Prince-skills/tree/main/flash-key)，
启用**截图秒发**功能（Alt+V），一键把剪贴板图片存成文件并打出路径：

```
任意工具截图 → 切到 Claude → Alt+V → 路径自动打出 → 回车 → see-free 看懂
```

两个 skill 各司其职，打通"截图→发给 AI→AI 看懂"全流程。
