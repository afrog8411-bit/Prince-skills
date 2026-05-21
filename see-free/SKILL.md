---
name: see-free
description: >
  智谱AI 免费多模态 — 看图理解、AI 绘图、AI 视频、多 Key 并行批处理。
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

# 智谱AI 视觉 Skill v4 — 多 Key 智能调度 + 并行批处理

用智谱 AI 开放平台的免费模型补 deepseek 缺失的视觉能力。

**免费模型**（永久免费）：
| 能力 | 模型 | 说明 |
|------|------|------|
| 图片理解（通用） | `glm-4v-flash` | 速度快，128K 上下文 |
| 图片理解（分析） | `glm-4.1v-thinking-flash` | 思维链推理，适合图表/逻辑分析 |
| AI 绘图 | `cogview-3-flash` | 文生图 |
| AI 视频 | `cogvideox-flash` | 文生视频，异步提交 |

## 前置条件：首次使用引导

用户第一次触发图片理解/AI 绘图/AI 视频时，如果发现 API Key 未配置，按以下流程引导用户完成设置，一步都不能跳：

```
发现没有 ZHIPU_API_KEY → 主动询问"要先注册智谱获取免费 API Key，要现在弄吗？"
→ 用户同意 → 给出以下步骤：
```

**步骤 1：注册智谱**
- 打开 https://bigmodel.cn → 点击右上角「注册」
- 支持手机号或邮箱注册
- **需要实名认证**（身份证 + 人脸识别），约 2 分钟完成
- 建议用**手机号注册多个账号**（一个手机号可绑多个账号），后续可配置多个 Key 实现并行加速

**步骤 2：创建 API Key**
- 登录后进入「控制台」→ 左侧「API Key」→ 「添加 API Key」
- 随便起个名字（如 "claude-code"）
- 复制生成的 Key（一串以 `xxx.` 开头的字符串）
- **如果注册了多个账号**，每个账号登录后都创建一次 Key

**步骤 3：配置到本地**
- 把 Key 写入 `~/.claude/skills/see-free/.env`：

  **一个 Key（够用）：**
  ```
  ZHIPU_API_KEY=你刚才复制的key
  ```
  **多个 Key（推荐，可并行加速）：**
  ```
  ZHIPU_API_KEY=第一个账号的key
  ZHIPU_API_KEY_2=第二个账号的key
  ZHIPU_API_KEY_3=第三个账号的key
  # 可以继续加 _4 _5 ... 不限数量
  ```

- 也可以设置系统环境变量（变量名同样为 `ZHIPU_API_KEY` / `ZHIPU_API_KEY_2` ...）
- **单 Key 完全可用**，多 Key 只是在批量生成或高并发时更快
- 配置完成后**不需要重启 Claude Code**，直接再说一次"帮我看这张图"即可

**关于费用**：智谱的 `glm-4v-flash`、`glm-4.1v-thinking-flash` 等模型目前有**免费额度**，日常使用足够，不需要充值。

> 如果用户说"太麻烦了"或"不想注册" → 不要强推，回退为："没关系，那我用文字描述帮你分析，你跟我说说这张图长什么样？"
>
> 如果用户说"一个就够了" → 不强求多注册，单 Key 完全够用。

## 脚本命令

```bash
# ========== 视觉对话（推荐）==========
# 进入交互式视觉对话模式
python ~/.claude/skills/see-free/scripts/glm.py chat <图片路径或URL>

# 例：丢一张图，然后像聊天一样追问
python ~/.claude/skills/see-free/scripts/glm.py chat 截图.png
python ~/.claude/skills/see-free/scripts/glm.py chat https://example.com/pic.jpg

# 在对话中，问题含"分析/评价/对比"等词 → 自动用思维链模型
# 输入 exit 退出

# ========== 单次图片理解 ==========
python ~/.claude/skills/see-free/scripts/glm.py vision <路径或URL>
python ~/.claude/skills/see-free/scripts/glm.py vision <路径或URL> -q 帮我分析一下这个UI设计
python ~/.claude/skills/see-free/scripts/glm.py vision <路径或URL> -q 分析这张财报图表 --thinking
python ~/.claude/skills/see-free/scripts/glm.py vision a.png b.png -q 对比这两张截图

# ========== AI 绘图 ==========
python ~/.claude/skills/see-free/scripts/glm.py draw "描述文本"
python ~/.claude/skills/see-free/scripts/glm.py draw "描述" [输出路径] --size 720x1280 --enhance

# ========== AI 视频（一站式：自动提交 → 轮询 → 下载打开）==========
python ~/.claude/skills/see-free/scripts/glm.py video "描述"
python ~/.claude/skills/see-free/scripts/glm.py video "描述" --image 参考图.png

# ========== AI 视频（手动分步）==========
python ~/.claude/skills/see-free/scripts/glm.py video-submit "描述"
python ~/.claude/skills/see-free/scripts/glm.py video-poll <task_id>
python ~/.claude/skills/see-free/scripts/glm.py video-download <url> [输出路径]

# ========== v4 新命令：并行批量处理 ==========

# 查看所有 API Key 的健康状态
python ~/.claude/skills/see-free/scripts/glm.py keys

# 并行生成多张图片（自动分配不同 Key）
python ~/.claude/skills/see-free/scripts/glm.py batch-draw "prompt1" "prompt2" "prompt3" [--workers 3] [--enhance] [--size 1024x1024]

# 并行理解多张图片
python ~/.claude/skills/see-free/scripts/glm.py batch-vision img1.png img2.png img3.png -q "描述这张图" [--workers 3]

# 从文件读取提示词，逐行生成图片
python ~/.claude/skills/see-free/scripts/glm.py queue prompts.txt [--workers 3] [--enhance]
```

### 选项说明

* `--enhance`: 自动追加质量关键词，适合 prompt 较短时
* `--size`: 1024x1024（方图）| 1280x720（横版）| 720x1280（竖版）
* `--open`: 生成后弹出文件管理器定位到文件（Windows）
* `--thinking`: 强制用思维链模型（不设则自动检测）
* `--workers`: 并行数，默认自动根据健康 Key 数量决定
* URL 支持: vision 和 chat 接受 HTTP/HTTPS 图片链接
* 图片已默认去除 AI 水印

## 多 Key 智能调度（v4）

本 skill 支持**多个 API Key 自动调度**，实现跨账号并发突破：

**配置方式**：在 `.env` 或环境变量中设置多个 Key：
```
ZHIPU_API_KEY=xxx
ZHIPU_API_KEY_2=xxx
ZHIPU_API_KEY_3=xxx
```

**工作原理**：
- 所有 Key 自动加载，round-robin 轮流使用
- 某个 Key 遇到 429 限流时，自动冷却 30s，切换到其他 Key
- 健康状态跨进程持久化（`.key_state.json`），多个命令之间共享冷却信息
- `batch-*` 命令自动根据健康 Key 数量调节并行数

**适用场景**：
- 批量生成图片时，不同 Key 可以同时发请求，突破单账号并发限制
- 一个 Key 被限流时，自动切换到其他 Key，不影响使用
- 建议 3-5 个 Key 性价比最高，再多收益递减

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
- 多张图请求 → 自动用 `batch-draw` 并行生成

**批量/队列**：
- "一次生成多张图"、"批量生成" → 用 `batch-draw` 或 `queue`
- 用户给一个文件说"每行生成一张" → 用 `queue`
- "一次性理解这些图"、"批量分析" → 用 `batch-vision`

**AI 视频** — 一站式 `video` 命令：
- 负载高时自动等 10s→30s→60s→120s→120s 重试提交
- 提交成功后每 15s 轮询，最长等 15 分钟
- 生成完成自动下载并用默认播放器打开
- **多 Key 对视频模型无效**（限速在模型层面），耐心等重试即可

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

批量：
```
✅ prompt1 → IMAGE_SAVED:path1.png
✅ prompt2 → IMAGE_SAVED:path2.png
```

## 错误处理

- API Key 未设置 → 走上方「前置条件」全流程引导
- 图片路径不存在或 URL 无效 → 请用户确认
- API 429/5xx → 自动切换下一个 Key 重试，全部失败后指数退避
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
