---
name: git-commit
description: >
  Git 提交与推送工作流。**主动型**——任务做完有变更时，不等用户开口就分析变更、
  准备提交、写 message。用户说"提交"、"上传"、"commit"、"push"、"同步到 GitHub"、
  "推一下"、"更新仓库"、"同步一下"时触发。
  注意：如果 Claude 刚完成一个产生文件变更的任务，应该主动检查要不要提交，
  而不是等用户下指令。不要 under-trigger。
  不触发：纯 git 命令解释（如"git rebase 是干嘛的"）、不涉及提交的 git 查询。
---

# Git 主动提交 + 智能推送

Skill 不是教你怎么提交——而是让你**少问用户、多干活**。

## 核心原则

1. **主动**：改完了别等用户说，直接查状态准备提交。
2. **少问**：commit message 从 diff 里读，不要问"要写什么 message"。
3. **只问一次**：所有确认浓缩成一句"改好了，可以推吗？"。
4. **留记录**：推完后更新 CLAUDE.md 或会话记忆，记录本次做了什么。

红线（来自全局 CLAUDE.md）：

> **git push 必须问用户**。commit 可以自己做，push 前必须问"可以推吗？"，等确认再推。

## 行为

### 触发时机

- 用户明确说"提交/commit/push/上传/同步/推一下"
- **Claude 刚完成一项修改代码/文档/配置的任务，且 git status 有变更**
- 用户说"改好了"、"差不多了"、"收工"且当前是 git 仓库

### 自动工作流

**① 查变更** —— `git status --short` + `git diff --stat`

**② 读 diff** —— `git diff` 看到底改了啥，理解变更意图，不只看文件名。

**③ 写 message** —— 基于实际 diff 内容生成规范 message：

优先用 feat / fix / refactor / docs / chore：
```
feat(see-free): 1302 限流自动等待 30s 重试
```

> 不用展示给用户确认。除非用户有特别说明（如"这次叫 xxx"）。

**④ 提交** —— `git commit`

**⑤ 问权限** —— 一句话：

> "已提交。可以推送到 GitHub 吗？"

**⑥ 推送** —— 用户回复"可以" → `git push`，回复"不" → 终止。

**⑦ 留痕** —— 推送成功后，更新项目 CLAUDE.md 或会话记录：

```
## 变更日志
- 2026-05-23: see-free v5.1 — 1302 处理、--json、batch 串行化
```

### 异常处理

| 场景 | 怎么做 |
|------|--------|
| 工作区干净 | 告知无需提交，终止 |
| 没有远程仓库 | 提示配置 remote，终止 |
| 分支落后 | 提示先 pull，终止。不自动 pull（怕冲突） |
| 推送被拒 | 提示用户处理，不擅自 rebase/force |
| 用户中途说"算了" | 立即停，不操作 |
| 变更太多/太杂 | 问一次"要拆成多个 commit 吗？"，用户说不用就合 |

## message 生成规范

message 应该反映「**改了啥 + 为什么**」，不是「改了哪些文件」：

```
✓ feat(auth): implement JWT refresh token rotation       # 好的：功能+意图
✓ fix(see-free): 1302 rate limit with 30s cooldown       # 好的：修复+方案
✗ update                                               # 差的：没信息
✗ fix bug                                              # 差的：没说什么 bug
✗ commit changes                                       # 差的：废话
✗ 改了 glm.py 和 SKILL.md                               # 差的：文件名不是 message
```

从 diff 的上下文推断 scope（影响范围），从修改意图推断 type（变更类型）。
