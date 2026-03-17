# AutoResearch PPT Architecture

- Date: 2026-03-17
- Purpose: 把 autoresearch、PPT 产品架构、Skill-first MVP、视觉闭环验证串成一张统一路线图
- Status: draft

## 1. Core Thesis

这个项目不应先被定义为“AI 生成 PPT”。

更准确的定义是：

`一个会研究、会试排版、会看结果、会自己修正的 PPT agent system。`

## 2. Why AutoResearch Matters Here

PPT 不是单一技术问题，它同时涉及：

1. layout generation
2. document layout parsing
3. vector / editable graphics
4. presentation agent planning
5. visual judging / reward modeling

如果没有 autoresearch，架构很容易被某一条局部路线绑死。

## 3. AutoResearch Layer

## 3.1 Responsibilities

1. 用官方 API 持续拉论文元数据
2. 做 triage 和 capability mapping
3. 更新技术路线优先级
4. 反哺产品 backlog

## 3.2 Capability map

每篇论文都应被映射到以下能力之一：

1. `parser`
2. `planner`
3. `renderer`
4. `judge`
5. `repairer`
6. `exporter`
7. `benchmark`

## 3.3 Example

- DesignSense -> `judge`
- DeepPresenter -> `planner + judge loop`
- COVec -> `parser / editable decomposition`
- LayoutPrompter -> `planner + retriever`

## 4. Skill-first MVP Layer

## 4.1 Why first

先证明 agentic loop 能不能跑通，再决定是否重投自研 engine。

## 4.2 System shape

```text
User request
  -> Skill Planner
  -> Host Adapter
  -> Render Capture
  -> Visual Judge
  -> Repair Policy
  -> Retry or Commit
```

## 4.3 Host choices

1. browser canvas editor
2. Figma-like host
3. PowerPoint / Slides automation

当前建议：

先从可控的 browser-side host 开始，快速验证闭环。

## 4.4 New killer feature: reverse decomposition from static slide image

新增的核心突破点不是只“生成 PPT”，而是：

`把一张静态幻灯片图逆向解构成可独立编辑的 PPTX。`

### Target loop

1. 输入目标 slide image
2. 做 layout detection / OCR / cutout / color pickup
3. 反向重建 scene graph
4. 导出 editable PPTX
5. 渲染预览图
6. 与原图做 pixel diff / Gemini 视觉裁判
7. 自动修正坐标和样式
8. 最多迭代 `MAX_ITERATIONS = 5`

### Why this matters

这条能力直接击穿现有 AI PPT 工具的两个大缺陷：

1. 漂亮结果经常是死图，不可编辑
2. 模板化生成太死，不够像参考图

## 5. Visual Closed-loop Layer

## 5.1 Inputs

1. rendered screenshot
2. object coordinates
3. current intent
4. previous failures

## 5.2 Judges

### Rule judge

负责：

- overlap
- out-of-bounds
- center alignment
- overflow

### VLM judge

负责：

- visual hierarchy
- semantic match
- style consistency

### Future learned judge

来自：

- DesignSense 类 reward model
- 自己积累的 trace data

### Cost control

视觉 API 强制固定：

- preferred model: `gemini-1.5-flash`
- if unavailable on the current API date, downgrade to the cheapest available `flash-lite` model and log it
- hard stop: `MAX_ITERATIONS = 5`
- no infinite retry

## 5.3 Repair policy

不是“重新整页生成”，而是：

1. 定位问题区域
2. 推导最小修正动作
3. 执行并复检

## 6. Full Product Evolution

## Phase A

AutoResearch + Skill MVP + trace store

### Goal

验证：

- 真实高频排版动作
- 视觉闭环纠错
- 用户接受度

## Phase B

Scene graph + web editor

### Goal

掌控对象模型与局部编辑

## Phase C

PPTX round-trip + brand system

### Goal

接入企业真实工作流

## Phase D

Dedicated layout judge / reward model

### Goal

从通用 VLM 升级为专业视觉验收器

## 7. Traceability Architecture

要求过程留痕，就不能只把留痕当“文档习惯”，而要把它做进系统。

### For every run, store:

1. user intent
2. planner actions
3. before screenshot
4. after screenshot
5. judge result
6. repair action
7. final acceptance state

这同时也是未来训练 judge 和 repair policy 的核心数据集。

## 8. Immediate Implementation Recommendation

现在最该做的不是：

- 训练一个大而全的 layout model

而是：

1. 固化 action schema
2. 固化 screenshot-based judge interface
3. 固化 trace format
4. 用小任务验证闭环能否稳定收敛
5. 立刻做 image-to-editable-PPTX 的最小 reverse loop

`mvp_visual_loop.py` 和 `mvp_reverse_pptx_loop.py` 是这条路线的两个最小原型。

## 9. Final Judgment

AutoResearch 不是附属功能，而是架构的一层。

因为这个产品的核心竞争力不会只是“生成能力”，而是：

`研究 -> 规划 -> 执行 -> 观察 -> 修正 -> 归档`

这一整条 agentic system。
