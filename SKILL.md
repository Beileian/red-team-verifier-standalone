---
name: red-team-verifier
description: 独立输出验证代理。以子代理身份加载，不共享主进程上下文，独立审查分析输出中的幻觉和错误。触发条件：与 output-integrity-gate v1.3.0 联动 — 按风险等级分级触发（P0阻塞/P1异步/P2跳过），由 gate 判定后通过 delegate_task 唤起。改编自 Agile-V 的代码验证代理（CC BY-SA 4.0）。
version: "1.1.0"
x-borg:
  assimilated: true
  method: manual
  type: overlay
  source: https://github.com/Agile-V/agile_v_skills
  upstream_version: "1.4"
  date: 2026-06-28
category: dogfood
auto_load: false
triggers:
  - output-integrity-gate 联动触发
  - 任何分析输出完成后的独立验证
---

# Red Team Verifier — 输出独立验证

> 改编自 Agile-V red-team-verifier v1.4（CC BY-SA 4.0），扩展适用域：代码验证 → 通用输出验证。

## 加载方式

不自动加载（`auto_load: false`）。由 output-integrity-gate 或 serenity-router 在分析完成后以**子代理**身份加载：

```
delegate_task(
  goal="独立验证分析输出",
  context="[分析输出全文] + [上游数据源引用]",
  skills=["red-team-verifier"]
)
```

子代理**不共享主进程上下文** — 仅接收分析输出文本和数据源引用，独立执行验证。

## 内容结构

本 skill 为 Overlay 结构：

| 层 | 路径 | 内容 |
|------|------|------|
| 上游原版 | `base/SKILL.md` | Agile-V v1.4 代码验证代理 |
| 隐序适配 | `local/SKILL.md` | 通用输出验证 + 分级触发 P0/P1/P2 |
| 动态规则 | `references/redteam_rules.json` | 自进化规则库 — 每次发现新模式自动追加（7条当前规则）

加载时先读上游原则，再读本地适配，最后加载动态规则合并检测。
