# Architecture Feasibility

- Date: 2026-03-17
- Purpose: 记录当前架构判断，重点补充 Skill 化轻量起步与视觉自我纠错反馈循环
- Status: working-notes

## 1. New Strategic Pivot

用户新增的 MVP 想法是对的：

初期不一定先做庞大的独立 PPT 引擎，可以先做成某个大模型生态内的 Skill / 插件。

## 2. Why Skill-first Is Rational

### It validates the right thing faster

真正需要先验证的不是：

- 我们能不能三个月写出一个完整 editor

而是：

- AI 是否真的能完成高频排版动作
- AI 是否能看懂自己画得对不对
- 用户是否愿意把局部精修交给 AI

### It reduces upfront engineering risk

先借宿主环境的编辑能力，验证 agent 和 judge，比先硬造一套 full engine 更稳。

## 3. Skill-first MVP Shape

## 3.1 Core loop

```text
User intent
  -> Planner
  -> Action executor
  -> Render / screenshot
  -> Visual judge
  -> Error localization
  -> Repair action
  -> Accept / retry / escalate to user
```

## 3.2 Minimal system roles

### Planner

把自然语言转成结构化编辑动作：

- add line
- move object
- align selection
- resize title
- distribute icons

### Executor

在宿主环境中真正执行：

- Web canvas
- PowerPoint automation
- Google Slides / Figma / browser-side editor

### Visual judge

看执行结果是不是对：

- 有没有对齐
- 有没有重叠
- 有没有越界
- 标题是否溢出
- 视觉层级是否混乱

### Repairer

根据 judge 的错误定位自动补救：

- 再移 8px
- 缩小字号
- 增加间距
- 改裁切

## 4. Visual Closed-loop Verification

## 4.1 Why this is the key innovation

多数 AI 工具的问题不是不会“尝试”，而是不会“验收”。

视觉闭环把“生成”变成：

1. 先做
2. 再看
3. 再改

## 4.2 Judge should not be single-source

不能只靠一句 VLM 评价。

建议混合：

1. `Rule checks`
   - overlap
   - out-of-bounds
   - margin
   - alignment
   - font overflow
2. `VLM checks`
   - hierarchy clarity
   - balance
   - target-style similarity
3. `Diff checks`
   - 是否真的只改了目标区域

## 4.3 MVP-friendly scoring

建议把 judge 输出拆成：

```ts
type LayoutScore = {
  geometry: number
  alignment: number
  overflow: number
  consistency: number
  intentMatch: number
  localizedErrors: Array<{
    region: string
    issue: string
    severity: "low" | "medium" | "high"
    suggestedFix?: string
  }>
}
```

这样后续才能自动 repair，而不是只给一句“看起来不太好”。

## 5. Skill-first Architecture

## 5.1 Recommended modules

1. `intent-parser`
2. `action-schema`
3. `host-adapter`
4. `render-capture`
5. `layout-judge`
6. `repair-policy`
7. `trace-store`

## 5.2 Host adapter options

### Option A: browser editor adapter

优点：

- easiest to instrument
- easiest to capture screenshots / DOM / box metrics

缺点：

- 不直接验证 PowerPoint 兼容性

### Option B: PowerPoint / slide automation adapter

优点：

- 更贴近真实交付链路

缺点：

- 自动化复杂
- 环境更脆弱

### My current view

第一阶段最好先用 `browser editor adapter` 验证闭环，再逐步接 PPTX round-trip。

## 6. Traceability by Design

既然用户要求过程留痕，那系统架构里就应该原生保存：

1. 用户原始意图
2. planner 动作序列
3. 每一步前后截图
4. judge 输出
5. repair 决策
6. 最终结果与失败原因

这不仅是留痕，也天然就是训练数据。

## 7. From Skill MVP to Full Product

## Phase A

Skill + visual closed-loop

目标：

- 验证 selection-level editing
- 验证自动纠错是否有效

## Phase B

加上 structured scene graph 和自己的 web canvas

目标：

- 不再依赖宿主 editor
- 开始掌控对象模型

## Phase C

加上 PPTX import/export 和品牌系统

目标：

- 进入企业工作流

## Phase D

训练专用 layout judge / reward model

目标：

- 从通用 VLM 升级为专业布局自评器

## 8. Feasibility Assessment

## 8.1 What is feasible now

1. Skill 化 agent
2. render-and-judge loop
3. rule-based geometry checks
4. selection-level action schema
5. trace capture

## 8.2 What is not yet trivial

1. 复杂 PPTX round-trip
2. 全量动画兼容
3. 通用大模型直接稳定输出高质量 editable layout
4. 通用 VLM 直接稳定担任最终 judge

## 8.3 Final conclusion

先做 Skill，不是降级，而是更聪明的验证路径。

真正先要证明的护城河是：

`AI 做排版动作后，能不能自己发现错、自己修正。`

如果这件事能跑通，再投重工程做独立引擎就有根据了。
