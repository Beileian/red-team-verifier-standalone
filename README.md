# Red Team Verifier Standalone

**通用输出验证代理** — 改编自 [Agile-V](https://agile-v.org/) red-team-verifier v1.4（CC BY-SA 4.0），由隐序（Yinxu）适配为通用输出幻觉审查体系。

一套四层的输出防御架构，用于拦截 LLM 幻觉、数字错误、跨实体串扰和推理缺陷。

## 四层架构

```
┌─────────────────────────────────────────────────────┐
│ ① base/                     Agile-V 验证代理原版      │
│    (red-team-verifier v1.4)  代码/固件/原理图验证      │
├─────────────────────────────────────────────────────┤
│ ② local/                    隐序适配层 v1.1.0         │
│    (red-team-verifier-local) 通用输出验证 + 分级触发   │
│    P0阻塞 / P1异步 / P2跳过                           │
├─────────────────────────────────────────────────────┤
│ ③ output-integrity-gate/    输出完整性门禁 v1.18.0    │
│    主进程输出前 30 秒自检（7 项）+ 风险分级            │
├─────────────────────────────────────────────────────┤
│ ④ comprehensive-review/     全面评审框架 v1.35.0      │
│    Rubrics 八维评分 + 红蓝互辩 + 决策三角 + 理解债闸门  │
└─────────────────────────────────────────────────────┘
```

## 各层职责

| 层 | 定位 | 触发方式 | 核心能力 |
|:--:|------|------|------|
| ① base | 验证代理原版 | 代码/固件/原理图验证 | FT-CODE 故障分类、Eval Gate、多周期验证 |
| ② local | 通用输出验证适配 | gate 分级判定后 delegate_task 唤起 | 幻觉猎杀清单、FT-CODE 扩展、跨实体检查 |
| ③ gate | 输出前自检 | 任何含数字/事实的输出 | 7 项自检、风险分级（P0/P1/P2）、P0 阻塞唤子代理 |
| ④ comprehensive-review | 全面评审 | 「全面评审」「Rubrics+红蓝」触发词 | Rubrics 八维、红蓝互辩、决策三角、理解债闸门 |

## 安装

将对应 skill 目录复制到你的 agent 的 skills 目录：

```bash
# 通用输出验证（推荐组合：base + local + gate）
cp -r base ~/.hermes/skills/dogfood/red-team-verifier/
cp -r local ~/.hermes/skills/dogfood/red-team-verifier/local/
cp -r output-integrity-gate ~/.hermes/skills/dogfood/output-integrity-gate/

# 全面评审（可选，用于报告/方案的深度评审）
cp -r comprehensive-review ~/.hermes/skills/dogfood/comprehensive-review/
```

## 发布完整性检查

本仓库所有 SKILL.md 中引用的 `references/` 文件已完整发布。修改后推送前请运行：

```bash
python3 verify_release.py        # 检查引用完整性（exit 0=通过）
python3 verify_release.py --json # CI 友好输出
```

## 许可证

- `base/` — Agile-V red-team-verifier v1.4，[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，含 GSD（MIT）部分
- `local/`、`output-integrity-gate/`、`comprehensive-review/` — 隐序适配层，CC BY-SA 4.0

## 与上游的关系

| 文件 | 来源 | 说明 |
|------|------|------|
| `base/SKILL.md` | Agile-V v1.4 | 原版未改动 |
| `local/SKILL.md` | 隐序适配 | 扩展适用域为通用输出验证 |
| `comprehensive-review/SKILL.md` | 隐序原创 | 独立评审框架 |
| `output-integrity-gate/SKILL.md` | 隐序原创 | 输出前自检门禁 |

## 版本历史

- **v1.3.0 (2026-08-02)** — references 完整发布修复；三件套同步至 comprehensive-review v1.35.0 / gate v1.18.0；新增多路合成实操经验（内容类型校验/角色约束/Refute 层/执行层闸门/工具权限最小化）
- **v1.2.0 (2026-07-25)** — 精简推送（references 未发布，存在悬空引用——v1.3.0 已修复）
