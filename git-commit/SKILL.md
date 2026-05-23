---
name: git-commit
description: >
  Git 提交与推送工作流。当用户说"提交"、"上传"、"commit"、"push"、"同步到 GitHub"、
  "推送到仓库"、"更新仓库"、"提交变更"、"git push"、"同步一下" 或任何涉及
  把代码变更提交并推送到远程仓库的场景时触发。
  注意：即使没有明确说"commit"或"push"，只要用户在代码变更后提到"上传"、"更新"、"同步"，
  也应该触发本 skill。
  不触发：纯 git 命令询问（如"git rebase 是什么意思"）、不涉及提交/推送的 git 操作。
---

# Git Commit & Push 工作流

处理从「代码改好了」到「已推送到远程仓库」的完整流程。

## 核心约束

严格遵守以下红线（来自用户全局 CLAUDE.md）：

> **git push 特别约束**：commit 是本地操作，可以做。但推送到任何远程仓库（GitHub、GitLab 等）
> 之前，必须明确问你"可以推吗？"，等你回复确认。不管这个仓库之前推过多少次、
> 你之前是否允许过——每一次都要问。没有例外。

## 工作流

### Step 1: 检查仓库状态

运行 `git status --short` 和 `git diff --stat`，向用户展示当前变更概览：

```
变更文件：
  modified: src/file1.py (15 insertions, 3 deletions)
  added:    src/file2.py (新文件)
  deleted:  old/config.yml
```

### Step 2: 确认暂存范围

- 如果用户明确说了要提交什么，按用户说的 staging
- 如果没有指定，展示未暂存文件列表，问"要全部提交还是只提交其中一部分？"
- 用户确认后 `git add <files>` 或 `git add -A`

### Step 3: 生成提交信息

运行 `git diff --cached` 查看实际变更，生成规范的 commit message：

```
<type>(<scope>): <简短描述>

<详细说明（如需要）>
```

类型参考：feat / fix / refactor / docs / style / chore / perf / test

**生成后一定要展示给用户确认**，用户可能想修改。确认后再 commit。

### Step 4: 提交

```bash
git commit -m "<title>" -m "<body>"
```

### Step 5: 展示提交结果

```bash
git log --oneline -3      # 展示最近 3 条 commit
git status --short         # 确认工作区干净
```

### Step 6: 询问推送权限

**这一步不可跳过。** 必须明确说：

> "已提交。可以推送到 GitHub 吗？"

用 `git remote -v` 确认远程仓库地址，展示给用户。
等待用户回复确认后再 push。

### Step 7: 推送

```bash
git push origin <branch>
```

推送成功后，展示结果摘要：

```
✅ 已推送到 origin/main
   commit abc1234: feat(auth): implement JWT-based authentication
```

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 没有变更可提交 | 告知用户工作区干净，无需提交 |
| 没有配置远程仓库 | 提示用户先配置 remote，然后终止 |
| 分支落后远程 | 提示先 `git pull` 再推送，或者告知可能需 force push（**必须问用户**） |
| 推送被拒（非快进） | 建议先 pull --rebase，处理冲突后再试 |
| 用户中途改主意 | 任何一步用户说"算了"都立即终止，不做未授权的操作 |

## 提交信息规范

commit message 应该清晰反映变更内容：

- **好的例子**：`feat(api): add rate limiting to chat endpoint` / `fix(see-free): handle 1302 rate limit with 30s cooldown`
- **差的例子**：`update` / `fix bug` / `changes` / `asdf`

如果用户的变更涉及多个不相关的改动，建议拆成多个 commit。
