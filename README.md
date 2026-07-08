# 隐序输出验证三件套 (Yinxu Output Verification Toolkit)

> 三个协同工作的 AI agent skill，构成分析输出的完整防御体系——从自检门禁、到独立红队审查、到统一评审框架。

## 三层架构

```
分析输出
  │
  ├── ① output-integrity-gate（自检门禁）
  │     输出前 30 秒自检：数字-实体绑定 / 范围合理性 / 断言可追溯
  │     风险分级 P0/P1/P2 → 决定是否唤醒红队子代理
  │
  ├── ② red-team-verifier（独立红队审查）
  │     子代理独立上下文，不共享主进程记忆
  │     P0 阻塞 / P1 异步 / P2 跳过
  │     7 项 FT-CODE 分类 + 自进化规则库
  │
  └── ③ comprehensive-review（统一评审框架）
        串联 Rubrics 量化评分 + 红蓝对抗
        输出：评分表 → 红队批判 → 蓝队建设 → 整合结论
```

## 各 Skill 说明

### ① output-integrity-gate（自检门禁）

**来源**：隐序原创（基于实测幻觉模式）

通用幻觉拦截器。任何含数字/事实断言的输出，自动执行 7 项自检（v1.6.0 已扩展至 14 项）。按风险等级（P0/P1/P2）决定是否唤起 red-team-verifier 子代理。

### ② red-team-verifier（独立红队审查）

**来源**：改编自 [Agile-V red-team-verifier v1.4](https://github.com/Agile-V/agile_v_skills)（CC BY-SA 4.0）

从「代码验证代理」适配为「通用输出验证代理」。独立子代理运行，不共享主进程上下文。7 项 FT-CODE 分类 + 自进化动态规则库 `redteam_rules.json`。

> ⚠️ **重要**：Red Team Protocol 规定红队只批判不给修复建议。蓝队建设部分由 `comprehensive-review` 提供。

### ③ comprehensive-review（统一评审框架）

**来源**：隐序原创（整合 Rubrics 评分 + 红蓝对抗）

串联 Rubrics 量化评分 + 红队独立批判 + 蓝队建设建议。输出完整四段结构：评分表→红队批判→蓝队建设→可信度评级。

## 安装方式

```bash
git clone https://github.com/Beileian/red-team-verifier-standalone.git
```

按你的 agent 框架（Hermes、OpenClaw/Grace、Claude Code）的 skill 加载机制引入。

**最小安装**：`red-team-verifier` 可独立运行。
**完整防御**：建议三个 skill 全部加载，按 `output-integrity-gate → red-team-verifier → comprehensive-review` 链路协同。

## 许可

| 组件 | 许可 | 来源 |
|------|------|------|
| output-integrity-gate | CC BY-SA 4.0 | 隐序原创 |
| red-team-verifier (base) | CC BY-SA 4.0 | [Agile-V/agile_v_skills](https://github.com/Agile-V/agile_v_skills) |
| red-team-verifier (local) | CC BY-SA 4.0 | 隐序适配（继承上游） |
| comprehensive-review | CC BY-SA 4.0 | 隐序原创 |
