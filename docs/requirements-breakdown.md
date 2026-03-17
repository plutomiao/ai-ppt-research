# Requirements Breakdown

- Date: 2026-03-17
- Purpose: 保存需求拆解和优先级判断
- Status: working-notes

## Primary User Segments

1. 咨询 / 战略 / 金融
2. 销售 / 商务 / 市场
3. 教育培训
4. 品牌与企业内宣
5. 设计协作团队

## Core JTBD

### JTBD-1

在公司模板和历史 deck 基础上，快速做客户版 / 行业版 / 英文版。

### JTBD-2

把旧 PPT 拆开重组，不只是换字，而是重写逻辑和重排内容。

### JTBD-3

先让 AI 起草，再由人做最后的专业精修。

### JTBD-4

保证品牌统一，但允许个别页面打破模板。

### JTBD-5

最终交付必须仍然是可继续编辑的 PPTX。

## Pain Breakdown

## P0 Pain

### P0-1 旧 deck 接不住

- 多数场景不是 blank page
- 历史材料多、复用频繁
- 任何只会 from-scratch 的产品都会失分

### P0-2 AI 不会精修

- 会写字
- 不会精确对齐
- 不会可靠地只改局部

### P0-3 导入导出 fidelity 不够

- 字体丢失
- 表格图表丢失
- 动画 / 视频 / 页眉页脚丢失
- 最终还要人工补坑

### P0-4 模板太死

- 全局风格重要
- 局部例外也重要
- 现有工具通常只能二选一

## P1 Pain

### P1-1 版本管理差

- 一稿多用常见
- 但缺少 audience variant 机制

### P1-2 图表和表格返工重

- 文本可以重写
- 图表和表格更难重构

### P1-3 多人协作难控

- deck 是资产，不是一次性交付物
- 缺少差异追踪和变更解释

## Product Requirements

## Must Have

1. 导入 PPTX 并解析为内部 scene graph
2. 导出为可继续编辑的 PPTX
3. 元素级手工编辑
4. deck / slide / selection 三层 AI 编辑
5. 主题继承与局部 override
6. 版本对比和回退

## Should Have

1. 从旧 deck 自动抽品牌 token
2. 讲稿 / 备注管理
3. audience variant generation
4. 表格 / 图表数据绑定

## Nice to Have

1. 实时多人协作
2. 高级动画
3. 语音演讲辅助

## MVP Decision

MVP 不应一开始做庞大的独立引擎。

### Better MVP

先做成某个大模型生态内的 Skill / 插件化能力层：

1. 接用户自然语言指令
2. 在宿主编辑环境中执行排版动作
3. 截图渲染结果
4. 用 VLM 自检“有没有画对 / 有没有对齐 / 有没有溢出”
5. 自动重试或提示修正

## Why This MVP Is Strong

1. 能最快验证“视觉闭环纠错”是否真提升质量
2. 不必先自建完整 editor engine
3. 可以先验证真实用户是否愿意把“精修动作”交给 AI
4. 可以用最少工程量测试 selection-level editing 的价值

## Success Metrics for MVP

1. 10 个常见排版任务成功率
2. 首次动作成功率
3. 经过视觉闭环后二次成功率
4. 平均修正轮数
5. 用户主观满意度
6. 导出的可继续编辑程度

## Working Hypothesis

如果视觉闭环能显著提升：

- 对齐正确率
- 溢出修正率
- 样式一致性

那就说明这个产品的核心价值不在“生成”，而在“看懂结果并自己修正”。
