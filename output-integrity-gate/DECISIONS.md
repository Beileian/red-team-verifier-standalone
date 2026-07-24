# output-integrity-gate — Decision History

> Format: SkillHone 决策四元组 (诊断, 修订, 证据, 结果)

---

## [v1.3.0] 2026-06-29

- **Trigger**: 用户反馈"门禁必须覆盖rubrics全7维度，不只是数据安全2.5/7"，且不能只限股票分析
- **Diagnosis**: 
  1. 原门禁(P0)对所有输出无差别唤起子代理审查，token开销大
  2. 缺少风险分级 — 简单查询和高风险输出同等对待
- **Alternatives**:
  - (A) 全量异步巡检 — 每次输出后异步调用子代理
  - (B) 分级触发 — P0阻塞(高危数字断言)/P1异步(中度风险)/P2跳过(低风险)
  - (C) 纯prompt自检 — 不加子代理，仅在prompt中加检查项
- **Chosen**: (B) — 改动小、成本低、直接封堵高危漏洞
- **Evidence**: 与 red-team-verifier/local v1.1.0 联动测试通过
- **Outcome**: ✅ accepted

---

## [v1.1.0] 2026-06-28

- **Trigger**: 发现门禁只检查了数据安全维度(Rubrics ⑦)，但其他6个维度（事实正确性、覆盖度、推理严谨性等）未覆盖
- **Diagnosis**: 门禁设计时仅关注了"数据不泄露"场景，忽略了"数据被错误归属"这种更隐蔽的幻觉
- **Outcome**: ✅ accepted

---

## Design Principles

1. **分级优于全量** — 不是所有输出都需要子代理审查，按风险分级节省成本
2. **子代理独立验证 > prompt级补丁** — 自检清单不能替代独立审查
3. **与 red-team-verifier 联动** — 本 skill 负责分级判定，verifier 负责执行审查
