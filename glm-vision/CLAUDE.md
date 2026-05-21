# glm-vision — 智谱 AI 视觉 Skill

## 项目说明

智谱 AI 免费多模态模型的 Claude Code Skill，提供图片理解、AI 绘图、AI 视频能力。

## 目录结构

```
glm-vision/
├── SKILL.md          # Skill 定义（安装到 ~/.claude/skills/ 后生效）
├── scripts/
│   └── glm.py        # CLI 工具
├── docs/
│   └── v2-design.md  # 设计文档
├── .env              # API Key（已 gitignore）
└── glm-output/       # 生成的图片/视频输出（已 gitignore）
```

## 开发约定

- **SKILL.md** 中的路径用 `~/skills/glm-vision/`，这是安装到 `~/.claude/skills/` 后的目标路径
- 开发时直接在 `C:\free\skills\glm-vision\` 下操作，用绝对路径或相对路径调用
- 不改 `.env` 的路径引用逻辑（`load_key()` 已自动从脚本上级目录加载）

## 开发命令

```bash
# 开发时调用（scripts/ 目录下）
python scripts/glm.py vision <图片路径> -q "问题"
python scripts/glm.py chat <图片路径>
python scripts/glm.py draw "描述" --enhance
```

## 生成类任务规则

- `draw`（绘图）、`video`（视频）等生成类任务一律后台运行
- 用户只需要提出需求，不需要等待
- 生成完成后自动用默认程序打开文件并通知用户

## 提交前检查

- [ ] `python scripts/glm.py --help` 能正常输出
- [ ] 两种模型调用至少验证一种可用
- [ ] `.env` 不被提交
