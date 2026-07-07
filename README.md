# Red Team Verifier — 通用输出验证代理

> 改编自 [Agile-V red-team-verifier v1.4](https://github.com/Agile-V/agile_v_skills)（CC BY-SA 4.0），由隐序（Yinxu）从「代码验证代理」适配为「通用输出验证代理」。

## 这是什么

一个 **Red Team 独立验证 agent skill**，用于审查 LLM 分析输出中的幻觉、事实错误、跨实体数字串扰和推理断裂。

它作为独立子代理运行——**不共享主进程上下文**，仅接收分析输出文本和数据源引用，独立执行验证。

## 与原始 Agile-V 的区别

| | Agile-V 原版 | 隐序适配版 |
|---|---|---|
| 适用域 | 代码验证（Build Agent 产物 vs REQ） | 通用输出验证（股票分析/日报/BTC/任何含数字断言的分析） |
| FT-CODE | 4 个（FT-PLAN/TOOL/MISP/SYS） | 7 个（新增 FT-DATA/SOURCE/CROSS/RANGE/CONTR/FORMAT） |
| 触发方式 | 手动 | 分级触发：P0 阻塞 / P1 异步 / P2 跳过 |
| 规则库 | 静态 checklist | 动态 `redteam_rules.json`，每次发现新模式自动追加 |
| 与 gate 联动 | 无 | 与 `output-integrity-gate` 联动——gate 判定风险等级后由 gate 唤起 |

## 结构

```
├── SKILL.md                    # 顶层 overlay —— 加载时先读上游原则，再读本地适配
├── base/SKILL.md               # Agile-V v1.4 原版（代码验证代理）
├── local/SKILL.md              # 隐序适配层 —— 通用输出验证
├── local/DECISIONS.md          # 决策历史
├── references/redteam_rules.json  # 自进化规则库（7 条当前规则）
├── meta.json                   # 上游元数据 + 本地适配说明
└── README.md
```

## 核心原则

**"You do not verify your own work."** — 同一模型不能同时做分析和审查。Red Team 作为**独立子代理**介入，不共享分析上下文。

## 分级触发

| 级别 | 触发条件 | 行为 |
|------|---------|------|
| **P0** | 含交易建议/财务数字断言 | 阻塞——完整验证，CRITICAL/MAJOR 不交付 |
| **P1** | 事实判断但无交易建议 | 异步——完整验证，结果后台返回 |
| **P2** | 纯代码/文档/行政操作 | 不唤醒 |

## 许可

- 上游 Agile-V red-team-verifier：**CC BY-SA 4.0** → https://github.com/Agile-V/agile_v_skills
- 借鉴 Get Shit Done (GSD)：**MIT** → https://github.com/gsd-build/get-shit-done
- 隐序适配层：**CC BY-SA 4.0**（继承上游）

## 安装方式

将此仓库克隆到你的 AI agent skills 目录，按你的 agent 框架（如 Hermes、OpenClaw/Grace、Claude Code）的 skill 加载机制引入即可。

```
git clone https://github.com/Beileian/red-team-verifier-standalone.git
```
