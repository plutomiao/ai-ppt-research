# arXiv Research Notes

- Date: 2026-03-17
- Source policy: 仅使用 arXiv 官方免费 API `http://export.arxiv.org/api/`
- Purpose: 研究图片转可编辑 PPT 元素、layout generation、agentic reflection，并判断如何接入 autoresearch
- Status: working-notes

## 1. Query Log

以下查询均通过官方 API 拉取：

1. `http://export.arxiv.org/api/query?search_query=all:%22graphic+layout+generation%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending`
2. `http://export.arxiv.org/api/query?search_query=all:%22layout+generation%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending`
3. `http://export.arxiv.org/api/query?search_query=all:%22vector+graphics+generation%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending`
4. `http://export.arxiv.org/api/query?search_query=all:%22image+vectorization%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending`
5. `http://export.arxiv.org/api/query?search_query=all:%22LayoutGPT%22&start=0&max_results=3&sortBy=relevance&sortOrder=descending`
6. `http://export.arxiv.org/api/query?search_query=all:%22LayoutPrompter%22&start=0&max_results=3&sortBy=relevance&sortOrder=descending`
7. `http://export.arxiv.org/api/query?search_query=all:%22PPTAgent%22&start=0&max_results=3&sortBy=relevance&sortOrder=descending`
8. `http://export.arxiv.org/api/query?search_query=all:%22vector+graphics+editing%22&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending`
9. `http://export.arxiv.org/api/query?search_query=all:%22DocLayNet%22&start=0&max_results=3&sortBy=relevance&sortOrder=descending`
10. `http://export.arxiv.org/api/query?search_query=all:%22document+layout+analysis%22&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending`

## 2. Layout Generation: Most Relevant Papers

## 2.1 DesignSense (2026)

- Paper: `DesignSense: A Human Preference Dataset and Reward Modeling Framework for Graphic Layout Generation`
- arXiv: http://arxiv.org/abs/2602.23438v1

### Why it matters

这篇最贴近“视觉闭环验证”。

关键信号：

1. 通用 VLM 对布局偏好判断并不稳定
2. 专门的 layout-aware judge 更可靠
3. 用 reward model 做 RL 或 inference-time selection 都能增益

### Takeaway

我们的“AI 先执行，再自己看一眼是否对齐/是否好看”的思路是对的，但不能只靠通用 VLM，最好训练或蒸馏一个专门的 layout judge。

## 2.2 Sketch-to-Layout (2025)

- Paper: `Sketch-to-Layout: Sketch-Guided Multimodal Layout Generation`
- arXiv: http://arxiv.org/abs/2510.27632v1

### Why it matters

说明“草图/线框约束”是比复杂参数更自然的人机接口。

### Takeaway

Skill MVP 里可以允许用户用简单草图或参考线作为约束，而不一定只靠纯文字。

## 2.3 PosterLLaVA (2024)

- Paper: `PosterLLaVa: Constructing a Unified Multi-modal Layout Generator with LLM`
- arXiv: http://arxiv.org/abs/2406.02884v3

### Why it matters

把 layout generation 直接转成 JSON + visual instruction tuning，并落到 editable SVG poster。

### Takeaway

“先结构化 JSON，再渲染成可编辑图形”这条链路是成熟方向，不应直接让模型吐最终像素。

## 2.4 Graphist (2024)

- Paper: `Graphic Design with Large Multimodal Model`
- arXiv: http://arxiv.org/abs/2404.14368v1

### Why it matters

从 unordered design elements 生成 JSON draft protocol，输出坐标、尺寸、层级。

### Takeaway

PPT 任务同样应该先输出 draft protocol，再由执行器落到画布。

## 2.5 Spot the Error (2024)

- Paper: `Spot the Error: Non-autoregressive Graphic Layout Generation with Wireframe Locator`
- arXiv: http://arxiv.org/abs/2401.16375v1

### Why it matters

这篇非常像视觉自我纠错的原型：它用 rendered wireframe 检测错误 token，并做 iterative refinement。

### Takeaway

视觉闭环里，“把当前 slide 渲染成 wireframe / screenshot，再用判别器找错误区域”是非常值得借的套路。

## 2.6 LayoutGPT (2023)

- Paper: `LayoutGPT: Compositional Visual Planning and Generation with Large Language Models`
- arXiv: http://arxiv.org/abs/2305.15393v2

### Why it matters

证明 LLM 可以做 visual planner，把 text 条件转成 layout。

### Takeaway

LLM 适合做“规划器”，但不应单独承担“最终验证器”。

## 2.7 LayoutPrompter (2023)

- Paper: `LayoutPrompter: Awaken the Design Ability of Large Language Models`
- arXiv: http://arxiv.org/abs/2311.06495v1

### Why it matters

强调三个关键点：

1. serialization
2. exemplar retrieval
3. ranking

### Takeaway

这非常适合接 autoresearch 和检索系统：先找相似版式案例，再让模型生成，再做 ranking。

## 2.8 CAL-RAG (2025)

- Paper: `CAL-RAG: Retrieval-Augmented Multi-Agent Generation for Content-Aware Layout Design`
- arXiv: http://arxiv.org/abs/2506.21934v1

### Why it matters

已经把 retrieval + layout recommender + grader + feedback agent 串起来了。

### Takeaway

这几乎就是我们要的 agentic skeleton，只是要把目标从 poster 扩展到 PPT / slide editing。

## 3. Presentation Agent Papers

## 3.1 PPTAgent (2025)

- Paper: `PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides`
- arXiv: http://arxiv.org/abs/2501.03936v3

### Why it matters

明确提出 presentation generation 不能只看内容，还要看 design 和 coherence；并采用 edit-based workflow。

### Takeaway

“edit-based presentation generation”比“from-scratch 一把生成”更像真实工作流。

## 3.2 DeepPresenter (2026)

- Paper: `DeepPresenter: Environment-Grounded Reflection for Agentic Presentation Generation`
- arXiv: http://arxiv.org/abs/2602.22839v1

### Why it matters

这篇几乎正面命中了用户新增的 MVP 思路：

- 不是只做内部 self-reflection
- 而是基于 rendered slides 做 environment-grounded reflection

### Takeaway

“画出来 -> 看一眼 -> 改一轮”不是拍脑袋，而是已经有前沿论文在同方向推进。

## 4. Image -> Editable Elements / Vectorization

## 4.1 COVec (2025)

- Paper: `Clair Obscur: an Illumination-Aware Method for Real-World Image Vectorization`
- arXiv: http://arxiv.org/abs/2511.20034v2

### Why it matters

目标明确：把 raster image 变成 editable, scalable vector representation，同时提升 editability。

### Takeaway

对“把截图里的图形恢复成可编辑 shape/layer”很有启发，尤其是 layer-aware vectorization。

## 4.2 Illustrator's Depth (2025)

- Paper: `Illustrator's Depth: Monocular Layer Index Prediction for Image Decomposition`
- arXiv: http://arxiv.org/abs/2511.17454v1

### Why it matters

从 raster 预测全局一致的 layer ordering，目标直接就是 editability。

### Takeaway

图片转 PPT 元素，不应只做轮廓提取，还要恢复层级顺序。

## 4.3 SVGen (2025)

- Paper: `SVGen: Interpretable Vector Graphics Generation with Large Language Models`
- arXiv: http://arxiv.org/abs/2508.09168v1

### Why it matters

从自然语言到 SVG，强调 semantic accuracy 和 structural completeness。

### Takeaway

说明让模型直接吐可编辑矢量代码是可行的，但前提是训练数据和结构约束足够强。

## 4.4 VectorEdits (2025)

- Paper: `VectorEdits: A Dataset and Benchmark for Instruction-Based Editing of Vector Graphics`
- arXiv: http://arxiv.org/abs/2506.15903v1

### Why it matters

说明“文本指令改矢量图”已经被正式 benchmark 化，而且 current LLMs still struggle。

### Takeaway

selection-level vector editing 很有价值，但还不能指望纯现成大模型零样本就稳定做好。

## 4.5 Reason-SVG (2025)

- Paper: `Reason-SVG: Hybrid Reward RL for Aha-Moments in Vector Graphics Generation`
- arXiv: http://arxiv.org/abs/2505.24499v1

### Why it matters

引入 Drawing-with-Thought 和 hybrid reward，评估结构有效性、语义一致性、视觉质量。

### Takeaway

“先解释设计意图，再输出结构，再由 reward 检查”很适合我们未来训练专用 Skill agent。

## 4.6 SVGEditBench V2 (2025)

- Paper: `SVGEditBench V2: A Benchmark for Instruction-based SVG Editing`
- arXiv: http://arxiv.org/abs/2502.19453v1

### Why it matters

结论很直白：当前方法在 SVG editing 上还有 massive room for improvement。

### Takeaway

这再次说明 MVP 应该先做闭环验证，不应假设“模型一次就画对”。

## 5. Document Layout / Parsing

## 5.1 DocLayNet (2022)

- Paper: `DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis`
- arXiv: http://arxiv.org/abs/2206.01062v1

### Why it matters

图片转可编辑 PPT 元素，第一步往往不是生成，而是 page parsing。

### Takeaway

DocLayNet 是页面元素检测的重要底层数据基础。

## 5.2 GLAM (2023)

- Paper: `A Graphical Approach to Document Layout Analysis`
- arXiv: http://arxiv.org/abs/2308.02051v1

### Why it matters

直接利用 PDF 元数据图结构，而不是把所有页面都当纯图像处理。

### Takeaway

如果输入是原始 PPTX / PDF，不应退化成纯 screenshot pipeline，能用结构元数据就用结构元数据。

## 5.3 PromptDLA (2026)

- Paper: `PromptDLA: A Domain-aware Prompt Document Layout Analysis Framework with Descriptive Knowledge as a Cue`
- arXiv: http://arxiv.org/abs/2603.09414v1

### Why it matters

强调 domain priors 对 layout analysis 很重要。

### Takeaway

PPT 版式解析同样需要 domain-aware cues，不能只拿通用 document parser 硬套。

## 5.4 COTe (2026)

- Paper: `The COTe score: A decomposable framework for evaluating Document Layout Analysis models`
- arXiv: http://arxiv.org/abs/2603.12718v1

### Why it matters

告诉我们：布局解析质量不能只看 IoU / mAP，要看更细的覆盖、重叠、越界、冗余。

### Takeaway

我们自己的视觉闭环评估也应该是 decomposable 的，而不是只给一个模糊总分。

## 6. Synthesis: What This Means for Our Product

## 6.1 The academic consensus is moving toward:

1. 结构化中间表示，而不是端到端像素直接生成
2. 检索增强与 exemplar selection
3. 可视化 judge / reward model
4. iterative refinement
5. environment-grounded reflection

## 6.2 Direct implications for AI PPT

### Image / slide image -> editable elements

建议拆成四步：

1. layout parsing
2. text/OCR + semantic role detection
3. layer decomposition / vectorization
4. scene-graph reconstruction

### Layout generation

建议拆成四步：

1. retrieve similar slide archetypes
2. generate structured draft protocol
3. render
4. judge and revise

## 7. How to Combine with AutoResearch

这里的 “autoresearch” 我按“自动化研究代理 / 检索-阅读-归纳循环”理解；当前目录里没有现成实现，所以先按体系结构定义。

### 7.1 AutoResearch Loop

1. `Retriever`
   - 用 arXiv API 拉官方元数据
2. `Triage`
   - 过滤出与 layout / vector / presentation agent 最相关的论文
3. `Card Writer`
   - 为每篇论文生成结构化 note card
4. `Capability Mapper`
   - 把论文映射到产品能力：parser / planner / judge / renderer / reward
5. `Decision Updater`
   - 更新技术路线优先级

### 7.2 Why this matters

研究不是为了做读书笔记，而是为了不断更新：

- 哪些能力可直接工程化
- 哪些需要训练私有 judge
- 哪些可以只做 Skill MVP 验证

## 8. Final Research Judgment

最值得立刻拿来做 MVP 验证的，不是训练一个 full layout model，而是：

1. 用现成大模型做 planner / executor
2. 用 screenshot / wireframe 做 environment-grounded reflection
3. 用 rule-based + VLM-based judge 混合评分
4. 把修正循环真正跑起来

这条路径和最新 presentation agent、layout judge、vector editing 研究是对齐的。
