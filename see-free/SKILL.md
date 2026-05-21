---
name: see-free
description: >
  智谱AI 免费多模态 — 看图理解、AI 绘图、AI 视频。
  以下场景触发：

  图片理解：用户发来图片路径/截图/screenshot、问"看看这张图"、"帮我看看"、"图片里有什么"、
  "这是什么图"、"截图里有什么"、"读一下这张图"、"分析这张图"、"识别图片"、"提取图中文字"、
  "这张图讲了什么"、"这个UI/设计怎么样"、"图表数据是什么"、"对比这两张图"。

  AI 绘图："画一张"、"帮我画"、"生成图片"、"设计一个"、"做个图"、"生成海报/logo/封面"、
  "帮我做张图"、描述画面后要求画出来。

  AI 视频："生成视频"、"做个视频"、"帮我做个动画/视频"、"文生视频"、"图生视频"。

  不触发：纯文字对话、抽象讨论、不涉及任何视觉内容的请求（如"你觉得呢"）。
---

# 智谱AI 视觉 Skill v3

用智谱 AI 开放平台的免费模型补 deepseek 缺失的视觉能力。

**免费模型**（永久免费）：
| 能力 | 模型 | 说明 |
|------|------|------|
| 图片理解（通用） | `glm-4v-flash` | 速度快，128K 上下文 |
| 图片理解（分析） | `glm-4.1v-thinking-flash` | 思维链推理，适合图表/逻辑分析 |
| AI 绘图 | `cogview-3-flash` | 文生图 |
| AI 视频 | `cogvideox-flash` | 文生视频，异步提交 |

## 前置条件

首次使用前，用户需要注册并获取 API Key：
1. 访问 https://bigmodel.cn 注册登录（需要实名认证）
2. 进入控制台 → API Key → 创建新 Key → 复制
3. 写入 `~/.claude/skills/glm-vision/.env`：
   ```
   ZHIPU_API_KEY=你的key
   ```
   或设置环境变量 `ZHIPU_API_KEY`

如果用户说还没注册或没有 Key，引导用户完成上述步骤。

## 脚本命令

```bash
# ========== 视觉对话（推荐）==========
# 进入交互式视觉对话模式
python ~/.claude/skills/glm-vision/scripts/glm.py chat <图片路径或URL>

# 例：丢一张图，然后像聊天一样追问
python ~/.claude/skills/glm-vision/scripts/glm.py chat 截图.png
python ~/.claude/skills/glm-vision/scripts/glm.py chat https://example.com/pic.jpg

# 在对话中，问题含"分析/评价/对比"等词 → 自动用思维链模型
# 输入 exit 退出

# ========== 单次图片理解 ==========
python ~/.claude/skills/glm-vision/scripts/glm.py vision <路径或URL>
python ~/.claude/skills/glm-vision/scripts/glm.py vision <路径或URL> -q 帮我分析一下这个UI设计
python ~/.claude/skills/glm-vision/scripts/glm.py vision <路径或URL> -q 分析这张财报图表 --thinking
python ~/.claude/skills/glm-vision/scripts/glm.py vision a.png b.png -q 对比这两张截图

# ========== AI 绘图 ==========
python ~/.claude/skills/glm-vision/scripts/glm.py draw "描述文本"
python ~/.claude/skills/glm-vision/scripts/glm.py draw "描述" [输出路径] --size 720x1280 --enhance

# ========== AI 视频（一站式：自动提交 → 轮询 → 下载打开）==========
python ~/.claude/skills/glm-vision/scripts/glm.py video "描述"
python ~/.claude/skills/glm-vision/scripts/glm.py video "描述" --image 参考图.png

# ========== AI 视频（手动分步）==========
python ~/.claude/skills/glm-vision/scripts/glm.py video-submit "描述"
python ~/.claude/skills/glm-vision/scripts/glm.py video-poll <task_id>
python ~/.claude/skills/glm-vision/scripts/glm.py video-download <url> [输出路径]
```

### 关于 --

* `--enhance`: 自动追加质量关键词，适合 prompt 较短时
* `--size`: 1024x1024（方图）| 1280x720（横版）| 720x1280（竖版）
* `--open`: 生成后弹出文件管理器定位到文件（Windows）
* `--thinking`: 强制用思维链模型（不设则自动检测）
* URL 支持: vision 和 chat 接受 HTTP/HTTPS 图片链接
* 图片已默认去除 AI 水印

## 视觉记忆缓存

本 skill 使用**会话级视觉记忆**来提升多轮对话效率：

1. **首次看图**：调用 `vision` 或 `chat`，完整结果存入视觉记忆
2. **用户追问**：
   - 如果记忆中有足够信息回答 → **不调智谱**，直接基于记忆用 deepseek 回答
   - 如果记忆不足（用户问的视觉细节记忆里没有，如空间关系、特定元素）→ 再次调 vision，用更聚焦的问题
3. **换图或新话题** → 重新调 vision，更新记忆
4. **会话结束** → 记忆自动清除

在回答中标注信息来源：
- 直接来自智谱视觉 → `**[智谱视觉]**`
- 基于记忆 + deepseek 推理 → `**[分析]**`
- 最终答案始终展示给用户

## 路由规则

根据用户问题类型和复杂度自动选择最优路径：

**纯描述/识别** — 智谱直出（glm-4v-flash）：
- "图里有什么"、"这是什么东西"、"帮我看看这张截图"
- 标注 `**[智谱视觉]**`

**分析/推理/对比** — 思维链模型（glm-4.1v-thinking-flash）：
- "分析这个图表"、"这个 UI 有什么问题"、"对比这两张截图"
- chat 模式下自动检测问题意图，含"分析/评价/对比/为什么"等词自动切换
- 标注 `**[智谱分析]**`

**AI 绘图**：
- prompt 短时加 `--enhance` 提升质量
- 竖向图加 `--size 720x1280`，横向图 `--size 1280x720`

**AI 视频** — 一站式 `video` 命令（内置自动重试、轮询、下载打开）：
- 负载高时自动等 10s→30s→60s→120s→120s 重试提交
- 提交成功后每 15s 轮询，最长等 15 分钟
- 生成完成自动下载并用默认播放器打开

## 输出格式

```
**[智谱视觉]** 这是一张电商后台的订单详情页截图。页面顶部显示订单号...

**[智谱分析]** 这张图表显示了 Q1-Q4 的销售趋势。通过思维链分析：1) 全年增长...

**[分析]** 根据之前看到的截图数据，订单金额为 ¥2,580，共 3 件商品...
```

绘图/视频：
```
已生成图片，保存到 `C:\free\glm-output\image_xxx.png`
提示词：xxx
尺寸：1024×1024
```

## 错误处理

- API Key 未设置 → 引导用户去 bigmodel.cn 注册 → 写入 .env
- 图片路径不存在或 URL 无效 → 请用户确认
- API 429/5xx → 自动重试（最多 4 次，指数退避）
- 内容审核拦截 → 提示用户调整提示词
- 视频失败（VIDEO_FAILED）→ 告知用户重新提交
