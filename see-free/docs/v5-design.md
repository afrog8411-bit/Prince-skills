# see-free v5：付费视觉升级

## 目标

视觉识别从免费模型升级为智谱 `glm-5v-turbo`（付费），提升识别精度。绘图/视频保持免费模型不变。

## 架构变更

### Key 管理

```
当前（v4）：                        v5：
ZHIPU_API_KEY      →  free pool    ZHIPU_API_KEY       →  free pool  (绘图/视频)
ZHIPU_API_KEY_2    →  free pool    ZHIPU_API_KEY_2     →  free pool
ZHIPU_API_KEY_3    →  free pool    ZHIPU_API_KEY_3     →  free pool
                                    ZHIPU_API_KEY_PAID  →  single key (视觉)
```

两个独立的 key 来源，互不干扰：
- **免费池**：现有 KeyScheduler + `.key_state.json`，用于 draw/video
- **付费单 key**：直接使用，无调度开销，简单重试，用于 vision/chat/batch-vision

### 模型路由

| 命令 | v4 模型 | v5 模型 | Key 源 |
|------|---------|---------|--------|
| vision | glm-4v-flash / thinking-flash | **glm-5v-turbo** | 付费 |
| chat | 同上 | **glm-5v-turbo** | 付费 |
| batch-vision | 同上 | **glm-5v-turbo** | 付费 |
| draw | cogview-3-flash | 不变 | 免费 |
| video / video-submit / video-poll | cogvideox-flash | 不变 | 免费 |
| batch-draw / queue | cogview-3-flash | 不变 | 免费 |
| keys | — | 不变 | — |

### `--thinking` 参数处理

v4 中 `--thinking` 用于在 `glm-4v-flash` 和 `glm-4.1v-thinking-flash` 之间切换。
v5 升到 `glm-5v-turbo` 后，保留该参数但不再切换模型——统一用 `glm-5v-turbo`。

### batch-vision 性能优化

**当前**：每个子进程启动独立 Python 解释器，加载全部代码、读 .env、初始化调度器
→ N 个图片 = N 次 ~100ms 启动开销 + N 次文件读取

**优化后**：线程池直接调用 `do_vision` 内部函数
→ 零启动开销，共享已加载的 key 和模块

## 代码改动清单

### glm.py

1. **新增 `load_paid_key()`**：加载 `ZHIPU_API_KEY_PAID`（环境变量优先，.env 后备）
2. **新增 `_req_paid()`**：付费 API 请求函数
   - 单 key 直连，无调度器
   - 相同内容安全审核逻辑
   - 更长重试（6 次 vs 4 次），因为付费 key 不应轻易放弃
3. **修改 `_call_model()`**：新增 `paid` 参数，paid=True 时调 `_req_paid()`
4. **修改 `do_vision()`**：模型用 `glm-5v-turbo`，传递 paid=True
5. **修改 `do_chat()`**：同上
6. **修改 `do_batch_vision()`**：模型用 `glm-5v-turbo` + paid + **线程池直调**
7. **其他函数**：draw/video/queue/batch-draw 不动

### SKILL.md

1. 模型表格新增 GLM-5V-Turbo
2. Key 配置新增 ZHIPU_API_KEY_PAID 说明
3. 命令参考更新模型名
4. batch 相关更新

### .env

新增一行：
```
ZHIPU_API_KEY_PAID=adbf5e2cff6749c29d6ec20573546601.Cm8cjKX0wgplxNxF
```

## 不做的事

- 不重构 KeyScheduler 的磁盘 IO（对免费 key 影响不大，改动风险大于收益）
- 不拆分 glm.py 多文件（~620 行，还没到拆的时候）
- 不改 draw/video 的任何逻辑
- 不加外部依赖（继续纯标准库）
- 不处理 chat 的多轮 token 优化（GLM-5V-Turbo 价格便宜，保持视觉精度更重要）
