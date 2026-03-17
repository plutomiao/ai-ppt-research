# Competitive Analysis

- Date: 2026-03-17
- Purpose: 保存竞品阶段分析，明确哪些产品解决了什么，哪些关键问题仍未解决
- Status: working-notes

## Stage Goal

回答三个问题：

1. 现有 AI PPT 产品到底强在哪
2. 为什么它们没有真正接住企业级 PPT 工作流
3. 我们应该绕开什么伪需求

## Market Split

### 1. AI-first 出稿工具

- Gamma
- Tome（已 sunset）

### 2. 协作型 slides 工具

- Pitch
- Figma Slides
- Canva

### 3. 开源底座

- PPTist
- Presenton
- AiPPT
- Marp
- Slidev
- PptxGenJS
- pptx-automizer

## Product Notes

## Gamma

### Strong

- 从空白页到初稿很快
- card 化体验对非设计用户友好
- 主题化、语言转换、叙事包装顺手

### Weak

- 导入旧 PPT / Doc 时只真正接住 text，不接住原 layout
- card/block 系统限制了对象级编辑
- AI 偏文案改写，不是精准布局编辑
- 导出 PowerPoint 仍有 unsupported elements

### Stage Judgment

Gamma 更像“智能卡片生成器”，不是“可长期维护的 PPT 工作台”。

## Tome

### Strong

- 很早验证了 AI 讲故事、文档转 slides、现代视觉页的需求

### Weak

- 2025-04-30 已 sunset
- 历史能力也没有走到可编辑 PPTX 工作流

### Stage Judgment

可当作产品史参考，不应再当现役竞品。

## Pitch

### Strong

- 协作成熟
- 模板 / 品牌资产能力好
- 正在持续补强 guides、layers、shrink-to-fit 等精细编辑能力
- 比大多数 AI-first 工具更接近真实企业需求

### Weak

- import/export PPTX 仍有明显兼容边界
- AI 仍主要是起稿和局部加速，不是 selection-level intelligent editing

### Stage Judgment

Pitch 是最像“工作台”的闭源对手之一，但仍没彻底解决 round-trip fidelity 和对象级 AI 编辑。

## Figma Slides

### Strong

- 设计模式、图层、Auto Layout、协作都强
- 对设计团队很友好

### Weak

- PPTX import/export 都有明显信息损失
- 更偏 Figma 生态，不是 PowerPoint 存量世界的第一选择

### Stage Judgment

Figma Slides 证明“精细编辑能力”必须有，但也证明“设计强”不等于“PPT 兼容强”。

## Canva

### Strong

- 模板和资产生态极强
- Magic Design 适合快速给出候选版式
- 大量用户已接受其创作工作流

### Weak

- 本质仍偏模板推荐与人工继续编辑
- 对复杂旧 deck 的结构继承和精修并不突出

### Stage Judgment

Canva 适合大众快速出图，不是高保真 PPTX round-trip 引擎。

## PPTist

### Strong

- 开源里最像在线 PowerPoint 编辑器
- 元素级编辑能力强
- 很适合研究浏览器内 slide editor 的交互模型

### Weak

- 更像底层引擎而不是成熟 SaaS
- 商业化和文档成熟度都要自己补

### Stage Judgment

PPTist 是“编辑器底座候选”，不是直接可卖产品。

## Presenton

### Strong

- AI 生成、模板、私有化、API 路线完整
- 重视从已有 PPTX 抽模板

### Weak

- 编辑能力仍偏 schema/template，不是自由画布
- 官方自己也承认 elaborate editing tools 不足

### Stage Judgment

Presenton 是“AI 出稿引擎候选”，不是“人类天天精修 deck 的工作台”。

## AiPPT

### Strong

- 很明确地押注 PPTX <-> JSON <-> PPTX
- 在线编辑、复杂解析、反渲染这条路线是对的

### Weak

- OSS 更像 capability demo
- 企业级核心能力不完全开源

### Stage Judgment

方向非常对，但产品完整度不足。

## What Existing Products Still Miss

### Missing #1: Existing deck round-trip

绝大多数产品对“导入已有 deck -> 局部修改 -> 再导出”都不够强。

### Missing #2: Selection-level editing

很多产品能“改一页”，不能“改这一个对象”。

### Missing #3: Global rules + local exceptions

品牌统一和局部例外之间缺少优雅机制。

### Missing #4: Visual self-check

现有产品通常是生成后让人自己看。很少有产品把“自动生成 -> 自动视觉检查 -> 自动修正”做成主流程。

## Strategic Decision from This Stage

### We should not start with:

- 纯 prompt 生成新 deck
- 纯模板市场
- 纯 Markdown 演示

### We should start with:

1. 让系统接住旧 PPTX / slide image / template
2. 强化元素级编辑
3. 强化 AI 的视觉闭环纠错
4. 保留导出到 PPTX 的现实兼容性

## Immediate Product Hypothesis

最有机会的不是“比 Gamma 更会出稿”，而是：

`比现有工具更会接旧 deck、更会精修、更会自我发现排版错误。`
