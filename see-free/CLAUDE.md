# glm-vision — 智谱 AI 视觉 Skill v5

## 项目说明

智谱 AI 多模态模型的 Claude Code Skill。**视觉识别走付费 GLM-5V-Turbo**，绘图/视频走免费模型。

## 目录结构

```
glm-vision/
├── SKILL.md          # Skill 定义（安装到 ~/.claude/skills/ 后生效）
├── scripts/
│   └── glm.py        # CLI 工具
├── docs/
│   ├── v2-design.md  # v2 设计文档
│   └── v5-design.md  # v5 设计文档
├── .env              # API Key（已 gitignore）
└── glm-output/       # 生成的图片/视频输出（已 gitignore）
```

## 环境变量

| 变量 | 用途 |
|------|------|
| `ZHIPU_API_KEY` / `_2` / `_3` … | 免费模型（draw/video） |
| `ZHIPU_API_KEY_PAID` | 付费视觉（vision/chat，GLM-5V-Turbo） |

## 开发约定

- **SKILL.md** 中的路径用 `~/.claude/skills/see-free/`，这是安装到 `~/.claude/skills/` 后的目标路径
- 改完验证后复制到 `~/.claude/skills/see-free/` 部署
- 不改 `.env` 的路径引用逻辑（各函数自动从脚本上级目录加载）

## 开发命令

```bash
# 开发时调用（scripts/ 目录下）
python scripts/glm.py vision <图片路径> -q "问题"
python scripts/glm.py chat <图片路径>
python scripts/glm.py draw "描述" --enhance
python scripts/glm.py keys
```

## 生成类任务规则

- `draw`（绘图）、`video`（视频）等生成类任务一律后台运行
- 用户只需要提出需求，不需要等待
- 生成完成后自动用默认程序打开文件并通知用户

## 提交前检查

- [ ] `python scripts/glm.py --help` 能正常输出
- [ ] `python scripts/glm.py keys` 显示付费 + 免费 Key 状态
- [ ] vision/chat 两种模型至少验证一种可用
- [ ] `.env` 不被提交
