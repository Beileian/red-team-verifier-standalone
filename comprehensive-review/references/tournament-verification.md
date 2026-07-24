# 竞标赛验证模式 (Tournament Verification)

> P2 可选增强 — 用于 P0 级别输出（含交易建议）时提高置信度

## 来源

ClaudeDevs "Getting started with loops" — Proactive Loop 的复合示例：

> "When fixing a bug, use a workflow to explore three solutions in parallel worktrees and have a judge adversarially review them."

## 隐序适配

```
                     ┌─ 子代理 A（deepseek-v4-flash）─┐
P0 分析输出 ─────────┼─ 子代理 B（deepseek-v4-flash）─┼─→ 裁判代理 → 最优方案
                     └─ 子代理 C（deepseek-v4-flash）─┘   (deepseek-v4-pro)
```

## 触发条件

- P0 级别输出（含交易建议/具体价位）
- 用户显式要求「竞标赛验证」
- 关键决策场景（首次建仓/大仓位调整）

**不触发**：P1/P2 输出、日报、BTC 常规报告

## 执行方式

```python
delegate_task(tasks=[
  {
    "goal": "独立分析[标的]，给出完整交易建议",
    "context": "[标的]+[数据源]+[时间框架]",
    "toolsets": ["terminal","web","file"]
  },
  {
    "goal": "独立分析[标的]，给出完整交易建议（独立视角）",
    "context": "[标的]+[数据源]+[时间框架]",
    "toolsets": ["terminal","web","file"]
  },
  {
    "goal": "独立分析[标的]，给出完整交易建议（反向思维视角）",
    "context": "[标的]+[数据源]+[时间框架]",
    "toolsets": ["terminal","web","file"]
  }
])

# 三个子代理并行产出 → 裁判代理评审 → 选最优或综合
```

## 裁判标准

| 维度 | 权重 | 评估 |
|------|:--:|------|
| 数据准确性 | 30% | 数字来源可追溯、无虚构 |
| 推理严谨性 | 25% | 因果链清晰、结论有据 |
| 反共识覆盖 | 20% | 是否考虑了相反观点 |
| 可执行性 | 15% | 止损/目标/仓位具体明确 |
| 简洁度 | 10% | 无冗余、聚焦关键判断 |

## 成本

3 × delegate_task（~1500-3000 token/个）+ 1 × 裁判评审（~2000 token）
≈ 总计 ~8000 token → deepseek-v4-flash 约 ¥0.01/次

## 使用记录

| 日期 | 标的 | 结果 | 备注 |
|------|------|------|------|
| — | — | — | 待首次使用 |
