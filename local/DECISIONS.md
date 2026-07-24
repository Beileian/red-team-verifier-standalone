# red-team-verifier/local — Decision History

> Format: SkillHone 决策四元组 (诊断, 修订, 证据, 结果)
> 本 skill 是 output-integrity-gate 的执行层，与主 skill 联动。

---

## [v1.1.0] 2026-06-29

- **Trigger**: output-integrity-gate 升级到 v1.3.0 分级触发机制
- **Diagnosis**: 
  1. 原设计对所有输出无差别唤起审查，token开销大
  2. 需要与 gate 的分级(P0/P1/P2)对应，只对P0阻塞级输出启动完整审查
- **Chosen**: 新增分级模型 — P0阻塞(完整审查)/P1异步(轻量审查)/P2跳过
- **Evidence**: 与 output-integrity-gate v1.3.0 联动测试通过
- **Outcome**: ✅ accepted

---

## [v1.0.0] 2026-06-28

- **Trigger**: 建立三层防御体系（output-integrity-gate + red-team-verifier + serenity-router）
- **Diagnosis**: 单独的自检清单(prompt级)无法发现跨实体数字串扰（如36元从招行跑到万华），需要独立子代理无上下文审查
- **Design**: 从 Agile-V 代码验证代理适配为通用输出验证
- **Outcome**: ✅ accepted

---

## Design Principles

1. **独立上下文** — 审查时不共享主进程上下文，才能发现主进程未察觉的幻觉
2. **分级联动** — 不自行决定审查范围，由 output-integrity-gate 传递风险等级
3. **证据优先** — 猎杀清单（FT-CODE分类）基于实测幻觉模式，非理论推演
