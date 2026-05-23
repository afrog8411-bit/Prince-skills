# v5 设计批判

## 审查项

### 1. `_req_paid()` vs 合并到 `_req()`

**批判**：增加一个独立函数多出 ~40 行代码重复（URL 构造、异常处理、安全审核）。

**裁决**：保留独立函数。
- 理由：免费 key 走调度器（多 key、RR、冷却），付费 key 直接单 key 重试——底层逻辑完全不同，硬合并会增加 lambda/分支复杂度，可读性反而下降
- 40 行重复是合理的 DRY 边界

### 2. `--thinking` 参数保留

**批判**：GLM-5V-Turbo 本身就是视觉旗舰，不再需要 "是否用 thinking 模型" 的切换。保留一个 no-op 参数增加迷惑性。

**裁决**：**砍掉**。
- 旧 `--thinking` 是在免费模型之间做选择（glm-4v-flash ≈ 快 vs thinking-flash ≈ 深）
- 升到 GLM-5V-Turbo 后，模型本身就兼具速度和深度，参数无意义
- 移除 argparse 中的 `--thinking`，但 CLI 不报错（通过 `parse_known_args` 或放宽容忍）

**实际处理**：不报错即可，argparse 默认会报 unknown argument。加 `allow_abbrev=True` 不够。
改为：不显式移除 flag，但在 do_vision 中忽略该参数。
最终：简单处理——保留 argparse 定义但注释里写 "已废弃，仅兼容旧调用"。

### 3. batch-vision 线程安全

**批判**：`_req_paid()` 中 `sys.exit(1)` 在子线程中抛出 `SystemExit`（继承 `BaseException` 而非 `Exception`），`except Exception` 抓不住。

**裁决**：batch 处理层需要 `except BaseException` 或 `except (Exception, SystemExit)` 来捕获。

### 4. 付费 key 重试策略

**批判**：6 次重试（最长 61s）对于付费 API 来说是否过长？普通网络问题 4 次（15s）足够。

**裁决**：改为 5 次（1+2+4+8+16=31s），与免费 key 持平但少一次。付费 API 稳定性应该更好。

### 5. 付费 key 未配置时回退

**批判**：无回退机制，少一个容错路径。

**裁决**：不加回退。Prince 明确要付费方案，fallback 到免费模型违背意图。

### 6. CLAUDE.md 更新

**批判**：漏了，开发目录的 CLAUDE.md 需要更新 v5 相关信息。

**裁决**：补上。简短的版本记录和新增环境变量说明。

## 精简后改动清单

### glm.py
1. 新增 `load_paid_key()` — 加载单 key
2. 新增 `_req_paid()` — 付费请求，5 次重试
3. 修改 `_call_model()` — 加 `paid` 参数
4. 修改 `do_vision()` — 用 glm-5v-turbo + paid，保留 `--thinking` 但忽略
5. 修改 `do_chat()` — 同上
6. 修改 `do_batch_vision()` — 线程池直调 + BaseException 捕获
7. 其余不变

### SKILL.md
1. 模型表 + GLM-5V-Turbo
2. Key 配置 + ZHIPU_API_KEY_PAID
3. 命令表更新

### .env
1. + ZHIPU_API_KEY_PAID

### CLAUDE.md
1. + 版本号、新 env var
