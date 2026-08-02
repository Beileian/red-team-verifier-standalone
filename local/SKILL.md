---
name: red-team-verifier-local
description: 隐序定制层 — 将 Agile-V 的代码验证代理适配为通用输出验证。幻觉猎杀清单 + FT-CODE 分类 + 分级触发 (P0阻塞/P1异步/P2跳过)，与 output-integrity-gate v1.3.0 联动。
version: "1.2.1"
---

# Red Team Verifier — 隐序适配层

## 适用范围扩展

上游 red-team-verifier 定位为代码验证代理（验证 Build Agent 产出物是否匹配 REQ）。
本适配层将其扩展为**通用输出验证**：任何含数字/事实断言的分析输出，均可被 Red Team 独立审查。

## 核心原则（继承上游，扩展适用域）

**"You do not verify your own work."** — 同一模型分析万华化学，同一模型检查万华化学的输出 → 自检盲区。Red Team 作为**独立角色**介入，不共享分析上下文。

## 分级触发模型（v1.1.0）

由 output-integrity-gate v1.3.0 判定风险等级后通过 delegate_task 唤起：

| 级别 | 唤醒条件 | 阻塞? | 子代理行为 |
|------|---------|:---:|------|
| **P0** | 含交易建议/财务数字断言 | **阻塞** | 完整验证（7项FT-CODE），返回问题列表。主进程等结果，CRITICAL/MAJOR不交付 |
| **P1** | 事实判断无交易建议 + gate自检<7分 | 异步 | 完整验证，结果后台返回。主进程先交付 |
| **P2** | 纯代码/文档/行政操作 | 不唤醒 | — |

### 子代理接收的上下文格式

主进程通过 delegate_task 传递：

```
goal="独立验证以下分析输出"
context="
[风险等级: P0/P1]
--- 分析输出 ---
[完整的markdown分析全文]
--- 数据源 ---
as-of: [行情日期]
来源: [同花顺/券商研报/web_search]
涉及实体: [股票代码列表]
--- 要求 ---
逐条检查7项FT-CODE，标记所有发现。
P0阻塞：返回CRITICAL/MAJOR时精确指出错误位置+修正建议。
"
skills=["red-team-verifier"]
```

触发方式：
- 主进程完成分析输出后 → 以子代理 (delegate_task) 身份加载本 skill
- 子代理仅接收分析输出文本 + 上游数据源引用 → 不依赖主进程上下文
- 子代理独立验证 → 返回发现的问题列表

## 通用幻觉猎杀清单（继承上游 §Hallucination Hunting，扩展适用域）

| 上游原始 | 本层适配 |
|------|------|
| feature not in any REQ | **断言在当前对话中无来源**（数字/事实/引用无法追溯到工具调用或用户输入） |
| logic not traceable | **推理链断裂**（结论跳过了中间步骤，或前文数据推不出后文结论） |
| constraint not in Gatekeeper output | **数字超出已知区间**（股价 < 52周低点 / 增长率 > 500% / 市值偏离行业范围一个数量级） |
| unspecified dependencies | **跨实体数字串扰**（数字 A 来自股票 X，却出现在股票 Y 的分析中） |

### 检查流程（每次验证执行）

```
1. 逐条提取分析输出中的所有量化断言（数字/百分比/日期/名称）
2. 对每条断言，回溯：该数字从哪个工具调用/搜索/用户输入来的？
3. 标记：有来源 / 推断（标注"[推断]"）/ 无来源（标记为潜在幻觉）
4. 交叉对比：同一输出内同一指标的不同出现，数值是否一致？
5. 范围检查：每个数值是否在已知的合理区间内？
6. 跨实体检查：如果对话涉及多个实体，每个数字是否归属正确的实体？
```

## 错误分类体系（FT-CODE，继承上游 §Failure Taxonomy，扩展适用域）

| FT-CODE | 上游原始含义 | 本层适配 |
|------|------|------|
| `FT-DATA` | —（新增） | 数据错误：数字本身不对（行情过期/财报列读错/单位混淆） |
| `FT-SOURCE` | —（新增） | 来源缺失：断言无工具调用/搜索/用户输入支撑 |
| `FT-CROSS` | —（新增） | 跨实体串扰：数字属于另一实体（如招行36元→万华分析） |
| `FT-RANGE` | —（新增） | 范围异常：数字超出合理区间（如股价 < 52周低点） |
| `FT-LOGIC` | FT-MISP (wrong read of output) | 推理错误：前文数据推不出该结论 |
| `FT-CONTR` | —（新增） | 内部矛盾：同一指标两处数值不一致 |
| `FT-FORMAT` | FT-PLAN (process deviation) | 格式缺失：as-of标签缺失 / 来源类型未标注 |

## 严重性分级（继承上游 §Severity & Disposition，扩展适用域）

| 严重性 | FT-CODE 映射 | 处置 |
|------|------|------|
| **CRITICAL** | FT-DATA / FT-CROSS / FT-CONTR | **硬拦截** — 修正后重新输出，不交付错误版本 |
| **MAJOR** | FT-SOURCE / FT-RANGE / FT-LOGIC | **Rework** — 补充来源或修正推理链 |
| **MINOR** | FT-FORMAT | **标注后放行** — 补充 as-of / 来源标注后交付 |

## 与 output-integrity-gate 的关系

```
output-integrity-gate v1.3.0  = 自检清单（主进程输出前自查，7项，~30秒）
                                  + 风险分级（P0/P1/P2）
                                  + P0→阻塞唤子代理，P1→条件异步唤

red-team-verifier v1.1.0       = 独立审查（子代理独立验证，7项 FT-CODE）
                                  ↑
                             不共享上下文
                             不看分析过程，只看最终输出
                             按分级触发——P0阻塞/P1异步/P2跳过
```

两者互补：
- gate 抓显性错误（数字范围/标注缺失/实体绑定/ID截断）+ 判定风险等级
- verifier 抓隐性错误（推理断裂/内部矛盾/跨实体串扰）
- gate 是快餐（输出前30秒自检），verifier 是体检（独立子代理跑完整验证）
- **P0阻塞是硬防线**：含交易建议的输出不经过子代理审查不交付

## 已知捕捉案例

| 日期 | 错误 | gate 拦？ | verifier 拦？ | FT-CODE |
|------|------|:---:|:---:|------|
| 2026-06-28 | 万华化学建议36元买入 | ✅ 第1/4项 | ✅ 第4条检查 | FT-CROSS |
| 2026-06-28 | 农行持有成本4.26→6.26 | ✅ 第3项 | ✅ 第2条检查 | FT-SOURCE |
| 2026-06-27 | 中国长城股价30天前 | ✅ 第2项 | ✅ 第5条检查 | FT-DATA |
| 2026-06-27 | 营收102→158亿 | ✅ 第2项 | ✅ 第6条检查 | FT-DATA + FT-CONTR |


---

## 🆕 执行层闸门（v1.2.0 · 2026-08-02 BTC 治理缺口注入）

> 来源：BTC 虚拟量化系统 4连亏期间越闸 BUY 事故——报告层纪律「4连亏下不追加」
> 连续 10 天标注 P0 但从未被执行，因为纪律只写在 LLM 报告里。

**核心教训：报告层建议 ≠ 执行层闸门。**

任何「X 情况下禁止 Y 操作」的纪律，必须写成执行引擎里的硬条件
（if 判断/降权逻辑），不能只写在 cron prompt 或 LLM 报告里。
LLM 建议可被忽略，脚本条件不会。

### 分级触发的执行层实现

本 skill 的 P0 阻塞机制（「主进程等结果，CRITICAL/MAJOR 不交付」）**依赖调用方
脚本实际 await 子代理结果**——如果调用方只是发起 delegate_task 后不检查返回值，
P0 阻塞就是纸面承诺。

**修复模板**（调用方脚本中的硬条件）：

```python
def _apply_review_gate(state, signal):
    """4连亏下 BUY 降权 HOLD——执行层硬闸门，不依赖 LLM 自觉"""
    health = compute_strategy_health(state)
    losing = health.get("consecutive_losing_weeks", 0)
    if losing >= 4 and signal["signal"] == "buy":
        gated = dict(signal)
        gated["signal"] = "hold"
        gated["review_gate"] = {
            "applied": True,
            "consecutive_losing_weeks": losing,
            "original_signal": "buy",
            "original_score": signal["score"],
        }
        return gated, True
    return signal, False
```

**验证**：单元测试三例（4连亏拦截 / HOLD 放行 / 健康放行）全过后才可交付。

---

## 🆕 审查 agent 工具权限最小化（v1.2.0 · 2026-08-02 注入）

**核心原则：审查类 agent 不应拥有修改被审查对象的能力。**

跑偏的审查 cron 会话可能利用全权限工具集违规写入 skill references
（2026-08-02 机器人ETF宏观跑偏实例：会话内 skill_manage 修改了
multi-model-review 的 references，来源标注为伪造）。

### 推荐工具集

| 角色 | enabled_toolsets | 理由 |
|------|------|------|
| 审查者（红队/反共识/宏观） | `["terminal", "file", "web"]` | 读数据/搜索/验证，不需要 skill_manage/patch/write_file |
| 合成器 | `["terminal", "file", "web"]` | 读上游输出 + 生成报告，不需要修改 skill |
| Refute Pass | `["terminal", "file"]` | 读上游 + 推理，不需要 web 搜索 |

### 检查方法

```python
# 审计所有审查 cron 的工具集是否含越权工具
for j in jobs:
    if any(k in j.name for k in ["红队", "反共识", "宏观", "Refute", "合成"]):
        tools = j.enabled_toolsets or ["(全部)"]
        assert tools != ["(全部)"], f"{j.name} 全权限——需收敛"
        assert not set(tools) & {"skills"}, f"{j.name} 含 skill 管理权限"
```

**红线**：skill_manage / patch / write_file 不得出现在审查类 cron 的工具集中。

## 输出审计链（v1.2.1 新增，2026-08-02 蜂群蓝红蓝 P0-2）

每次完成一轮验证（P0/P1）后，**必须**调用 `scripts/verifier_audit.py` 追加一条审计记录：

```bash
python3 /root/.openclaw/workspace/scripts/verifier_audit.py --output "<被验证输出标识>" --level P0 --verdict CRITICAL|MAJOR|MINOR|CLEAN --findings "<发现摘要>"
```

- 审计记录写入 `logs/verifier/audit_YYYYMMDD.jsonl`（追加，不覆盖）
- 目的：让「每输出 → 每验证」可追溯，验证本身也可被审计（验证器也需要被验证）
- 无审计记录 = 本轮验证未完成，视为未交付
