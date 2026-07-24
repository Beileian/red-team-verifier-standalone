# Comprehensive Review — 决策历史

> 新决策按 ADR 格式记录，格式规范见 `engineering-patterns/references/adr-format.md`

### ADR-002: 容器匹配检查——分析评审与执行计划的断层修复

**背景**：gate.cat 全面评审的分析结论正确（参考保留，分层萃取），但执行计划中 Layer 1 → MEMORY 是默认模板——该记录含"设计思想有萃取价值"等评估结论，不适合入 MEMORY。用户两次纠正。

**决策**：comprehensive-review v1.18.0 新增 §执行计划容器匹配检查。

**关联改动**：borg-collective v1.15.0→v1.16.0（Layer 1 模板修正），comprehensive-review v1.17.1→v1.18.0

### ADR-003: 对话场景三路审查格式规则——区分真实正交与模拟审查

**背景**：2026-07-14 机器人ETF午间分析以"三路审查"格式输出，正文含🔴红队/🔄反共识/🌐宏观映射三段，但底部标注"本分析未经红队独立审查"——用户立即指出自相矛盾。

**决策**：comprehensive-review v1.20.0 新增格式规则：真实三路并行标注 ✅，单模型模拟标注 ⚠️，禁止在模拟审查底部标注"未经审查"。

### ADR-004: 2026-07-15 蒸馏cron评审——"建议而非执行"是安全闸门

**背景**：EarlETF 蒸馏 cron 全面评审发现 agent "建议蒸馏但不执行"→ 初判 P0 bug → 用户指出违反 skill 自进化红线。

**决策**：回退自动执行方案，保留提案确认机制。全面评审蓝队建设阶段追加规则：发现"建议而非执行"时，先对照 persona §操作红线——可能不是 bug 而是安全闸门。

**关联改动**：三个蒸馏 cron prompt 回退 auto-execute 段，保留对照验证+跳过可见性改进。

**原因**：模拟红队≠独立审查员。同模型角色扮演无法替代不同模型+独立上下文的认知正交性。格式自相矛盾比审查不足更损害信任。

**修改文件**：comprehensive-review v1.18.0→v1.20.0

### ADR-001: ADR 格式引入——统一工程决策的记录标准

**背景**：系统有三个 DECISIONS.md 格式各不统一。agent-sphere 的全面评审触发 ADR 格式萃取。

**决策**：从 agent-sphere 萃取 ADR 格式模板 → `engineering-patterns/references/adr-format.md`。新决策按 ADR 格式写；历史决策不强制迁移。

**关联改动**：三个 DECISIONS.md 各追加 ADR 格式示范条目

## [1.10.0] 2026-07-04

- **Trigger**: 本场两次全面评审（起涨点蒸馏 4.4/10 + 顾王琴三启发 5.5/10）均驱动了系统改动
- **Chosen**: 建立 P0/P1/P2 分层落地标准
- **Outcome**: P0 时间框架声明立即落地，P1 持有周期匹配经确认后落地

## [1.9.0] 2026-07-04

- **Trigger**: 衍复投资顾王琴访谈分析→三启发→全面评审 5.5/10 🟡 B
- **Chosen**: P0 时间框架声明 / P1 资产配置建议 / P2 疲劳度低碳注入
- **Outcome**: P0 已落地（three-in-one-analysis v2.2.0）

## [1.8.0] 2026-07-04

- **Trigger**: 《买在起涨点》书籍蒸馏评审 4.4/10 🟠 C
- **Chosen**: 建 `references/book-distillation-pitfalls.md` / 蒸馏前强制框架重叠分析 / 不入库不建skill
- **Outcome**: 蒸馏降级为轻量对照清单

## [1.3.0] 2026-07-03

- **Trigger**: 英伟达"算力贷"溯源翻车
- **Chosen**: 新增财经溯源时间窗口门禁——Step 0 强制锁定 ±72h 官方一手源
- **Outcome**: ✅ accepted
