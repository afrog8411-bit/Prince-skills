# flash-key 截图粘贴功能设计

## 目标

Alt+A 截图后，Ctrl+V 直接粘贴到终端，不管剪贴板里是什么。

## 方案

在终端窗口中拦截 `Ctrl+V`，检测剪贴板有图片时自动存图并打出路径，否则放行正常粘贴。

## 用户流程

```
Alt+A 截图 → 切到 Claude 终端 → Ctrl+V → 图片路径自动出现 → 回车
```

## 实现

- **快捷键**：`Ctrl+V`（仅在终端窗口中拦截）
- **触发条件**：剪贴板含图片 (CF_BITMAP) + 当前窗口为终端
- **存图路径**：`C:\free\screenshots\yyyy-MM-dd_HHmmss.png`
- **非图片**：完全放行，不走任何额外逻辑
- **依赖**：`scripts/save-clipimg.ps1`（PowerShell 剪贴板存图助手）

## 配置

flash-key 向导新增第五步：

```
Step 5：截图粘贴
  是否需要"截图即贴"功能？
  Alt+A 截图后，在终端 Ctrl+V 自动打出图片路径。
  
  默认开启 | 快捷键：Ctrl+V
```

## 新增文件

- `scripts/save-clipimg.ps1` — 保存剪贴板图片到文件
