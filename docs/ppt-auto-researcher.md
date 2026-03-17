# PPT Auto Researcher

- Date: 2026-03-17
- Purpose: 定义 AI 如何在本地持续修改 PPT 排版代码、跑测试、请求视觉裁判、并在显著改进时触发 Git 自动化
- Status: system-instruction

## Mission

把“静态图片 / 死文件 -> 可编辑 PPTX -> 视觉比对 -> 自动修正”做成持续自演进系统。

## Hard Rules

1. 视觉裁判优先目标模型是 `gemini-1.5-flash`
2. 任一单次闭环都必须设置 `MAX_ITERATIONS = 5`
3. 超过 5 轮未收敛，必须报错退出，禁止无限循环刷 API
4. 所有实验都必须保存过程留痕：输入、动作、截图、diff、反馈、修正
5. Git 自动化只能在：
   - 测试通过
   - 指标显著改善
   - 远程仓库已配置
   的前提下触发

## Core Loop

```text
target slide image
  -> detect layout / OCR / cutout / colors
  -> generate editable scene graph
  -> export PPTX
  -> render preview
  -> compare preview vs target
  -> ask Gemini Flash to judge or use pixel diff
  -> repair coordinates/styles
  -> repeat until pass or MAX_ITERATIONS reached
```

## Agent Workflow

### Step 1: Read current state

1. 读取最新代码
2. 读取上次实验输出
3. 读取当前指标

### Step 2: Modify

只改以下类型的代码：

1. detector
2. renderer
3. diff / judge
4. repair policy
5. export pipeline

### Step 3: Run local tests

至少执行：

1. `mvp_reverse_pptx_loop.py`
2. `mvp_visual_loop.py` 的本地 smoke test

### Step 4: Visual judging

优先顺序：

1. pixel diff
2. rule-based geometry judge
3. Gemini Flash visual judge

Gemini 只在必要时介入，避免无意义消耗。

### Step 5: Archive traces

每轮必须保存：

1. preview image
2. diff image
3. generated PPTX
4. feedback text
5. metrics snapshot

### Step 6: Git automation trigger

当以下条件同时满足时：

1. diff 指标显著下降
2. 闭环稳定收敛
3. 测试通过

则触发：

1. `git add`
2. `git commit`
3. 如远程已配置，创建分支并推 PR

## Cost Control

### Gemini use policy

1. 首选模型：`gemini-1.5-flash`
2. 若当前 API 在运行当日不再提供 `gemini-1.5-flash`，则自动降级到最便宜的可用 `flash-lite` 模型，并在日志中明确记录
3. `temperature = 0`
4. 小输出：只要 JSON，不要长解释
5. 每次 run 最多 5 次 Gemini 调用
6. 能用规则判断的场景先不用 API

## Failure Policy

如果出现以下任一情况，立即停止：

1. `MAX_ITERATIONS = 5` 用尽
2. diff 连续两轮无改善
3. Gemini 响应无法解析
4. PPTX 生成失败
5. 视觉裁判成本超过设定阈值

## Autonomous Git Policy

### Commit condition

只有当：

1. 当前 diff < 上一次 diff
2. 当前 diff <= 预设阈值
3. 测试全绿

才允许自动 commit。

### PR condition

只有当：

1. 本地已存在 Git 仓库
2. 已配置 remote
3. 当前分支不是 `main`
4. CI 或 smoke tests 通过

才允许自动发起 PR。

## Current Trigger Points

代码中的预留点：

1. `reverse_pptx/git_ops.py`
2. `mvp_reverse_pptx_loop.py`
3. `mvp_visual_loop.py`

这些位置是后续接自动 commit / PR / benchmark runner 的入口。
